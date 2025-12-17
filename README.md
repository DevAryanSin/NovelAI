# 📚 NovelAI - AI-Powered Children's Storybook Generator

Transform any PDF into an engaging, illustrated children's storybook using the power of Google's Gemini API.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Next.js](https://img.shields.io/badge/next.js-16.0+-black.svg)
![Gemini API](https://img.shields.io/badge/Gemini-API-orange.svg)

## 🌟 Overview

NovelAI is an intelligent application that leverages **Google's Gemini 2.5 Flash API** to automatically convert complex PDF documents into child-friendly storybooks complete with AI-generated illustrations. The application simplifies text for young readers (ages 6-8) and creates colorful, engaging images that bring stories to life.

## 🎯 Why Gemini API is Essential

This project fundamentally relies on **two distinct Gemini models** to achieve its core functionality:

### 1. **Gemini 2.5 Flash (Text Generation)**
- **Purpose**: Simplifies complex text into child-friendly language
- **Why it's necessary**: 
  - Transforms adult-level content into age-appropriate narratives
  - Generates concise, meaningful chapter titles (2-3 words)
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

### 🔑 Key Gemini API Features Utilized

1. **Multimodal Capabilities**: Seamlessly switches between text and image generation
2. **Structured Output**: JSON mode ensures reliable, parseable responses
3. **High Performance**: Fast response times enable real-time processing
4. **Cost Efficiency**: Flash models provide excellent quality at lower costs
5. **Reliability**: Built-in retry logic handles API rate limits gracefully

## 🚀 Features

- ✅ **PDF Text Extraction**: Automatically extracts and chunks content into chapters
- ✅ **Intelligent Text Simplification**: Converts complex text into simple, engaging stories
- ✅ **AI-Generated Illustrations**: Creates unique images for each chapter
- ✅ **Lazy Loading**: On-demand chapter processing for optimal performance
- ✅ **Progress Tracking**: Real-time feedback during PDF processing
- ✅ **Image Caching**: Reduces redundant API calls and improves speed
- ✅ **Retry Mechanism**: Robust error handling with exponential backoff
- ✅ **Rate Limiting**: Semaphore-based concurrency control
- ✅ **Interactive UI**: Beautiful, responsive Next.js frontend with animations

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

## 🛠️ Technology Stack

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

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey))

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/NovelAI.git
cd NovelAI/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```env
GEMINI_API_KEY=your_api_key_here
```

5. **Run the backend server**
```bash
uvicorn main:app --reload --port 8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment variables**
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. **Run the development server**
```bash
npm run dev
```

5. **Open your browser**
```
http://localhost:3000
```

## 🎮 Usage

1. **Upload a PDF**: Click the upload button and select any PDF document
2. **Wait for Processing**: The app extracts text and splits it into chapters
3. **View Chapters**: Navigate through chapters using the interactive UI
4. **Lazy Loading**: Chapters are simplified and illustrated on-demand as you view them
5. **Enjoy**: Read the simplified story with beautiful AI-generated illustrations!

## 🔧 API Endpoints

### `POST /process_pdf`
Uploads and processes a PDF file, extracting chapters.

**Request:**
- Content-Type: `multipart/form-data`
- Body: PDF file

**Response:**
- Server-Sent Events (SSE) stream with progress updates
- Final payload: `ProcessedBook` object with chapters

### `POST /simplify_chapter`
Simplifies a single chapter using Gemini AI.

**Request:**
```json
{
  "chapter_number": 1,
  "raw_text": "Original chapter text..."
}
```

**Response:**
```json
{
  "success": true,
  "chapter_number": 1,
  "title": "Magic Forest",
  "simplified_text": "Once upon a time...",
  "image_prompt": "Colorful forest with talking animals..."
}
```

### `POST /generate_images`
Generates an illustration for a chapter.

**Request:**
```json
{
  "chapter_number": 1,
  "image_prompt": "A magical forest scene..."
}
```

**Response:**
```json
{
  "image": "data:image/png;base64,..."
}
```

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

## 📊 Performance Metrics

- **PDF Processing**: ~10-30 seconds (depending on size)
- **Text Simplification**: ~2-5 seconds per chapter
- **Image Generation**: ~3-8 seconds per image
- **Total Time (10 chapters)**: ~5-10 minutes (with lazy loading)

## 🐛 Error Handling

The application includes comprehensive error handling:

- **503 Errors**: Automatic retry with exponential backoff
- **Rate Limiting**: Semaphore-based concurrency control
- **Network Failures**: Graceful degradation with user feedback
- **Invalid PDFs**: Clear error messages
- **API Quota**: Informative error responses

## 🚢 Deployment

### Backend (Render/Railway)
```bash
# Dockerfile included
docker build -t novelai-backend .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key novelai-backend
```

### Frontend (Vercel)
```bash
# vercel.json included
vercel --prod
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini Team**: For providing powerful multimodal AI capabilities
- **FastAPI**: For the excellent async web framework
- **Next.js Team**: For the amazing React framework
- **Open Source Community**: For the incredible tools and libraries

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using Google Gemini API**
