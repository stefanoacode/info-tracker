import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
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
    session.add(Content(person_id=person.id, source_platform="x", original_url="https://x.com/karpathy/status/1", raw_text="Fine-tuning is great", ai_summary="**So what:** Fine-tuning works.\n\n- Simple\n- Effective", so_what="Fine-tuning works", topics=["fine-tuning"], published_at=datetime(2026, 4, 5, tzinfo=timezone.utc)))
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

def test_get_digest(client):
    resp = client.get("/api/digest")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert data["items"][0]["so_what"] is not None

def test_get_digest_by_category(client):
    resp = client.get("/api/digest?category=Builders")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) > 0
