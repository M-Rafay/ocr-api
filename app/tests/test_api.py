import base64
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from app import models

# Create tables for testing
models.Base.metadata.create_all(bind=engine)

client = TestClient(app)

TEST_USER = "testuser"

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_extract_text():
    # Use a small black image as dummy
    img_path = os.path.join(os.path.dirname(__file__), "black.png")
    if not os.path.exists(img_path):
        import cv2
        import numpy as np
        cv2.imwrite(img_path, np.zeros((10,10,3), dtype=np.uint8))
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    resp = client.post("/extract-text", json={
        "image_base64": img_b64,
        "user_id": TEST_USER,
        "language": "en"
    })
    assert resp.status_code == 200
    assert "results" in resp.json()

def test_upload_pdf():
    # Create a dummy PDF
    from fpdf import FPDF
    pdf_path = os.path.join(os.path.dirname(__file__), "dummy.pdf")
    if not os.path.exists(pdf_path):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Test PDF", ln=True)
        pdf.output(pdf_path)
    with open(pdf_path, "rb") as f:
        resp = client.post("/upload-pdf", data={"user_id": TEST_USER}, files={"file": ("dummy.pdf", f, "application/pdf")})
    assert resp.status_code == 200
    assert "pages" in resp.json()

def test_history():
    resp = client.get(f"/history/{TEST_USER}")
    assert resp.status_code == 200
    assert "history" in resp.json() 