# Quick Start Guide - OCR API

## Prerequisites

- Python 3.8+ or Docker
- Git

## Installation Options

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ocr-api
   ```

2. **Build and run with Docker**
   ```bash
   docker build -t ocr-api .
   docker run -p 8000:8000 ocr-api
   ```

3. **Test the API**
   ```bash
   curl http://localhost:8000/health
   ```

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ocr-api
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Test the API**
   ```bash
   curl http://localhost:8000/health
   ```

---

## Your First OCR Request

### 1. Extract Text from an Image URL

```bash
curl -X POST http://localhost:8000/extract-text \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/sample-text-image.png",
    "user_id": "my-first-user",
    "language": "en"
  }'
```

### 2. Extract Text from a Local Image

First, convert your image to base64:
```python
import base64

with open("my-image.png", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()
```

Then make the request:
```bash
curl -X POST http://localhost:8000/extract-text \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "'$image_base64'",
    "user_id": "my-first-user",
    "language": "en"
  }'
```

### 3. Upload and Extract PDF

```bash
curl -X POST http://localhost:8000/upload-pdf \
  -F "file=@my-document.pdf" \
  -F "user_id=my-first-user" \
  -F "language=en"
```

### 4. Check Your History

```bash
curl http://localhost:8000/history/my-first-user
```

---

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide interactive documentation where you can test the API directly in your browser.

---

## Common Use Cases

### 1. Document Digitization

```python
import requests

def digitize_document(pdf_path, user_id):
    """Convert PDF document to searchable text"""
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        data = {'user_id': user_id, 'language': 'en'}
        response = requests.post(
            'http://localhost:8000/upload-pdf',
            files=files,
            data=data
        )
    return response.json()

# Usage
result = digitize_document('invoice.pdf', 'user123')
for page_num, text_blocks in result['pages'].items():
    print(f"Page {page_num}:")
    for block in text_blocks:
        print(f"  - {block['text']} (confidence: {block['confidence']:.2f})")
```

### 2. Receipt Processing

```python
import requests
import base64

def process_receipt(image_path, user_id):
    """Extract text from receipt image"""
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode()
    
    response = requests.post(
        'http://localhost:8000/extract-text',
        json={
            'image_base64': image_base64,
            'user_id': user_id,
            'language': 'en'
        }
    )
    return response.json()

# Usage
result = process_receipt('receipt.jpg', 'user123')
total_amount = None
for block in result['results']:
    if '$' in block['text'] or 'total' in block['text'].lower():
        print(f"Found amount: {block['text']}")
```

### 3. Multi-language Support

```python
def extract_multilingual_text(image_url, user_id):
    """Try multiple languages for better results"""
    languages = ['en', 'ur', 'ar']
    results = {}
    
    for lang in languages:
        response = requests.post(
            'http://localhost:8000/extract-text',
            json={
                'image_url': image_url,
                'user_id': user_id,
                'language': lang
            }
        )
        results[lang] = response.json()
    
    return results

# Usage
results = extract_multilingual_text('multilingual-image.png', 'user123')
for lang, result in results.items():
    print(f"{lang}: {[r['text'] for r in result['results']]}")
```

---

## Troubleshooting

### Common Issues

1. **"Monthly quota exceeded"**
   - Solution: Wait until next month or use a different `user_id`

2. **"Provide image_base64 or image_url"**
   - Solution: Make sure you're providing either `image_base64` or `image_url` in your request

3. **Docker build fails**
   - Solution: Ensure Docker is running and you have sufficient disk space

4. **OCR accuracy is low**
   - Solutions:
     - Use higher resolution images
     - Ensure good contrast between text and background
     - Choose the correct language
     - Pre-process images (crop, enhance contrast)

### Performance Tips

1. **For large PDFs**: Consider processing pages in batches
2. **For multiple images**: Use concurrent requests (but respect rate limits)
3. **For production**: Monitor memory usage and implement cleanup

### Monitoring Usage

```python
import requests

def check_usage(user_id):
    """Check how many API calls you've made this month"""
    history = requests.get(f'http://localhost:8000/history/{user_id}').json()
    return len(history['history'])

# Usage
calls_this_month = check_usage('user123')
print(f"API calls this month: {calls_this_month}/20")
```

---

## Next Steps

1. **Explore the full API documentation**: See `docs/API_Documentation.md`
2. **Run the test suite**: `pytest app/tests/`
3. **Customize the quota limits**: Modify `MONTHLY_QUOTA` in `app/middleware.py`
4. **Add authentication**: Implement proper user authentication
5. **Scale the application**: Add load balancing and caching

---

## Support

- **API Documentation**: `docs/API_Documentation.md`
- **Interactive Docs**: http://localhost:8000/docs
- **Issues**: Create an issue in the repository
- **Testing**: Run `pytest app/tests/` to verify functionality 