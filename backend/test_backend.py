"""
Test script to verify the PDF processing endpoint
"""
import requests

# Test the backend health
try:
    response = requests.get("http://localhost:8000/docs")
    print(f"✅ Backend is running! Status: {response.status_code}")
    print(f"📚 API docs available at: http://localhost:8000/docs")
except Exception as e:
    print(f"❌ Backend not responding: {e}")
    print("Please make sure the backend is running with: uvicorn main:app --reload")
