import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models import Category, Person, Content
from backend.collectors.base import CollectedItem
from backend.services.collector_service import CollectorService

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        cat = Category(name="Builders", sort_order=1)
        session.add(cat)
        session.commit()
        person = Person(name="Simon Willison", category_id=cat.id, platform_handles={"substack": "https://simonwillison.net/atom/everything/", "reddit": "simonw"})
        session.add(person)
        session.commit()
        yield session
    Base.metadata.drop_all(engine)

@pytest.mark.asyncio
async def test_collect_for_person(db):
    mock_rss = AsyncMock()
    mock_rss.collect.return_value = [CollectedItem(source_platform="substack", original_url="https://example.com/post/1", raw_text="New blog post about AI", published_at=datetime(2026, 4, 5, tzinfo=timezone.utc))]
    mock_reddit = AsyncMock()
    mock_reddit.collect.return_value = [CollectedItem(source_platform="reddit", original_url="https://reddit.com/r/ml/comment/1", raw_text="Interesting comment about LLMs", published_at=datetime(2026, 4, 4, tzinfo=timezone.utc))]
    service = CollectorService(collectors={"substack": mock_rss, "reddit": mock_reddit})
    person = db.query(Person).first()
    new_content = await service.collect_for_person(db, person)
    assert len(new_content) == 2
    assert db.query(Content).count() == 2

@pytest.mark.asyncio
async def test_collect_skips_duplicates(db):
    mock_rss = AsyncMock()
    item = CollectedItem(source_platform="substack", original_url="https://example.com/post/1", raw_text="Blog post")
    mock_rss.collect.return_value = [item]
    service = CollectorService(collectors={"substack": mock_rss})
    person = db.query(Person).first()
    await service.collect_for_person(db, person)
    await service.collect_for_person(db, person)
    assert db.query(Content).count() == 1
