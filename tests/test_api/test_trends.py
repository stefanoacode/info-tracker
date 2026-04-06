import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_db
from backend.main import app
from backend.models.trend import Trend

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
    session.add(Trend(topic="agents", description="Agent frameworks gaining traction", related_content_ids=[1, 2, 3], time_range="7d", sentiment_score=0.8, momentum_score=0.9))
    session.add(Trend(topic="fine-tuning", description="More teams adopting fine-tuning", related_content_ids=[4, 5], time_range="7d", sentiment_score=0.6, momentum_score=0.5))
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

def test_get_trends(client):
    resp = client.get("/api/trends")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["topic"] == "agents"

def test_get_trends_filter_by_time_range(client):
    resp = client.get("/api/trends?time_range=7d")
    assert len(resp.json()) == 2
