# User Guide - OCR API

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [API Endpoints Deep Dive](#api-endpoints-deep-dive)
4. [Language Support](#language-support)
5. [Image Processing](#image-processing)
6. [PDF Processing](#pdf-processing)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Best Practices](#best-practices)
10. [Advanced Usage](#advanced-usage)
11. [Troubleshooting](#troubleshooting)

---

## Introduction

The OCR API is a powerful text extraction service that converts images and PDFs into searchable text. It uses EasyOCR for high-accuracy text recognition and supports multiple languages including English, Urdu, and Arabic.

### Key Features

- **Multi-language Support**: English, Urdu, Arabic
- **Multiple Input Formats**: Images (PNG, JPEG, etc.) and PDFs
- **Image Pre-processing**: Automatic enhancement for better accuracy
- **Bounding Box Detection**: Precise text location information
- **Confidence Scoring**: Quality assessment for each text block
- **Usage Tracking**: Monitor your API usage
- **Rate Limiting**: Fair usage policies

---

## Getting Started

### Prerequisites

- API endpoint URL (default: `http://localhost:8000`)
- User ID for tracking (any string you choose)
- Images or PDFs to process

### Basic Setup

1. **Start the API server** (see Quick Start Guide)
2. **Test connectivity**:
   ```bash
   curl http://localhost:8000/health
   ```
3. **Make your first request** (see examples below)

---

## API Endpoints Deep Dive

### 1. Health Check

**Purpose**: Verify API availability and status

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok"
}
```

**Use Cases**:
- Monitoring API availability
- Load balancer health checks
- Pre-flight requests

### 2. Extract Text from Image

**Purpose**: Extract text from images using OCR

**Endpoint**: `POST /extract-text`

**Request Format**:
```json
{
  "image_base64": "base64_encoded_image_string",
  "image_url": "https://example.com/image.png",
  "language": "en",
  "user_id": "your_user_id"
}
```

**Parameters**:
- `image_base64` (optional): Base64-encoded image data
- `image_url` (optional): Public URL to an image
- `language` (optional): Language code ("en", "ur", "ar")
- `user_id` (required): Your unique identifier

**Response Format**:
```json
{
  "results": [
    {
      "text": "Extracted text content",
      "confidence": 0.95,
      "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
  ]
}
```

**Response Fields**:
- `text`: The extracted text string
- `confidence`: Confidence score (0.0 to 1.0)
- `bbox`: Bounding box coordinates (4 points defining text area)

### 3. Upload and Extract PDF

**Purpose**: Process multi-page PDF documents

**Endpoint**: `POST /upload-pdf`

**Request Format**: `multipart/form-data`

**Parameters**:
- `file`: PDF file (required)
- `user_id`: User identifier (required)
- `language`: Language code (optional, default: "en")

**Response Format**:
```json
{
  "pages": {
    "1": [
      {
        "text": "Page 1 content",
        "confidence": 0.92,
        "bbox": [[10, 20], [200, 20], [200, 40], [10, 40]]
      }
    ],
    "2": [
      {
        "text": "Page 2 content",
        "confidence": 0.88,
        "bbox": [[15, 25], [180, 25], [180, 45], [15, 45]]
      }
    ]
  }
}
```

### 4. Get User History

**Purpose**: Retrieve your OCR processing history

**Endpoint**: `GET /history/{user_id}`

**Response Format**:
```json
{
  "history": [
    {
      "id": 1,
      "input_type": "image",
      "input_path": "/app/uploads/img_user123.png",
      "language": "en",
      "result": [...],
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

---

## Language Support

### Supported Languages

| Language | Code | Best For |
|----------|------|----------|
| English | `en` | General text, documents, receipts |
| Urdu | `ur` | Urdu text, documents, newspapers |
| Arabic | `ar` | Arabic text, documents, books |

### Language Selection Tips

1. **Choose the primary language** of your document
2. **For mixed-language documents**, try the dominant language first
3. **For unknown content**, start with English (`en`)
4. **For better accuracy**, specify the exact language

### Multi-language Processing

```python
def process_multilingual_document(image_url, user_id):
    """Process document with multiple languages for best results"""
    languages = ['en', 'ur', 'ar']
    all_results = {}
    
    for lang in languages:
        try:
            response = requests.post(
                'http://localhost:8000/extract-text',
                json={
                    'image_url': image_url,
                    'user_id': user_id,
                    'language': lang
                }
            )
            all_results[lang] = response.json()
        except Exception as e:
            print(f"Error with {lang}: {e}")
    
    return all_results
```

---

## Image Processing

### Supported Formats

- **PNG**: Best for screenshots and digital images
- **JPEG/JPG**: Good for photos and scanned documents
- **BMP**: Basic bitmap format
- **TIFF**: High-quality scanned documents

### Image Quality Guidelines

#### Optimal Conditions
- **Resolution**: 300+ DPI for scanned documents
- **Contrast**: High contrast between text and background
- **Lighting**: Even, well-lit images
- **Orientation**: Text should be horizontal
- **File Size**: Under 10MB for best performance

#### Pre-processing Tips

1. **Enhance Contrast**:
   ```python
   import cv2
   import numpy as np
   
   def enhance_contrast(image_path):
       img = cv2.imread(image_path)
       # Convert to grayscale
       gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
       # Apply histogram equalization
       enhanced = cv2.equalizeHist(gray)
       return enhanced
   ```

2. **Remove Noise**:
   ```python
   def denoise_image(image_path):
       img = cv2.imread(image_path)
       # Apply bilateral filter
       denoised = cv2.bilateralFilter(img, 9, 75, 75)
       return denoised
   ```

3. **Resize for Processing**:
   ```python
   def resize_for_ocr(image_path, max_width=2000):
       img = cv2.imread(image_path)
       height, width = img.shape[:2]
       
       if width > max_width:
           ratio = max_width / width
           new_width = max_width
           new_height = int(height * ratio)
           resized = cv2.resize(img, (new_width, new_height))
           return resized
       return img
   ```

### Image Upload Methods

#### Method 1: Base64 Encoding
```python
import base64

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Usage
image_base64 = encode_image_to_base64("document.png")
```

#### Method 2: Direct URL
```python
# Use a publicly accessible URL
image_url = "https://example.com/document.png"
```

#### Method 3: Local File Upload
```python
def upload_local_image(image_path, user_id, language="en"):
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode()
    
    response = requests.post(
        "http://localhost:8000/extract-text",
        json={
            "image_base64": image_base64,
            "user_id": user_id,
            "language": language
        }
    )
    return response.json()
```

---

## PDF Processing

### PDF Requirements

- **Format**: Any standard PDF
- **Size**: Recommended under 50MB
- **Pages**: No limit (processed page by page)
- **Content**: Text-based PDFs work best

### PDF Processing Workflow

1. **Upload**: PDF is uploaded via multipart form
2. **Conversion**: Each page is converted to high-resolution image
3. **OCR**: Each page image is processed with OCR
4. **Results**: Text is organized by page number

### PDF Processing Example

```python
def process_pdf_document(pdf_path, user_id, language="en"):
    """Process a PDF document and extract text from all pages"""
    
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        data = {
            "user_id": user_id,
            "language": language
        }
        
        response = requests.post(
            "http://localhost:8000/upload-pdf",
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        
        # Process results by page
        for page_num, text_blocks in result["pages"].items():
            print(f"\n--- Page {page_num} ---")
            for block in text_blocks:
                print(f"Text: {block['text']}")
                print(f"Confidence: {block['confidence']:.2f}")
                print(f"Bounding Box: {block['bbox']}")
                print()
        
        return result
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Usage
result = process_pdf_document("invoice.pdf", "user123", "en")
```

### Large PDF Processing

For large PDFs, consider processing in batches:

```python
def process_large_pdf_in_batches(pdf_path, user_id, batch_size=10):
    """Process large PDFs by splitting into smaller chunks"""
    
    # First, get total pages (you might need to implement this)
    # For now, we'll process the entire PDF
    
    result = process_pdf_document(pdf_path, user_id)
    
    if result:
        total_pages = len(result["pages"])
        print(f"Processed {total_pages} pages")
        
        # Process results in batches
        for i in range(0, total_pages, batch_size):
            batch_pages = list(result["pages"].keys())[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}: pages {batch_pages}")
            
            # Process this batch
            for page_num in batch_pages:
                text_blocks = result["pages"][page_num]
                # Your processing logic here
                pass
    
    return result
```

---

## Error Handling

### Common Error Codes

| Status Code | Error | Description | Solution |
|-------------|-------|-------------|----------|
| 400 | Bad Request | Invalid request format | Check request body format |
| 429 | Too Many Requests | Quota exceeded | Wait or use different user_id |
| 500 | Internal Server Error | Server processing error | Retry or contact support |

### Error Handling Best Practices

```python
import requests
from requests.exceptions import RequestException

def safe_ocr_request(image_url, user_id, language="en"):
    """Make OCR request with proper error handling"""
    
    try:
        response = requests.post(
            "http://localhost:8000/extract-text",
            json={
                "image_url": image_url,
                "user_id": user_id,
                "language": language
            },
            timeout=30  # 30 second timeout
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("Rate limit exceeded. Try again later or use different user_id.")
            return None
        elif response.status_code == 400:
            print(f"Bad request: {response.json()}")
            return None
        else:
            print(f"Unexpected error: {response.status_code}")
            return None
            
    except RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
result = safe_ocr_request("https://example.com/image.png", "user123")
if result:
    print("OCR successful!")
else:
    print("OCR failed!")
```

### Retry Logic

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """Decorator to retry failed requests"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=1)
def robust_ocr_request(image_url, user_id, language="en"):
    """Robust OCR request with retry logic"""
    return safe_ocr_request(image_url, user_id, language)
```

---

## Rate Limiting

### Quota System

- **Free Tier**: 20 requests per user per month
- **Reset Date**: 1st of each month
- **Tracking**: Based on user_id

### Monitoring Usage

```python
def check_monthly_usage(user_id):
    """Check how many API calls you've made this month"""
    try:
        response = requests.get(f"http://localhost:8000/history/{user_id}")
        if response.status_code == 200:
            history = response.json()
            return len(history["history"])
        else:
            print(f"Error checking usage: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_usage_summary(user_id):
    """Get detailed usage summary"""
    usage_count = check_monthly_usage(user_id)
    if usage_count is not None:
        remaining = max(0, 20 - usage_count)
        print(f"API calls this month: {usage_count}/20")
        print(f"Remaining calls: {remaining}")
        
        if remaining == 0:
            print("⚠️  Monthly quota reached!")
        elif remaining <= 5:
            print("⚠️  Low quota remaining!")
        else:
            print("✅ Quota status: Good")
        
        return {
            "used": usage_count,
            "remaining": remaining,
            "limit": 20
        }
    return None

# Usage
summary = get_usage_summary("user123")
```

### Quota Management Strategies

1. **Use Multiple User IDs**:
   ```python
   def get_next_user_id(base_id, current_usage):
       """Get next available user ID when quota is reached"""
       if current_usage >= 20:
           return f"{base_id}_{int(time.time())}"
       return base_id
   ```

2. **Batch Processing**:
   ```python
   def batch_process_images(image_urls, base_user_id):
       """Process multiple images while respecting quota"""
       results = []
       user_id = base_user_id
       
       for i, url in enumerate(image_urls):
           # Check usage every 10 requests
           if i % 10 == 0:
               usage = check_monthly_usage(user_id)
               if usage and usage >= 20:
                   user_id = f"{base_user_id}_{i}"
           
           result = safe_ocr_request(url, user_id)
           if result:
               results.append(result)
       
       return results
   ```

---

## Best Practices

### 1. Image Preparation

- **Use high-resolution images** (300+ DPI for documents)
- **Ensure good contrast** between text and background
- **Avoid blurry or skewed images**
- **Crop unnecessary areas** to focus on text
- **Use appropriate file formats** (PNG for screenshots, JPEG for photos)

### 2. Language Selection

- **Choose the primary language** of your document
- **For mixed-language documents**, process with dominant language first
- **Try multiple languages** for better accuracy on complex documents
- **Use English as fallback** for unknown content

### 3. Error Handling

- **Always implement proper error handling**
- **Use timeouts** to prevent hanging requests
- **Implement retry logic** for transient failures
- **Log errors** for debugging and monitoring

### 4. Performance Optimization

- **Process images in batches** for multiple documents
- **Use appropriate image sizes** (don't send unnecessarily large images)
- **Implement caching** for repeated requests
- **Monitor memory usage** for large PDFs

### 5. Security Considerations

- **Validate input data** before sending to API
- **Use HTTPS** in production environments
- **Implement proper authentication** for production use
- **Sanitize user inputs** to prevent injection attacks

### 6. Monitoring and Logging

```python
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitored_ocr_request(image_url, user_id, language="en"):
    """OCR request with comprehensive monitoring"""
    start_time = time.time()
    
    try:
        logger.info(f"Starting OCR request for user {user_id}")
        
        result = safe_ocr_request(image_url, user_id, language)
        
        processing_time = time.time() - start_time
        logger.info(f"OCR completed in {processing_time:.2f}s")
        
        if result:
            text_count = len(result.get("results", []))
            logger.info(f"Extracted {text_count} text blocks")
        
        return result
        
    except Exception as e:
        logger.error(f"OCR request failed: {e}")
        return None
```

---

## Advanced Usage

### 1. Custom Image Pre-processing

```python
import cv2
import numpy as np
from PIL import Image, ImageEnhance

def preprocess_image_for_ocr(image_path):
    """Custom image pre-processing for better OCR results"""
    
    # Read image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh)
    
    # Save processed image
    processed_path = image_path.replace('.png', '_processed.png')
    cv2.imwrite(processed_path, denoised)
    
    return processed_path

# Usage
processed_image = preprocess_image_for_ocr("document.png")
result = upload_local_image(processed_image, "user123")
```

### 2. Batch Processing with Progress Tracking

```python
from tqdm import tqdm
import concurrent.futures

def batch_process_with_progress(image_paths, user_id, max_workers=3):
    """Process multiple images with progress tracking"""
    
    results = []
    
    with tqdm(total=len(image_paths), desc="Processing images") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(upload_local_image, path, user_id): path 
                for path in image_paths
            }
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    result = future.result()
                    results.append((path, result))
                except Exception as e:
                    results.append((path, {"error": str(e)}))
                
                pbar.update(1)
    
    return results

# Usage
image_paths = ["doc1.png", "doc2.png", "doc3.png"]
results = batch_process_with_progress(image_paths, "user123")
```

### 3. Text Post-processing

```python
import re
from typing import List, Dict

def post_process_ocr_results(results: List[Dict]) -> List[Dict]:
    """Clean and enhance OCR results"""
    
    processed_results = []
    
    for result in results:
        text = result["text"]
        confidence = result["confidence"]
        
        # Clean text
        cleaned_text = clean_text(text)
        
        # Only keep results with reasonable confidence
        if confidence > 0.5 and cleaned_text.strip():
            processed_results.append({
                **result,
                "text": cleaned_text,
                "original_text": text
            })
    
    return processed_results

def clean_text(text: str) -> str:
    """Clean OCR text output"""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common OCR artifacts
    text = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', text)
    
    # Fix common OCR mistakes
    text = text.replace('0', 'O')  # Common mistake
    text = text.replace('1', 'I')  # Common mistake
    
    return text.strip()

# Usage
raw_results = safe_ocr_request("image.png", "user123")
if raw_results:
    processed_results = post_process_ocr_results(raw_results["results"])
    print("Processed results:", processed_results)
```

### 4. Integration with External Services

```python
import json
from datetime import datetime

def save_results_to_database(results, user_id, source_type="image"):
    """Save OCR results to external database"""
    
    # This is a placeholder - implement your database logic
    record = {
        "user_id": user_id,
        "source_type": source_type,
        "timestamp": datetime.utcnow().isoformat(),
        "results": results,
        "total_text_blocks": len(results.get("results", [])),
        "average_confidence": sum(
            r["confidence"] for r in results.get("results", [])
        ) / len(results.get("results", [])) if results.get("results") else 0
    }
    
    # Save to your database here
    print(f"Saving record: {json.dumps(record, indent=2)}")
    return record

def integrate_with_cloud_storage(image_path, user_id):
    """Upload image to cloud storage, then process with OCR"""
    
    # Upload to cloud storage (placeholder)
    cloud_url = upload_to_cloud_storage(image_path)
    
    # Process with OCR
    result = safe_ocr_request(cloud_url, user_id)
    
    # Save results
    if result:
        save_results_to_database(result, user_id)
    
    return result

# Placeholder function
def upload_to_cloud_storage(image_path):
    """Upload image to cloud storage and return URL"""
    # Implement your cloud storage upload logic
    return f"https://your-cloud-storage.com/{image_path}"
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Low OCR Accuracy

**Symptoms**: Poor text recognition, missing characters, wrong words

**Solutions**:
- Use higher resolution images (300+ DPI)
- Improve image contrast and lighting
- Choose correct language
- Pre-process images (denoise, enhance contrast)
- Try multiple languages for complex documents

#### 2. Slow Processing

**Symptoms**: Long response times, timeouts

**Solutions**:
- Reduce image size (compress before sending)
- Process images in smaller batches
- Check network connectivity
- Use appropriate image formats (PNG for screenshots, JPEG for photos)

#### 3. Rate Limiting Issues

**Symptoms**: 429 errors, quota exceeded messages

**Solutions**:
- Monitor usage with `check_monthly_usage()`
- Use multiple user IDs for high-volume processing
- Implement proper retry logic with delays
- Consider upgrading quota limits

#### 4. Network Errors

**Symptoms**: Connection timeouts, network unreachable

**Solutions**:
- Check internet connectivity
- Verify API endpoint URL
- Implement retry logic with exponential backoff
- Use appropriate timeouts

#### 5. File Format Issues

**Symptoms**: 400 errors, unsupported format messages

**Solutions**:
- Use supported formats: PNG, JPEG, JPG, BMP, TIFF
- Convert unsupported formats before sending
- Check file integrity
- Ensure files are not corrupted

### Debugging Tools

```python
def debug_ocr_request(image_path, user_id, language="en"):
    """Debug OCR request with detailed logging"""
    
    print(f"=== OCR Debug Session ===")
    print(f"Image: {image_path}")
    print(f"User ID: {user_id}")
    print(f"Language: {language}")
    
    # Check file
    import os
    if os.path.exists(image_path):
        file_size = os.path.getsize(image_path)
        print(f"File size: {file_size} bytes")
    else:
        print("❌ File not found!")
        return None
    
    # Check usage
    usage = check_monthly_usage(user_id)
    print(f"Current usage: {usage}/20")
    
    # Make request
    try:
        result = upload_local_image(image_path, user_id, language)
        
        if result:
            print("✅ OCR successful!")
            print(f"Extracted {len(result['results'])} text blocks")
            
            for i, block in enumerate(result['results']):
                print(f"Block {i+1}: '{block['text']}' (confidence: {block['confidence']:.2f})")
        else:
            print("❌ OCR failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return result

# Usage
debug_ocr_request("problematic_image.png", "user123", "en")
```

### Performance Monitoring

```python
import time
import psutil
import threading

class PerformanceMonitor:
    def __init__(self):
        self.start_time = None
        self.memory_usage = []
        self.cpu_usage = []
    
    def start(self):
        self.start_time = time.time()
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop(self):
        if self.start_time:
            duration = time.time() - self.start_time
            avg_memory = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
            avg_cpu = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
            
            print(f"Performance Summary:")
            print(f"Duration: {duration:.2f}s")
            print(f"Avg Memory: {avg_memory:.1f}MB")
            print(f"Avg CPU: {avg_cpu:.1f}%")
    
    def _monitor_resources(self):
        while self.start_time:
            process = psutil.Process()
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
            self.cpu_usage.append(process.cpu_percent())
            time.sleep(0.1)

# Usage
monitor = PerformanceMonitor()
monitor.start()

# Your OCR processing here
result = safe_ocr_request("large_image.png", "user123")

monitor.stop()
```

---

## Conclusion

This user guide provides comprehensive information for using the OCR API effectively. Remember to:

1. **Start simple** with basic requests
2. **Monitor your usage** to avoid quota limits
3. **Implement proper error handling** in your applications
4. **Use best practices** for image preparation and processing
5. **Test thoroughly** before deploying to production

For additional support, refer to the API documentation and interactive docs at `http://localhost:8000/docs`. 