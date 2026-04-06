from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.services.digest import build_digest

router = APIRouter()

@router.get("/digest")
def get_digest(category: str | None = None, days: int = 1, db: Session = Depends(get_db)):
    return build_digest(db, category=category, days=days)
