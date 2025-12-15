import os
import traceback
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

key_ti = os.environ.get("GEMINI_API_KEY_TEXT_IMAGE")
client = genai.Client(api_key=key_ti)

print("Testing Image Generation...")
try:
    response = client.models.generate_images(
        model="gemini-2.5-flash",
        prompt="A cute cartoon dragon flying in the sky",
        config=types.GenerateImagesConfig(number_of_images=1)
    )
    print("Success!")
    if response.generated_images:
        print(f"Got {len(response.generated_images)} images.")
    else:
        print("Response has no generated_images.")
except Exception as e:
    print("FAILED")
    traceback.print_exc()
