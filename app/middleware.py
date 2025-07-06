from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .database import SessionLocal
from .models import APICallHistory

MONTHLY_QUOTA = 20

class QuotaMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/health"]:
            return await call_next(request)
        user_id = None
        if request.method == "POST":
            body = await request.json()
            user_id = body.get("user_id")
        elif request.method == "GET" and "user_id" in request.path_params:
            user_id = request.path_params["user_id"]
        if not user_id:
            return await call_next(request)
        db: Session = SessionLocal()
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        count = db.query(APICallHistory).filter(
            APICallHistory.user_id == user_id,
            APICallHistory.timestamp >= month_start
        ).count()
        db.close()
        if count >= MONTHLY_QUOTA:
            return JSONResponse(status_code=429, content={"detail": "Monthly quota exceeded (20 requests)"})
        return await call_next(request) 