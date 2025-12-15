import requests
import json

url = "http://127.0.0.1:8000/process_chapter"
payload = {"text": "A tiny dragon learned to fly in a magical forest."}

print("Sending request to backend...")
try:
    response = requests.post(url, json=payload, timeout=60)
    with open("test_result_log.txt", "w") as f:
        f.write(f"Status Code: {response.status_code}\n")
        if response.status_code == 200:
            data = response.json()
            f.write(f"Response Keys: {data.keys()}\n")
            f.write(f"Simplified Text: {data.get('simplified_text')[:100]}...\n")
            image_url = data.get("imageUrl", "")
            if image_url.startswith("data:image"):
                f.write(f"Image Generated Successfully! Length: {len(image_url)}\n")
            else:
                f.write(f"Image Generation Failed: {image_url}\n")
            
            f.write(f"Video URL: {data.get('videoUrl')}\n")
        else:
            f.write(f"Error Response: {response.text}\n")
except Exception as e:
    print(f"Request failed: {e}")
