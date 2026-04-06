from sqlalchemy.orm import Session
from backend.models.category import Category
from backend.models.content import Content
from backend.models.person import Person

def build_digest(db: Session, category: str | None = None, days: int = 1) -> dict:
    query = db.query(Content).join(Person).join(Category).filter(Content.ai_summary.isnot(None))
    if category:
        query = query.filter(Category.name == category)
    contents = query.order_by(Content.published_at.desc().nullslast()).limit(50).all()
    items = [{"person_name": c.person.name, "category_name": c.person.category.name, "source_platform": c.source_platform, "original_url": c.original_url, "so_what": c.so_what, "ai_summary": c.ai_summary, "topics": c.topics or [], "published_at": c.published_at.isoformat() if c.published_at else None} for c in contents]
    return {"items": items, "count": len(items)}
