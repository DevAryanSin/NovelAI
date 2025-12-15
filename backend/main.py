from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import base64
import re
import time
from typing import List, Optional
from dotenv import load_dotenv
import PyPDF2
import io

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing")

client = genai.Client(api_key=api_key)

class Chapter(BaseModel):
    chapter_number: int
    title: str
    simplified_text: str
    image: Optional[str] = ""
    image_prompt: Optional[str] = ""

class ProcessedBook(BaseModel):
    title: str
    total_chapters: int
    chapters: List[Chapter]

class ImageRequest(BaseModel):
    chapter_number: int
    simplified_text: str

def retry_with_backoff(func, max_retries=3, initial_delay=2):
    """Retry function with exponential backoff for API overload"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e)
            if "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower():
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    print(f"API overloaded, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
            raise e
    raise Exception("Max retries exceeded")

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def split_into_chapters(text: str) -> List[dict]:
    """Split text into chapters using common patterns"""
    chapter_pattern = r'(?:Chapter|CHAPTER|Ch\.|CH\.)\s*(\d+|[IVX]+)(?:\s*[:\-–—]\s*(.+?))?(?=\n|$)'
    
    chapters = []
    matches = list(re.finditer(chapter_pattern, text, re.MULTILINE))
    
    if matches:
        for i, match in enumerate(matches):
            chapter_num = i + 1
            chapter_title = match.group(2) if match.group(2) else f"Chapter {chapter_num}"
            
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chapter_text = text[start_pos:end_pos].strip()
            
            if len(chapter_text) > 3000:
                chapter_text = chapter_text[:3000] + "..."
            
            chapters.append({
                "number": chapter_num,
                "title": chapter_title.strip(),
                "text": chapter_text
            })
    else:
        words = text.split()
        chunk_size = 500
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chapters.append({
                "number": i // chunk_size + 1,
                "title": f"Part {i // chunk_size + 1}",
                "text": chunk
            })
    
    return chapters[:10]

def simplify_for_kids(text: str) -> str:
    """Simplify text for children aged 6-8"""
    prompt = f"""
    Rewrite the following story excerpt in simple English for children aged 6-8 years old.
    Use short sentences, simple words, and make it engaging and fun.
    Keep the main story elements but make it easy to understand.
    
    Original text:
    {text}
    
    Simplified version:
    """
    
    try:
        def call_api():
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        
        return retry_with_backoff(call_api)
    except Exception as e:
        print(f"Simplification error: {e}")
        return "Once upon a time, there was a wonderful story..."

def generate_image_prompt(simplified_text: str) -> str:
    """Generate a vivid image prompt from the text"""
    prompt = f"""
    Based on this children's story, create ONE vivid image prompt for a children's book illustration.
    Make it colorful, engaging, and appropriate for kids.
    
    Story:
    {simplified_text}
    
    Return ONLY the image prompt text.
    """
    
    try:
        def call_api():
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        
        result = retry_with_backoff(call_api)
        return result
    except Exception as e:
        print(f"Prompt generation error: {e}")
        return "A colorful children's book illustration"

def generate_image(prompt: str) -> str:
    """Generate image using Gemini"""
    try:
        enhanced_prompt = f"Children's book illustration style, colorful and vibrant: {prompt}"
        
        def call_api():
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=enhanced_prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"]
                )
            )
            return response
        
        response = retry_with_backoff(call_api)
        
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                return "data:image/png;base64," + base64.b64encode(image_bytes).decode()
        
        return ""
    except Exception as e:
        print(f"Image generation error: {e}")
        return ""

@app.post("/process_pdf", response_model=ProcessedBook)
async def process_pdf(file: UploadFile = File(...)):
    """Process uploaded PDF - only simplify text, don't generate images yet"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    pdf_content = await file.read()
    full_text = extract_text_from_pdf(pdf_content)
    
    lines = full_text.split('\n')
    book_title = lines[0].strip() if lines else file.filename.replace('.pdf', '')
    
    raw_chapters = split_into_chapters(full_text)
    
    processed_chapters = []
    
    for chapter_data in raw_chapters:
        print(f"Processing Chapter {chapter_data['number']}: {chapter_data['title']}")
        
        # Only simplify text - don't generate images yet
        simplified = simplify_for_kids(chapter_data['text'])
        
        # Add delay between chapters to avoid API overload
        time.sleep(1.5)
        
        processed_chapters.append(Chapter(
            chapter_number=chapter_data['number'],
            title=chapter_data['title'],
            simplified_text=simplified,
            image="",  # Empty - will be generated on-demand
            image_prompt=""
        ))
    
    return ProcessedBook(
        title=book_title,
        total_chapters=len(processed_chapters),
        chapters=processed_chapters
    )

@app.post("/generate_images")
async def generate_images(request: ImageRequest):
    """Generate images for a specific chapter on-demand"""
    
    print(f"Generating image for Chapter {request.chapter_number}")
    
    # Generate image prompt
    prompt = generate_image_prompt(request.simplified_text)
    
    # Generate image
    image = generate_image(prompt)
    
    return {
        "image": image,
        "image_prompt": prompt
    }
