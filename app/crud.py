from sqlalchemy.orm import Session
from . import models

def get_or_create_user(db: Session, user_id: str):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        user = models.User(user_id=user_id, api_calls=0)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def increment_api_calls(db: Session, user):
    user.api_calls += 1
    db.commit()
    db.refresh(user)

def log_api_call(db: Session, user_id: str, endpoint: str):
    call = models.APICallHistory(user_id=user_id, endpoint=endpoint)
    db.add(call)
    db.commit()

def create_ocr_job(db: Session, user, input_type: str, input_path: str, language: str, result):
    job = models.OCRJob(user_id=user.id, input_type=input_type, input_path=input_path, language=language, result=result)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_user_history(db: Session, user_id: str):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        return []
    return db.query(models.OCRJob).filter(models.OCRJob.user_id == user.id).order_by(models.OCRJob.created_at.desc()).all() 