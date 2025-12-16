"""PDF processing utilities for text extraction and chapter management"""

import PyPDF2
import io
import re
from typing import List
from fastapi import HTTPException


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


def generate_pdf_content(book, generate_image_prompt_func, generate_image_func):
    """Generate PDF content with chapters and images"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER
    from PIL import Image
    import base64
    import time
    
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
                prompt = generate_image_prompt_func(chapter.simplified_text)
                chapter.image = generate_image_func(prompt)
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
    
    return buffer
