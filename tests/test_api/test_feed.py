import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session, sessionmaker
from backend.database import Base, get_db
from backend.main import app
from backend.models import Category, Person, Content

@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    cat = Category(name="Builders", sort_order=1)
    session.add(cat)
    session.commit()
    person = Person(name="Karpathy", category_id=cat.id, platform_handles={"x": "karpathy"})
    session.add(person)
    session.commit()
    for i in range(3):
        session.add(Content(person_id=person.id, source_platform="x", original_url=f"https://x.com/karpathy/status/{i}", raw_text=f"Post {i} about AI", ai_summary=f"**So what:** Point {i}\n\n- Detail", so_what=f"Point {i}", topics=["ai", "llm"], published_at=datetime(2026, 4, 5 - i, tzinfo=timezone.utc)))
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_get_feed(client):
    resp = client.get("/api/feed")
    assert resp.status_code == 200
    assert len(resp.json()) == 3
    assert resp.json()[0]["so_what"] == "Point 0"

def test_get_feed_filter_by_category(client):
    resp = client.get("/api/feed?category=Builders")
    assert resp.status_code == 200
    assert len(resp.json()) == 3

def test_get_feed_filter_by_platform(client):
    resp = client.get("/api/feed?platform=x")
    assert len(resp.json()) == 3
    resp = client.get("/api/feed?platform=youtube")
    assert len(resp.json()) == 0

def test_get_feed_pagination(client):
    resp = client.get("/api/feed?limit=2&offset=0")
    assert len(resp.json()) == 2
