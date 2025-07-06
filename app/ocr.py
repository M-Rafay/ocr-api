import easyocr
import cv2
import numpy as np
from typing import List, Dict
import os

# Supported languages for EasyOCR
SUPPORTED_LANGUAGES = ["en", "ur", "ar"]

reader_cache = {}

def get_reader(lang: str):
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    if lang not in reader_cache:
        try:
            reader_cache[lang] = easyocr.Reader([lang], gpu=False)
        except Exception as e:
            print(f"Error initializing EasyOCR reader for {lang}: {e}")
            # Fallback to English
            reader_cache[lang] = easyocr.Reader(["en"], gpu=False)
    return reader_cache[lang]

def preprocess_image(image_path: str) -> np.ndarray:
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
        
        # Threshold
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    except Exception as e:
        print(f"Error in image preprocessing: {e}")
        # Return original image if preprocessing fails
        img = cv2.imread(image_path)
        if img is not None:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        raise e

def extract_text(image_path: str, lang: str = "en") -> List[Dict]:
    try:
        reader = get_reader(lang)
        processed_img = preprocess_image(image_path)
        
        # EasyOCR expects file path or numpy array
        results = reader.readtext(processed_img)
        
        extracted = []
        for (bbox, text, conf) in results:
            extracted.append({
                "text": text,
                "confidence": conf,
                "bbox": bbox
            })
        
        return extracted
    except Exception as e:
        print(f"Error in text extraction: {e}")
        return [] 