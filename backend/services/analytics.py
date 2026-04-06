import json
import logging
from sqlalchemy.orm import Session
from backend.llm.base import LLMProvider
from backend.models.content import Content
from backend.models.trend import Trend

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def detect_trends(self, db: Session, time_range: str = "7d") -> list[Trend]:
        contents = db.query(Content).filter(Content.ai_summary.isnot(None)).limit(100).all()
        if not contents:
            return []
        formatted = "\n\n".join(f"[{c.id}] {c.person.name} ({c.source_platform}): {c.ai_summary}" for c in contents)
        try:
            result = await self.llm.analyze_trends(formatted, time_range)
            trends_data = json.loads(result)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Trend analysis failed: {e}")
            return []
        db.query(Trend).filter(Trend.time_range == time_range).delete()
        new_trends = []
        for t in trends_data:
            trend = Trend(topic=t["topic"], description=t["description"], related_content_ids=t.get("related_content_ids", []), time_range=time_range, sentiment_score=t.get("sentiment_score", 0.0), momentum_score=t.get("momentum_score", 0.0))
            db.add(trend)
            new_trends.append(trend)
        db.commit()
        return new_trends
