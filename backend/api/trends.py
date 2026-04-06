from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.trend import Trend

router = APIRouter()

class TrendResponse(BaseModel):
    id: int
    topic: str
    description: str
    related_content_ids: list[int]
    detected_at: datetime
    time_range: str
    sentiment_score: float
    momentum_score: float
    model_config = {"from_attributes": True}

@router.get("/trends", response_model=list[TrendResponse])
def get_trends(time_range: str | None = None, limit: int = Query(default=20, le=50), db: Session = Depends(get_db)):
    query = db.query(Trend)
    if time_range:
        query = query.filter(Trend.time_range == time_range)
    return query.order_by(Trend.momentum_score.desc()).limit(limit).all()
