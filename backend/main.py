from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import base64
import re
import time
from typing import List, Optional
import json
from dotenv import load_dotenv
import PyPDF2
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from PIL import Image

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

def retry_with_backoff(func, max_retries=5, initial_delay=3):
    """Retry function with exponential backoff for API overload and network errors"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e).lower()
            # Check for retryable errors
            is_retryable = any([
                "503" in error_str,
                "unavailable" in error_str,
                "overloaded" in error_str,
                "winerror 10053" in error_str,  # Connection aborted
                "getaddrinfo failed" in error_str,  # DNS/network error
                "connection" in error_str,
                "timeout" in error_str,
                "network" in error_str
            ])
            
            if is_retryable and attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)
                print(f"Network/API error: {str(e)[:100]}")
                print(f"Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
                continue
            
            # If not retryable or max retries reached, raise the error
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
            # Get the chapter title from the match, or extract from first line of text
            chapter_title = match.group(2) if match.group(2) else ""
            
            start_pos = match.end()
            end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            chapter_text = text[start_pos:end_pos].strip()
            
            # If no title in pattern, try to extract from first line
            if not chapter_title and chapter_text:
                first_line = chapter_text.split('\n')[0].strip()
                if len(first_line) < 100:  # Likely a title if short
                    chapter_title = first_line
                    # Remove title from text
                    chapter_text = '\n'.join(chapter_text.split('\n')[1:]).strip()
            
            if not chapter_title:
                chapter_title = f"Chapter {chapter_num}"
            
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

def generate_chapter_title(chapter_text: str, chapter_number: int) -> str:
    """Generate a meaningful, concise chapter title based on content using AI"""
    prompt = f"""
Generate a concise, meaningful chapter title for this text.

Requirements:
- 2-3 words maximum
- NO verbs (use nouns and adjectives only)
- Capitalize each word (Title Case)
- Should capture the essence/theme of the chapter
- Examples of good titles: "The Time Traveller", "Strange Discovery", "Dark Forest", "Lost Kingdom"
- Return ONLY the title, no quotes, no extra text

Chapter text:
{chapter_text[:1000]}

Title:
"""
    
    try:
        def call_api():
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            result = response.text.strip()
            # Remove quotes if present
            result = result.replace('"', '').replace("'", "")
            return result
        
        title = retry_with_backoff(call_api)
        # Ensure it's not too long
        words = title.split()
        if len(words) > 3:
            title = " ".join(words[:3])
        return title
    except Exception as e:
        print(f"Title generation error: {e}")
        return f"Chapter {chapter_number}"

def simplify_for_kids(text: str) -> str:
    """Simplify text for children aged 6-8"""
    prompt = f"""
You are rewriting a story for children aged 6-8 years old.

Rules:
1. Use short sentences and simple words
2. Make it engaging and fun
3. Keep the main story elements
4. Return ONLY the simplified story text
5. Do NOT include any introductory phrases like "Here is the story" or "Simplified version"
6. Start directly with the story

Original text:
{text}

Simplified story:
"""
    
    try:
        def call_api():
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            result = response.text.strip()
            
            # Remove common unwanted prefixes
            unwanted_prefixes = [
                "Here is the story in simple English for children:",
                "Here is the simplified story:",
                "Simplified version:",
                "Here's the story:",
                "Here is the story:",
                "Story:"
            ]
            
            for prefix in unwanted_prefixes:
                if result.startswith(prefix):
                    result = result[len(prefix):].strip()
            
            return result
        
        return retry_with_backoff(call_api)
    except Exception as e:
        print(f"Simplification error: {e}")
        return "Once upon a time, there was a wonderful story..."

def generate_image_prompt(simplified_text: str) -> str:
    """Generate a vivid image prompt from the text"""
    prompt = f"""
Create ONE vivid image prompt for a children's book illustration based on this story.

Requirements:
- Colorful and engaging
- Appropriate for kids aged 6-8
- Describe a specific scene from the story
- Return ONLY the image prompt, no extra text

Story:
{simplified_text}

Image prompt:
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


