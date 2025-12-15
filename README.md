# Novel AI for Kids 📚✨

Transform any PDF novel into a beautiful, illustrated children's book using Google Gemini AI!

## Features

- **PDF Upload**: Upload any novel in PDF format
- **Smart Chapter Detection**: Automatically detects and splits chapters
- **Kid-Friendly Text**: Rewrites complex text in simple English for children aged 6-8
- **Beautiful Illustrations**: Generates 2 unique AI images for each chapter
- **Book-Like Interface**: Stunning page-flip animations and book formatting
- **Chapter Navigation**: Easy navigation between chapters

## How It Works

1. **Upload a PDF**: Drag and drop or click to upload your novel PDF
2. **AI Processing**: 
   - Extracts text from PDF
   - Detects chapters automatically
   - Simplifies text for kids using Gemini 2.5 Flash
   - Generates 2 unique illustrations per chapter using Gemini Image
3. **Read & Enjoy**: Beautiful book viewer with page flipping animations

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file with your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

Run the backend:
```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Tech Stack

### Backend
- FastAPI
- Google Gemini API (gemini-2.5-flash, gemini-2.5-flash-image)
- PyPDF2 for PDF processing
- Python 3.x

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- Framer Motion (animations)
- Lucide React (icons)

## API Endpoints

### POST `/process_pdf`
Processes a PDF file and returns a complete book with simplified text and images.

**Request**: Multipart form data with PDF file
**Response**:
```json
{
  "title": "Book Title",
  "total_chapters": 5,
  "chapters": [
    {
      "chapter_number": 1,
      "title": "Chapter Title",
      "simplified_text": "Kid-friendly text...",
      "image1": "base64_image_data",
      "image2": "base64_image_data",
      "image1_prompt": "Image description",
      "image2_prompt": "Image description"
    }
  ]
}
```

## Features in Detail

### Chapter Detection
The system automatically detects chapters using common patterns:
- "Chapter 1", "CHAPTER I", "Ch. 1", etc.
- Falls back to splitting by word count if no chapters detected
- Limits to 10 chapters for demo purposes

### Text Simplification
- Rewrites complex language into simple, engaging text
- Uses short sentences and simple words
- Maintains the main story elements
- Perfect for children aged 6-8

### Image Generation
- Creates 2 unique illustrations per chapter
- Children's book illustration style
- Colorful and vibrant
- Based on the simplified story content

### Book Viewer
- Beautiful book-like layout
- 3D page flip animations
- Text on left, images on right
- Chapter navigation buttons
- Page counter
- Responsive design

## Limitations

- Maximum 10 chapters processed (demo limitation)
- Chapter text limited to 3000 characters
- PDF must be text-based (not scanned images)
- Requires valid Gemini API key

## Future Enhancements

- [ ] Support for more chapters
- [ ] PDF download of the illustrated book
- [ ] Multiple language support
- [ ] Custom illustration styles
- [ ] Audio narration
- [ ] Save/load processed books

## License

MIT

## Credits

Powered by Google Gemini AI ❤️
