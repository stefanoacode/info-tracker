from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Config(Base):
    __tablename__ = "config"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(500), nullable=False)


def get_config(db, key: str, default: str = "") -> str:
    row = db.query(Config).get(key)
    return row.value if row else default


def set_config(db, key: str, value: str) -> None:
    row = db.query(Config).get(key)
    if row:
        row.value = value
    else:
        db.add(Config(key=key, value=value))
    db.commit()
