from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
from google.genai.errors import ServerError
import os
import base64
import re
import asyncio
from typing import List, Optional
import json
from dotenv import load_dotenv
import PyPDF2
import io
import random
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from PIL import Image

# -------------------------------------------------------------------
# INIT
# -------------------------------------------------------------------

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing")

client = genai.Client(api_key=api_key)

# -------------------------------------------------------------------
# GLOBAL LIMITS & CACHES (CRITICAL)
# -------------------------------------------------------------------

TEXT_SEMAPHORE = asyncio.Semaphore(2)      # Gemini Flash
IMAGE_SEMAPHORE = asyncio.Semaphore(1)     # Gemini Image

IMAGE_CACHE: dict[str, str] = {}           # prompt -> base64 image

# -------------------------------------------------------------------
# MODELS
# -------------------------------------------------------------------

class Chapter(BaseModel):
    chapter_number: int
    title: Optional[str] = ""
    raw_text: str  # Original extracted text
    simplified_text: Optional[str] = ""
    image: Optional[str] = ""
    image_prompt: Optional[str] = ""
    simplified: bool = False  # Track if chapter has been processed

class ProcessedBook(BaseModel):
    title: str
    total_chapters: int
    chapters: List[Chapter]

class ImageRequest(BaseModel):
    chapter_number: int
    image_prompt: str

class SimplifyChapterRequest(BaseModel):
    chapter_number: int
    raw_text: str

# -------------------------------------------------------------------
# RETRY LOGIC (NEW)
# -------------------------------------------------------------------

async def retry_with_backoff(func, *args, max_retries=5, initial_delay=1, **kwargs):
    """
    Retries an async function if it raises a ServerError (503).
    Uses exponential backoff with jitter.
    """
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except ServerError as e:
            if attempt == max_retries - 1:
                print(f"Max retries reached. Last error: {e}")
                raise e
            
            # Check if it's a 503 error (Server Error / Overloaded)
            if hasattr(e, 'code') and e.code != 503:
                 raise e

            delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Gemini 503 Error (Overloaded). Retrying in {delay:.2f}s... (Attempt {attempt + 1}/{max_retries})")
            await asyncio.sleep(delay)
    return await func(*args, **kwargs) # Should not be reached

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def extract_text_from_pdf(pdf_file: bytes) -> str:
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def split_into_chapters(text: str) -> List[dict]:
    pattern = r'(?:Chapter|CHAPTER)\s+(\d+)(.*?)(?=Chapter\s+\d+|$)'
    matches = re.findall(pattern, text, re.S)

    chapters = []
    for i, (_, content) in enumerate(matches[:10]):
        chapters.append({
            "number": i + 1,
            "text": content.strip()[:2500]
        })

    if not chapters:
        words = text.split()
        for i in range(0, min(len(words), 5000), 500):
            chapters.append({
                "number": len(chapters) + 1,
                "text": " ".join(words[i:i+500])
            })

    return chapters[:10]

# -------------------------------------------------------------------
# SINGLE AI CALL PER CHAPTER (🔥 BIG FIX)
# -------------------------------------------------------------------

async def process_chapter_ai(text: str) -> dict:
    prompt = f"""
You are creating a children's storybook for kids aged 6 to 8.

Your task:
1. Create a SHORT chapter title
2. Rewrite the chapter in VERY SIMPLE ENGLISH
3. Create ONE image description for an illustration

IMPORTANT RULES:
- Use simple words a child can understand
- Use short sentences (8–12 words max)
- Sound like a bedtime story
- Do NOT explain morals
- Do NOT use difficult words
- Do NOT talk to the reader
- Do NOT mention chapters, summaries, or rewriting
- Start the story directly

TITLE RULES:
- 2 or 3 words only
- NO verbs (only nouns & adjectives)
- Easy words for kids
- Title Case (Example: "Magic Forest", "Lost Puppy")

IMAGE PROMPT RULES:
- Describe ONE clear scene
- Colorful children's book illustration
- Happy, soft, friendly style
- No violence, fear, or darkness

Return ONLY valid JSON in this exact format:

{{
  "title": "Example Title",
  "simplified_text": "Very simple story text here.",
  "image_prompt": "Colorful children's illustration description"
}}

Chapter text:
{text[:2200]}
"""

    async def _call_api():
        async with TEXT_SEMAPHORE:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.6
                )
            )
        return response

    response = await retry_with_backoff(_call_api)
    return json.loads(response.text)


# -------------------------------------------------------------------
# IMAGE GENERATION (CACHED)
# -------------------------------------------------------------------