@app.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...)):
    """Process uploaded PDF with streaming progress updates"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    async def generate():
        try:
            # Read PDF
            pdf_content = await file.read()
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Extracting text from PDF...', 'progress': 5})}\n\n"
            
            full_text = extract_text_from_pdf(pdf_content)
            
            lines = full_text.split('\n')
            book_title = lines[0].strip() if lines else file.filename.replace('.pdf', '')
            
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Splitting into chapters...', 'progress': 10})}\n\n"
            
            raw_chapters = split_into_chapters(full_text)
            total_chapters = len(raw_chapters)
            
            processed_chapters = []
            
            for i, chapter_data in enumerate(raw_chapters):
                chapter_num = chapter_data['number']
                progress = 10 + int((i / total_chapters) * 80)
                
                yield f"data: {json.dumps({'type': 'progress', 'message': f'Processing chapter {i+1} of {total_chapters}...', 'progress': progress})}\n\n"
                
                print(f"Processing Chapter {chapter_num}")
                
                # Generate meaningful title using AI
                chapter_title = generate_chapter_title(chapter_data['text'], chapter_num)
                
                yield f"data: {json.dumps({'type': 'progress', 'message': f'Simplifying chapter {i+1}: {chapter_title}...', 'progress': progress + 5})}\n\n"
                
                # Small delay between API calls
                time.sleep(1)
                
                # Simplify text
                simplified = simplify_for_kids(chapter_data['text'])
                
                # Add delay between chapters to avoid API overload and network issues
                time.sleep(3)
                
                processed_chapters.append(Chapter(
                    chapter_number=chapter_num,
                    title=chapter_title,
                    simplified_text=simplified,
                    image="",  # Empty - will be generated on-demand
                    image_prompt=""
                ))
            
            # Send final result
            result = ProcessedBook(
                title=book_title,
                total_chapters=len(processed_chapters),
                chapters=processed_chapters
            )
            
            yield f"data: {json.dumps({'type': 'complete', 'data': result.model_dump(), 'progress': 100})}\n\n"
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing PDF: {error_msg}")
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

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

@app.post("/download_pdf")
async def download_pdf(book: ProcessedBook):
    """Generate a downloadable PDF with all chapters and images"""
    
    print(f"Generating PDF for: {book.title}")
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1e293b',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    chapter_title_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Heading2'],
        fontSize=18,
        textColor='#334155',
        spaceAfter=20,
        spaceBefore=20
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=12,
        leading=18,
        textColor='#475569'
    )
    
    # Add book title
    story.append(Paragraph(book.title, title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Process each chapter
    for i, chapter in enumerate(book.chapters):
        print(f"Adding Chapter {chapter.chapter_number} to PDF")
        
        # Generate image if not already generated
        if not chapter.image:
            print(f"Generating missing image for Chapter {chapter.chapter_number}")
            try:
                prompt = generate_image_prompt(chapter.simplified_text)
                chapter.image = generate_image(prompt)
                time.sleep(1)  # Small delay to avoid API overload
            except Exception as e:
                print(f"Error generating image for chapter {chapter.chapter_number}: {e}")
        
        # Add chapter title
        story.append(Paragraph(f"Chapter {chapter.chapter_number}: {chapter.title}", chapter_title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Add chapter text
        paragraphs = chapter.simplified_text.split('\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 0.1*inch))
        
        # Add image if available
        if chapter.image:
            try:
                # Decode base64 image
                if chapter.image.startswith('data:image'):
                    image_data = chapter.image.split(',')[1]
                else:
                    image_data = chapter.image
                
                image_bytes = base64.b64decode(image_data)
                img_buffer = io.BytesIO(image_bytes)
                
                # Open with PIL to get dimensions
                pil_img = Image.open(img_buffer)
                img_width, img_height = pil_img.size
                
                # Calculate scaled dimensions (max width 5 inches)
                max_width = 5 * inch
                aspect_ratio = img_height / img_width
                scaled_width = min(max_width, img_width)
                scaled_height = scaled_width * aspect_ratio
                
                # Reset buffer position
                img_buffer.seek(0)
                
                # Add image to PDF
                story.append(Spacer(1, 0.2*inch))
                rl_image = RLImage(img_buffer, width=scaled_width, height=scaled_height)
                story.append(rl_image)
                
            except Exception as e:
                print(f"Error adding image for chapter {chapter.chapter_number}: {e}")
        
        # Add page break between chapters (except last one)
        if i < len(book.chapters) - 1:
            story.append(PageBreak())
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Return as downloadable file
    filename = f"{book.title.replace(' ', '_')}_Kids_Edition.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
