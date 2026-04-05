import pytest
from unittest.mock import AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from backend.database import Base
from backend.models import Category, Person, Content
from backend.services.summarizer import SummarizerService

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        cat = Category(name="Builders", sort_order=1)
        session.add(cat)
        session.commit()
        person = Person(name="Karpathy", category_id=cat.id, platform_handles={"x": "karpathy"})
        session.add(person)
        session.commit()
        content = Content(person_id=person.id, source_platform="x", original_url="https://x.com/karpathy/status/123", raw_text="Fine-tuning is all you need for most production use cases. Don't overthink it.")
        session.add(content)
        session.commit()
        yield session
    Base.metadata.drop_all(engine)

@pytest.mark.asyncio
async def test_summarize_unsummarized_content(db):
    mock_llm = AsyncMock()
    mock_llm.summarize.return_value = "**So what:** Fine-tuning beats prompting for production.\n\n- Simple and effective\n- Most teams overthink this"
    mock_llm.extract_topics.return_value = ["fine-tuning", "llm", "production"]
    service = SummarizerService(llm=mock_llm)
    count = await service.summarize_pending(db)
    assert count == 1
    content = db.query(Content).first()
    assert content.ai_summary is not None
    assert "So what" in content.ai_summary
    assert content.so_what is not None
    assert len(content.topics) > 0

@pytest.mark.asyncio
async def test_summarize_skips_already_summarized(db):
    content = db.query(Content).first()
    content.ai_summary = "Already done"
    content.so_what = "Already extracted"
    db.commit()
    mock_llm = AsyncMock()
    service = SummarizerService(llm=mock_llm)
    count = await service.summarize_pending(db)
    assert count == 0
    mock_llm.summarize.assert_not_called()
