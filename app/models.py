from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    api_calls = Column(Integer, default=0)
    jobs = relationship("OCRJob", back_populates="user")

class OCRJob(Base):
    __tablename__ = "ocr_jobs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    input_type = Column(String)  # image or pdf
    input_path = Column(String)
    language = Column(String)
    result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="jobs")

class APICallHistory(Base):
    __tablename__ = "api_call_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    endpoint = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now()) 