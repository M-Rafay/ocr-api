# OCR API Documentation

## Overview

The OCR API is a FastAPI-based service that extracts text from images and PDFs using EasyOCR. It supports multiple languages (English, Urdu, Arabic) and includes features like image pre-processing, PDF parsing, and usage tracking. The service uses SQLite for data persistence, making it easy to deploy without external database dependencies.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, the API uses a simple `user_id` system for tracking usage and enforcing quotas.

## Rate Limiting
- **Free Tier**: 20 requests per user per month
- **Quota Reset**: Monthly (1st of each month)
- **Exceeded Quota**: Returns HTTP 429 (Too Many Requests)

## Data Storage
- **Database**: SQLite (file-based, no external dependencies)
- **File Storage**: Local file system for temporary uploads
- **Persistence**: Job history and user data stored in SQLite database

---

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
  "status": "ok"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Extract Text from Image

**POST** `/extract-text`

Extract text from an image using OCR. Accepts either base64-encoded image or image URL.

**Request Body:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",  // Optional
  "image_url": "https://example.com/image.png",     // Optional
  "language": "en",                                  // Optional: "en", "ur", "ar"
  "user_id": "user123"                              // Required
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "Hello World",
      "confidence": 0.95,
      "bbox": [[10, 20], [100, 20], [100, 40], [10, 40]]
    },
    {
      "text": "Sample Text",
      "confidence": 0.87,
      "bbox": [[50, 60], [150, 60], [150, 80], [50, 80]]
    }
  ]
}
```

**Example with base64:**
```bash
curl -X POST http://localhost:8000/extract-text \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "user_id": "user123",
    "language": "en"
  }'
```

**Example with URL:**
```bash
curl -X POST http://localhost:8000/extract-text \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.png",
    "user_id": "user123",
    "language": "ur"
  }'
```

**Supported Languages:**
- `en` - English (default)
- `ur` - Urdu
- `ar` - Arabic

---

### 3. Upload and Extract PDF

**POST** `/upload-pdf`

Upload a PDF file and extract text from all pages.

**Request:**
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: PDF file (required)
  - `user_id`: User identifier (required)
  - `language`: Language code (optional, default: "en")

**Response:**
```json
{
  "pages": {
    "1": [
      {
        "text": "Page 1 Content",
        "confidence": 0.92,
        "bbox": [[10, 20], [200, 20], [200, 40], [10, 40]]
      }
    ],
    "2": [
      {
        "text": "Page 2 Content",
        "confidence": 0.88,
        "bbox": [[15, 25], [180, 25], [180, 45], [15, 45]]
      }
    ]
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/upload-pdf \
  -F "file=@document.pdf" \
  -F "user_id=user123" \
  -F "language=en"
```

---

### 4. Get User History

**GET** `/history/{user_id}`

Retrieve OCR job history for a specific user.

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "input_type": "image",
      "input_path": "/app/uploads/img_user123.png",
      "language": "en",
      "result": [
        {
          "text": "Extracted text",
          "confidence": 0.95,
          "bbox": [[10, 20], [100, 20], [100, 40], [10, 40]]
        }
      ],
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "input_type": "pdf",
      "input_path": "/app/uploads/pdf_user123.pdf",
      "language": "en",
      "result": {
        "1": [...],
        "2": [...]
      },
      "created_at": "2024-01-15T11:45:00"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8000/history/user123
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Provide image_base64 or image_url"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Monthly quota exceeded (20 requests)"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Usage Examples

### Python Example

```python
import requests
import base64

# Extract text from image URL
def extract_text_from_url(image_url, user_id, language="en"):
    url = "http://localhost:8000/extract-text"
    data = {
        "image_url": image_url,
        "user_id": user_id,
        "language": language
    }
    response = requests.post(url, json=data)
    return response.json()

# Extract text from base64 image
def extract_text_from_base64(image_path, user_id, language="en"):
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
    
    url = "http://localhost:8000/extract-text"
    data = {
        "image_base64": image_base64,
        "user_id": user_id,
        "language": language
    }
    response = requests.post(url, json=data)
    return response.json()

# Upload PDF
def upload_pdf(pdf_path, user_id, language="en"):
    url = "http://localhost:8000/upload-pdf"
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        data = {"user_id": user_id, "language": language}
        response = requests.post(url, files=files, data=data)
    return response.json()

# Get history
def get_history(user_id):
    url = f"http://localhost:8000/history/{user_id}"
    response = requests.get(url)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Extract from URL
    result = extract_text_from_url(
        "https://example.com/image.png",
        "user123",
        "en"
    )
    print("Extracted text:", result)
    
    # Extract from local image
    result = extract_text_from_base64(
        "local_image.png",
        "user123",
        "ur"
    )
    print("Extracted text:", result)
    
    # Upload PDF
    result = upload_pdf("document.pdf", "user123")
    print("PDF pages:", result)
    
    # Get history
    history = get_history("user123")
    print("History:", history)
```

### JavaScript Example

```javascript
// Extract text from image URL
async function extractTextFromUrl(imageUrl, userId, language = 'en') {
    const response = await fetch('http://localhost:8000/extract-text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_url: imageUrl,
            user_id: userId,
            language: language
        })
    });
    return await response.json();
}

// Extract text from base64 image
async function extractTextFromBase64(imageBase64, userId, language = 'en') {
    const response = await fetch('http://localhost:8000/extract-text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_base64: imageBase64,
            user_id: userId,
            language: language
        })
    });
    return await response.json();
}

// Upload PDF
async function uploadPdf(file, userId, language = 'en') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    formData.append('language', language);
    
    const response = await fetch('http://localhost:8000/upload-pdf', {
        method: 'POST',
        body: formData
    });
    return await response.json();
}

// Get history
async function getHistory(userId) {
    const response = await fetch(`http://localhost:8000/history/${userId}`);
    return await response.json();
}

// Example usage
async function example() {
    try {
        // Extract from URL
        const result1 = await extractTextFromUrl(
            'https://example.com/image.png',
            'user123',
            'en'
        );
        console.log('Extracted text:', result1);
        
        // Upload PDF
        const fileInput = document.getElementById('pdfFile');
        const result2 = await uploadPdf(
            fileInput.files[0],
            'user123',
            'en'
        );
        console.log('PDF pages:', result2);
        
        // Get history
        const history = await getHistory('user123');
        console.log('History:', history);
    } catch (error) {
        console.error('Error:', error);
    }
}
```

---

## Best Practices

1. **Image Quality**: Use high-resolution images for better OCR accuracy
2. **Language Selection**: Choose the correct language for better results
3. **File Size**: Keep PDF files reasonable in size (< 50MB)
4. **Rate Limiting**: Monitor your usage to avoid quota limits
5. **Error Handling**: Always handle potential errors in your applications

## Supported File Formats

- **Images**: PNG, JPEG, JPG, BMP, TIFF
- **PDFs**: All PDF versions supported

## Performance Notes

- **Processing Time**: 1-5 seconds per image/page depending on size
- **Memory Usage**: Varies with image/PDF size
- **Concurrent Requests**: Limited by server resources 