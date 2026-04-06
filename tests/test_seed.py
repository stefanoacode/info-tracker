import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models import Category, Person
from backend.seed import seed_database


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_seed_creates_categories(db):
    seed_database(db)
    categories = db.query(Category).all()
    names = {c.name for c in categories}
    assert "Builders" in names
    assert "Researchers" in names
    assert "Founders" in names
    assert "Investors" in names
    assert "Commentators" in names


def test_seed_creates_people(db):
    seed_database(db)
    people = db.query(Person).all()
    assert len(people) > 0
    names = {p.name for p in people}
    assert "Andrej Karpathy" in names


def test_seed_is_idempotent(db):
    seed_database(db)
    count_first = db.query(Person).count()
    seed_database(db)
    count_second = db.query(Person).count()
    assert count_first == count_second
