from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import base64
import requests
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models, crud, ocr, pdf_utils, schemas
from .middleware import QuotaMiddleware

app = FastAPI(title="OCR API", description="Free OCR API for text extraction from images and PDFs")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(QuotaMiddleware)

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/extract-text", response_model=schemas.ExtractTextResponse)
def extract_text(request: schemas.ExtractTextRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not (request.image_base64 or request.image_url):
        raise HTTPException(status_code=400, detail="Provide image_base64 or image_url")
    # Save image
    image_path = os.path.join(UPLOAD_DIR, f"img_{request.user_id}.png")
    if request.image_base64:
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(request.image_base64))
    else:
        resp = requests.get(request.image_url)
        with open(image_path, "wb") as f:
            f.write(resp.content)
    # OCR
    results = ocr.extract_text(image_path, request.language)
    crud.log_api_call(db, request.user_id, "/extract-text")
    user = crud.get_or_create_user(db, request.user_id)
    crud.increment_api_calls(db, user)
    crud.create_ocr_job(db, user, "image", image_path, request.language, results)
    return {"results": results}

@app.post("/upload-pdf", response_model=schemas.UploadPDFResponse)
def upload_pdf(user_id: str, file: UploadFile = File(...), language: str = "en", db: Session = Depends(get_db)):
    pdf_path = os.path.join(UPLOAD_DIR, f"pdf_{user_id}.pdf")
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    image_paths = pdf_utils.pdf_to_images(pdf_path, UPLOAD_DIR)
    pages = {}
    for idx, img_path in enumerate(image_paths, 1):
        results = ocr.extract_text(img_path, language)
        pages[idx] = results
    crud.log_api_call(db, user_id, "/upload-pdf")
    user = crud.get_or_create_user(db, user_id)
    crud.increment_api_calls(db, user)
    crud.create_ocr_job(db, user, "pdf", pdf_path, language, pages)
    return {"pages": pages}

@app.get("/history/{user_id}", response_model=schemas.HistoryResponse)
def get_history(user_id: str, db: Session = Depends(get_db)):
    jobs = crud.get_user_history(db, user_id)
    history = []
    for job in jobs:
        history.append({
            "id": job.id,
            "input_type": job.input_type,
            "input_path": job.input_path,
            "language": job.language,
            "result": job.result,
            "created_at": job.created_at
        })
    crud.log_api_call(db, user_id, "/history")
    return {"history": history} 