async def generate_image_cached(prompt: str) -> str:
    if prompt in IMAGE_CACHE:
        return IMAGE_CACHE[prompt]

    async def _call_api():
        async with IMAGE_SEMAPHORE:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=f"Children's book illustration, colorful: {prompt}",
                config=types.GenerateContentConfig(response_modalities=["IMAGE"])
            )
        return response

    response = await retry_with_backoff(_call_api)

    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image = "data:image/png;base64," + base64.b64encode(
                part.inline_data.data
            ).decode()
            IMAGE_CACHE[prompt] = image
            return image

    return ""

# -------------------------------------------------------------------
# API ENDPOINTS
# -------------------------------------------------------------------

@app.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...)):
    """
    Extract chapters from PDF without AI processing.
    This reduces API load by only extracting text structure.
    """
    async def stream():
        pdf_bytes = await file.read()
        yield f"data: {json.dumps({'type': 'progress', 'progress': 10})}\n\n"

        text = extract_text_from_pdf(pdf_bytes)
        title = text.split("\n")[0][:80] or "Kids Book"

        yield f"data: {json.dumps({'type': 'progress', 'progress': 30})}\n\n"

        chapters_raw = split_into_chapters(text)
        chapters: list[Chapter] = []

        # Only extract chapters, NO AI processing
        for i, ch in enumerate(chapters_raw):
            yield f"data: {json.dumps({'type': 'progress', 'message': f'Extracting chapter {i+1}', 'progress': 40 + i * 5})}\n\n"

            chapters.append(Chapter(
                chapter_number=ch["number"],
                title=f"Chapter {ch['number']}",  # Temporary title
                raw_text=ch["text"],  # Store raw text
                simplified_text="",  # Empty until user clicks
                image_prompt="",
                image="",
                simplified=False  # Not yet processed
            ))

        book = ProcessedBook(
            title=title,
            total_chapters=len(chapters),
            chapters=chapters
        )

        yield f"data: {json.dumps({'type': 'complete', 'data': book.model_dump(), 'progress': 100})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")

# -------------------------------------------------------------------

@app.post("/simplify_chapter")
async def simplify_chapter(req: SimplifyChapterRequest):
    """
    Simplify a single chapter on-demand when user clicks it.
    This is called only when needed, reducing API load.
    """
    try:
        # Process the chapter with AI
        ai_result = await process_chapter_ai(req.raw_text)
        
        return {
            "success": True,
            "chapter_number": req.chapter_number,
            "title": ai_result["title"],
            "simplified_text": ai_result["simplified_text"],
            "image_prompt": ai_result["image_prompt"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to simplify chapter: {str(e)}"
        )

# -------------------------------------------------------------------

@app.post("/generate_images")
async def generate_images(req: ImageRequest):
    image = await generate_image_cached(req.image_prompt)
    return {"image": image}

# -------------------------------------------------------------------

@app.post("/download_pdf")
async def download_pdf(book: ProcessedBook):
    """
    Generate PDF with all chapters.
    Simplifies any unsimplified chapters and generates missing images sequentially.
    """
    
    # Step 1: Simplify all unsimplified chapters sequentially
    for i, chapter in enumerate(book.chapters):
        if not chapter.simplified or not chapter.simplified_text:
            print(f"Simplifying chapter {chapter.chapter_number} for PDF...")
            ai_result = await process_chapter_ai(chapter.raw_text)
            
            # Update the chapter with simplified data
            book.chapters[i].title = ai_result["title"]
            book.chapters[i].simplified_text = ai_result["simplified_text"]
            book.chapters[i].image_prompt = ai_result["image_prompt"]
            book.chapters[i].simplified = True
    
    # Step 2: Generate missing images sequentially
    for i, chapter in enumerate(book.chapters):
        if not chapter.image and chapter.image_prompt:
            print(f"Generating image for chapter {chapter.chapter_number}...")
            book.chapters[i].image = await generate_image_cached(chapter.image_prompt)
    
    # Step 3: Build the PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(book.title, styles["Title"]))
    story.append(Spacer(1, 0.4 * inch))

    for chapter in book.chapters:
        story.append(Paragraph(
            f"Chapter {chapter.chapter_number}: {chapter.title}",
            styles["Heading2"]
        ))
        story.append(Spacer(1, 0.2 * inch))

        for para in chapter.simplified_text.split("\n"):
            if para.strip():
                story.append(Paragraph(para, styles["BodyText"]))
                story.append(Spacer(1, 0.1 * inch))

        if chapter.image:
            img_bytes = base64.b64decode(chapter.image.split(",")[1])
            img_buf = io.BytesIO(img_bytes)
            story.append(Spacer(1, 0.2 * inch))
            story.append(RLImage(img_buf, width=4 * inch, height=4 * inch))

        story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={book.title}.pdf"
        }
    )
