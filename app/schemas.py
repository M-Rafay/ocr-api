from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict

class ExtractTextRequest(BaseModel):
    image_base64: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    language: Optional[str] = Field(default="en", description="Language code (en, ur, ar)")
    user_id: str

class ExtractedTextBox(BaseModel):
    text: str
    confidence: float
    bbox: List[List[float]]

class ExtractTextResponse(BaseModel):
    results: List[ExtractedTextBox]

class UploadPDFResponse(BaseModel):
    pages: Dict[int, List[ExtractedTextBox]]

class HistoryResponse(BaseModel):
    history: List[Dict] 