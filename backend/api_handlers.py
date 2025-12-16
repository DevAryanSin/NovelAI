"""API handlers for Gemini AI interactions"""

from google import genai
from google.genai import types
import os
import base64
import time
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing")

client = genai.Client(api_key=api_key)


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
