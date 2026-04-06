from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Content(Base):
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("people.id"), nullable=False)
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    original_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    so_what: Mapped[str | None] = mapped_column(String(500), nullable=True)
    topics: Mapped[list] = mapped_column(JSON, default=list)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    collected_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    person: Mapped["Person"] = relationship("Person", back_populates="contents")
