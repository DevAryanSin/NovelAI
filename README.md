# NovelAI - AI-Powered Children's Storybook Generator

Transform any PDF into an engaging, illustrated children's storybook using Google's Gemini API.


## Overview

NovelAI is an intelligent application that leverages **Google's Gemini 2.5 Flash API** to automatically convert complex PDF documents into child-friendly storybooks complete with AI generated illustrations. The application simplifies text for young readers (ages 6-8) and creates colorful, engaging images that bring stories to life.

## Why Gemini API is Essential

This project fundamentally relies on **two distinct Gemini models** to achieve its core functionality:

### 1. **Gemini 2.5 Flash (Text Generation)**
- **Purpose**: Simplifies complex text into child-friendly language
- **Why it's necessary**: 
  - Transforms adult-level content into age-appropriate narratives
  - Generates concise, meaningful chapter titles (2-3 words)
  - Gemini chatbot answers from uploaded novel pdf as core memory
  - Creates detailed image prompts for illustration generation
  - Maintains story coherence while simplifying vocabulary
  - Uses structured JSON output for reliable parsing

**API Implementation:**
```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.6
    )
)
```

### 2. **Gemini 2.5 Flash Image (Image Generation)**
- **Purpose**: Creates colorful children's book illustrations
- **Why it's necessary**:
  - Generates unique, context-aware images for each chapter
  - Produces child-friendly, vibrant illustrations
  - Maintains consistent artistic style throughout the book
  - No external image APIs or databases required

**API Implementation:**
```python
response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=f"Children's book illustration, colorful: {prompt}",
    config=types.GenerateContentConfig(response_modalities=["IMAGE"])
)
```


## Features

-  **PDF Text Extraction**: Automatically extracts and chunks content into chapters
-  **Text Simplification**: Converts complex text into simple, engaging stories
-  **AI Generated Illustrations**: Creates unique images for each chapter
-  **Lazy Loading**: On-demand chapter processing for optimised performance
-  **Image Caching**: Reduces redundant API calls and improves speed
-  **Retry Mechanism**: Robust error handling with exponential backoff
-  **Rate Limiting**: Semaphore-based concurrency control


## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    (Next.js + React)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ PDF Upload   │  │ Book Display │  │ Story View   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST API
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         Backend                             │
│                    (FastAPI + Python)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ PDF Parser   │  │ Text Processor│  │ Image Gen    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Google Gemini API                        │
│  ┌──────────────────────────┐  ┌──────────────────────┐    │
│  │  Gemini 2.5 Flash        │  │ Gemini 2.5 Flash     │    │
│  │  (Text Simplification)   │  │ Image (Illustrations)│    │
│  └──────────────────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

##  Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **Google Gemini API**: AI text and image generation
- **PyPDF2**: PDF text extraction
- **Pydantic**: Data validation and serialization
- **Python-dotenv**: Environment variable management

### Frontend
- **Next.js 16**: React framework with server-side rendering
- **React 19**: Modern UI library
- **Framer Motion**: Smooth animations and transitions
- **TailwindCSS 4**: Utility-first CSS framework
- **TypeScript**: Type-safe development


## Usage

1. **Upload a PDF**: Click the upload button and select any PDF document
2. **Wait for Processing**: The app extracts text and splits it into chapters
3. **View Chapters**: Navigate through chapters using the interactive UI
4. **Lazy Loading**: Chapters are simplified and illustrated on-demand as you view them
5. **Enjoy**: Read the simplified story with beautiful AI-generated illustrations!


## ⚡ Gemini API Optimization Techniques

### 1. **Concurrency Control**
```python
TEXT_SEMAPHORE = asyncio.Semaphore(2)   # Max 2 concurrent text requests
IMAGE_SEMAPHORE = asyncio.Semaphore(1)  # Max 1 concurrent image request
```

### 2. **Image Caching**
```python
IMAGE_CACHE: dict[str, str] = {}  # Cache generated images by prompt
```

### 3. **Retry with Exponential Backoff**
```python
async def retry_with_backoff(func, *args, max_retries=5, initial_delay=1, **kwargs):
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except ServerError as e:
            if e.code == 503:  # Model overloaded
                delay = initial_delay * (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(delay)
```

### 4. **Structured JSON Output**
```python
config=types.GenerateContentConfig(
    response_mime_type="application/json",  # Ensures parseable output
    temperature=0.6  # Balanced creativity
)
```

### 5. **Lazy Loading**
- Chapters are only processed when viewed by the user
- Reduces initial load time and API costs
- Improves user experience with progressive loading

##  Performance Metrics

- **PDF Processing**: ~10-30 seconds (depending on size)
- **Text Simplification**: ~2-5 seconds per chapter
- **Image Generation**: ~3-8 seconds per image
- **Total Time (10 chapters)**: ~5-10 minutes (with lazy loading)

## Error Handling

- **503 Errors**: Automatic retry with exponential backoff
- **Rate Limiting**: Semaphore-based concurrency control
- **Network Failures**: Graceful degradation with user feedback
- **Invalid PDFs**: Clear error messages
- **API Quota**: Informative error responses



---

**Built with ❤️ using Google Gemini API**
