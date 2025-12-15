# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from google import genai
# from google.genai import types
# import os
# import json
# import base64
# import time
# from dotenv import load_dotenv

# load_dotenv()

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ChapterRequest(BaseModel):
#     text: str

# @app.post("/process_chapter")
# async def process_chapter(request: ChapterRequest):
#     # Retrieve Keys
#     key_text_image = os.environ.get("GEMINI_API_KEY_TEXT_IMAGE")
#     key_video = os.environ.get("GEMINI_API_KEY_VIDEO")

#     if not key_text_image or not key_video:
#         raise HTTPException(status_code=500, detail="Missing API Keys in server environment")

#     # 1. Initialize Clients
#     client_ti = genai.Client(api_key=key_text_image)
#     client_v = genai.Client(api_key=key_video)

#     # Helper for Retries
#     def generate_with_retry(client_method, **kwargs):
#         max_retries = 3
#         for attempt in range(max_retries):
#             try:
#                 return client_method(**kwargs)
#             except Exception as e:
#                 # Check for 503 (Unavailable) or 429 (Too Many Requests)
#                 error_str = str(e)
#                 if "503" in error_str or "429" in error_str:
#                     if attempt < max_retries - 1:
#                         sleep_time = 2 ** attempt # Exponential backoff: 1s, 2s, 4s
#                         print(f"Model overload (503/429), retrying in {sleep_time}s...")
#                         time.sleep(sleep_time)
#                         continue
#                 raise e

#     # 2. Simplify Text (Gemini 2.5 Flash)
#     try:
#         prompt_simp = f"Simplify the following novel chapter for a young child (age 6-8). Return only the story text.\n\n{request.text}"
        
#         # User requested gemini-2.5-flash
#         resp_simp = generate_with_retry(
#             client_ti.models.generate_content,
#             model="gemini-2.5-flash", 
#             contents=prompt_simp
#         )
#         simplified_text = resp_simp.text
#     except Exception as e:
#         print(f"Simplification Error: {e}")
#         return {"error": f"Simplification failed: {e}"}

#     # 3. Extract Prompts
#     try:
#         prompt_extract = f"Extract a vivid image prompt and a short video prompt from this story. Return JSON: {{'image_prompt': '...', 'video_prompt': '...'}} \n\n Story: {simplified_text}"
#         resp_prompts = generate_with_retry(
#             client_ti.models.generate_content,
#             model="gemini-2.5-flash",
#             contents=prompt_extract,
#             config=types.GenerateContentConfig(response_mime_type="application/json")
#         )
#         prompts = json.loads(resp_prompts.text)
#     except Exception as e:
#         print(f"Prompt Extract Error: {e}")
#         prompts = {"image_prompt": "A magical story scene", "video_prompt": "A character walking"}

#     # 4. Generate Image (Gemini 2.5 Flash as requested)
#     image_b64 = ""
#     try:
#         # Use generate_images (plural) and specific image model if needed, 
#         # or gemini-2.5-flash if it supports it via this method.
#         # Based on debug list: models/gemini-2.5-flash-image seems appropriate.
#         resp_img = generate_with_retry(
#             client_ti.models.generate_images,
#             model="imagen-4.0-fast-generate-001", 
#             prompt=prompts.get("image_prompt", "Magic scene"),
#             config=types.GenerateImagesConfig(number_of_images=1)
#         )
#         if resp_img.generated_images:
#             img_bytes = resp_img.generated_images[0].image.image_bytes
#             image_b64 = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode('utf-8')
#     except Exception as e:
#         print(f"Image Gen Error: {e}")
#         image_b64 = "https://placehold.co/800x600?text=Image+Error"

#     # 5. Generate Video (Veo 3.0 Fast)
#     video_url = ""
#     try:
#         # User specified: veo-3.0-fast-preview -> veo-3.0-fast-generate-001
        
#         resp_video = generate_with_retry(
#             client_v.models.generate_videos,
#             model="veo-3.0-fast-generate-001",
#             prompt=prompts.get("video_prompt", "Magic video")
#         )
        
#         print(f"Video Generation Response Type: {type(resp_video)}")
#         # If the response contains a video asset directly (synchronous for fast models sometimes)
#         # or an operation.
#         # For now, we will inspect the structure via logs or just assume placeholder 
#         # until we confirm how to extract the URL/bytes from this specific SDK version's response.
        
#         # In many recent versions:
#         # if hasattr(resp_video, 'generated_videos'):
#         #     video_url = resp_video.generated_videos[0].video.uri # or similar
        
#         # For safety, logging and keeping placeholder or basic extraction if obvious.
#         if hasattr(resp_video, 'name'): # It might be an operation
#              print(f"Video Operation Name: {resp_video.name}")
        
#         video_url = "https://placehold.co/800x600?text=Video+Generated+(Check+Logs)"
        
#     except Exception as e:
#         print(f"Video Gen Error: {e}")
#         video_url = "https://placehold.co/800x600?text=Video+Error"

#     return {
#         "original_text": request.text,
#         "simplified_text": simplified_text,
#         "prompts": prompts,
#         "imageUrl": image_b64,
#         "videoUrl": video_url 
#     }

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import base64
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChapterRequest(BaseModel):
    text: str

# Initialize Gemini client ONCE
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY missing")

client = genai.Client(api_key=api_key)

@app.post("/process_chapter")
async def process_chapter(request: ChapterRequest):

    # 1️⃣ Simplify text (Gemini 2.5 Flash)
    simplify_prompt = f"""
    Simplify the following story for a 6–8 year old child.
    Use simple language and short sentences.
    Return ONLY the story text.

    Story:
    {request.text}
    """

    simplify_resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=simplify_prompt
    )

    simplified_text = simplify_resp.text

    # 2️⃣ Extract image prompt (Gemini reasoning)
    extract_prompt = f"""
    From the story below, create ONE vivid image prompt
    suitable for a children's illustrated book.

    Story:
    {simplified_text}

    Return ONLY the image prompt text.
    """

    img_prompt_resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=extract_prompt
    )

    image_prompt = img_prompt_resp.text

    # 3️⃣ Generate Image (Gemini Image Model)
    image_resp = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=image_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"]
        )
    )

    image_base64 = ""
    for part in image_resp.candidates[0].content.parts:
        if part.inline_data:
            image_bytes = part.inline_data.data
            image_base64 = (
                "data:image/png;base64," +
                base64.b64encode(image_bytes).decode()
            )

    return {
        "simplified_text": simplified_text,
        "image_prompt": image_prompt,
        "image": image_base64
    }
