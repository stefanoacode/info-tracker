from datetime import datetime
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.category import Category
from backend.models.content import Content
from backend.models.person import Person

router = APIRouter()

class FeedItem(BaseModel):
    id: int
    person_name: str
    person_id: int
    category_name: str
    source_platform: str
    original_url: str
    ai_summary: str | None
    so_what: str | None
    topics: list[str]
    published_at: datetime | None
    collected_at: datetime
    is_read: bool
    model_config = {"from_attributes": True}

@router.get("/feed", response_model=list[FeedItem])
def get_feed(category: str | None = None, platform: str | None = None, person_id: int | None = None, topic: str | None = None, limit: int = Query(default=50, le=200), offset: int = Query(default=0, ge=0), db: Session = Depends(get_db)):
    query = db.query(Content).join(Person).join(Category)
    if category:
        query = query.filter(Category.name == category)
    if platform:
        query = query.filter(Content.source_platform == platform)
    if person_id:
        query = query.filter(Content.person_id == person_id)
    query = query.order_by(Content.published_at.desc().nullslast())
    contents = query.offset(offset).limit(limit).all()
    return [FeedItem(id=c.id, person_name=c.person.name, person_id=c.person_id, category_name=c.person.category.name, source_platform=c.source_platform, original_url=c.original_url, ai_summary=c.ai_summary, so_what=c.so_what, topics=c.topics or [], published_at=c.published_at, collected_at=c.collected_at, is_read=c.is_read) for c in contents]

@router.patch("/feed/{content_id}/read")
def mark_as_read(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).get(content_id)
    if not content:
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    content.is_read = True
    db.commit()
    return {"status": "ok"}

@router.post("/collect/refresh")
async def refresh_collection(db: Session = Depends(get_db)):
    from backend.scheduler import _get_collectors
    from backend.services.collector_service import CollectorService
    service = CollectorService(collectors=_get_collectors())
    new_content = await service.collect_all(db)
    return {"new_items": len(new_content)}
