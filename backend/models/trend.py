from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Trend(Base):
    __tablename__ = "trends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    related_content_ids: Mapped[list] = mapped_column(JSON, default=list)
    detected_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    time_range: Mapped[str] = mapped_column(String(10), default="7d")
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    momentum_score: Mapped[float] = mapped_column(Float, default=0.0)
