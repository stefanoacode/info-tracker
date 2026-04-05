import logging
from sqlalchemy.orm import Session
from backend.collectors.base import BaseCollector, CollectedItem
from backend.models.content import Content
from backend.models.person import Person

logger = logging.getLogger(__name__)

class CollectorService:
    def __init__(self, collectors: dict[str, BaseCollector]):
        self.collectors = collectors

    async def collect_for_person(self, db: Session, person: Person) -> list[Content]:
        new_contents = []
        for platform, handle in person.platform_handles.items():
            collector = self.collectors.get(platform)
            if not collector:
                continue
            try:
                items = await collector.collect(handle)
                for item in items:
                    existing = db.query(Content).filter_by(person_id=person.id, original_url=item.original_url).first()
                    if existing:
                        continue
                    content = Content(person_id=person.id, source_platform=item.source_platform, original_url=item.original_url, raw_text=item.raw_text, published_at=item.published_at)
                    db.add(content)
                    new_contents.append(content)
            except Exception as e:
                logger.error(f"Collection failed for {person.name} on {platform}: {e}")
        db.commit()
        return new_contents

    async def collect_all(self, db: Session) -> list[Content]:
        all_new = []
        for person in db.query(Person).all():
            new = await self.collect_for_person(db, person)
            all_new.extend(new)
        return all_new
