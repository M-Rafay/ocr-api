# OCR API (FastAPI, EasyOCR, Open Source)

## Features
- Extract text from images (base64 or URL) and PDFs (multi-page)
- Supports English, Urdu, Arabic
- Image pre-processing with OpenCV
- PDF to image conversion with PyMuPDF
- SQLite for job history and quota (no external database needed)
- Monthly quota enforcement (20 requests/user)
- Dockerized

## Setup
1. Clone repo
2. Build and run Docker:
   ```bash
   docker build -t ocr-api .
   docker run -p 8000:8000 ocr-api
   ```
   
   Or run locally:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Health
`GET /health`

### Extract Text
`POST /extract-text`
- JSON: `{ "image_base64": str, "image_url": str, "language": "en|ur|ar", "user_id": str }`
- Returns: `{ "results": [ { "text": str, "confidence": float, "bbox": [...] } ] }`

### Upload PDF
`POST /upload-pdf`
- Form: `user_id` (str), `file` (PDF), `language` (optional)
- Returns: `{ "pages": { page_num: [ ... ] } }`

### History
`GET /history/{user_id}`
- Returns: `{ "history": [ ... ] }`

## Testing
- Run `pytest app/tests/`

## Notes
- Temporary files saved in `app/uploads/`
- No cloud storage used
- SQLite database for persistence (file-based)
- Quota: 20 requests/user/month (free tier simulation) 