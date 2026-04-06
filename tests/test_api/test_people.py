import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import Session, sessionmaker
from backend.database import Base, get_db
from backend.main import app
from backend.seed import seed_database

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
    seed_database(session)
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

def test_list_categories(client):
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    names = {c["name"] for c in data}
    assert "Builders" in names

def test_list_people(client):
    resp = client.get("/api/people")
    assert resp.status_code == 200
    assert len(resp.json()) > 0

def test_list_people_by_category(client):
    resp = client.get("/api/people?category=Builders")
    assert resp.status_code == 200
    assert all(p["category_name"] == "Builders" for p in resp.json())

def test_add_person(client):
    resp = client.post("/api/people", json={"name": "New Person", "bio": "A new person to track", "category_name": "Investors", "platform_handles": {"x": "newperson"}})
    assert resp.status_code == 201
    assert resp.json()["name"] == "New Person"
    assert resp.json()["is_custom"] is True

def test_delete_person(client):
    resp = client.post("/api/people", json={"name": "Temporary", "category_name": "Builders", "platform_handles": {}})
    person_id = resp.json()["id"]
    resp = client.delete(f"/api/people/{person_id}")
    assert resp.status_code == 204
