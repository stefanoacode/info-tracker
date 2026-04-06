from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from backend.config import settings


class Base(DeclarativeBase):
    pass


def get_engine(url: str | None = None):
    db_url = url or settings.database_url
    return create_engine(db_url, echo=False)


def get_db(url: str | None = None) -> Session:
    """Get a database session. Creates tables and seeds on first use."""
    engine = get_engine(url)
    Base.metadata.create_all(engine)
    return Session(engine)


def ensure_data_dir():
    """Ensure the data directory exists for SQLite."""
    Path(settings.database_url.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)
