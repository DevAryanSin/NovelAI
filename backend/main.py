from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import time
import tempfile
import os

# Import from our modular files
from pdf_processor import extract_text_from_pdf, split_into_chapters, generate_pdf_content
from api_handlers import (
    generate_chapter_title,
    simplify_for_kids,
    generate_image_prompt,
    generate_image
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/process_pdf")
async def process_pdf(file: UploadFile = File(...)):
    """Process uploaded PDF with streaming progress updates"""
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    async def generate():
        # Use temporary file to handle large PDFs
        tmp_path = None
        try:
            # Save uploaded file to /tmp directory
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            yield f"data: {json.dumps({'type': 'progress', 'message': 'Extracting text from PDF...', 'progress': 5})}\n\n"
            
            # Extract text from temporary file (reduces memory pressure)
            full_text = extract_text_from_pdf(tmp_path)
            
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
        finally:
            # Clean up temporary file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                    print(f"Cleaned up temporary file: {tmp_path}")
                except Exception as e:
                    print(f"Error cleaning up temporary file: {e}")
    
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
    
    # Generate PDF content using the pdf_processor module
    buffer = generate_pdf_content(book, generate_image_prompt, generate_image)
    
    # Return as downloadable file
    filename = f"{book.title.replace(' ', '_')}_Kids_Edition.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
