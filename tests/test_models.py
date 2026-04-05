import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models.category import Category
from backend.models.person import Person
from backend.models.content import Content
from backend.models.trend import Trend


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_create_category(db):
    cat = Category(name="Builders", description="Engineers shipping AI products", sort_order=1)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    assert cat.id is not None
    assert cat.name == "Builders"
    assert cat.is_custom is False


def test_create_person_with_category(db):
    cat = Category(name="Investors", sort_order=1)
    db.add(cat)
    db.commit()

    person = Person(
        name="Elad Gil",
        bio="Investor and author",
        category_id=cat.id,
        platform_handles={"x": "@elogoism", "substack": "https://blog.eladgil.com"},
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    assert person.id is not None
    assert person.category.name == "Investors"
    assert person.platform_handles["x"] == "@elogoism"


def test_create_content(db):
    cat = Category(name="Builders", sort_order=1)
    db.add(cat)
    db.commit()

    person = Person(name="Karpathy", category_id=cat.id, platform_handles={"x": "@karpathy"})
    db.add(person)
    db.commit()

    content = Content(
        person_id=person.id,
        source_platform="x",
        original_url="https://x.com/karpathy/status/123",
        raw_text="Fine-tuning is all you need for most use cases.",
        so_what="Fine-tuning beats prompting for production use cases",
        topics=["fine-tuning", "llm"],
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    assert content.id is not None
    assert content.person.name == "Karpathy"
    assert "fine-tuning" in content.topics


def test_create_trend(db):
    trend = Trend(
        topic="agents",
        description="Agent frameworks gaining momentum across builders and founders",
        related_content_ids=[1, 2, 3],
        time_range="7d",
        sentiment_score=0.7,
        momentum_score=0.85,
    )
    db.add(trend)
    db.commit()
    db.refresh(trend)
    assert trend.id is not None
    assert trend.momentum_score == 0.85
