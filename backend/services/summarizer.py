import logging
import re
from sqlalchemy.orm import Session
from backend.llm.base import LLMProvider
from backend.models.content import Content

logger = logging.getLogger(__name__)

def _extract_so_what(summary: str) -> str:
    match = re.search(r"\*\*So what:\*\*\s*(.+?)(?:\n|$)", summary)
    if match:
        return match.group(1).strip()
    for line in summary.split("\n"):
        line = line.strip()
        if line and not line.startswith("-") and not line.startswith("#"):
            return line
    return ""

class SummarizerService:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def summarize_pending(self, db: Session) -> int:
        pending = db.query(Content).filter(Content.ai_summary.is_(None)).all()
        count = 0
        for content in pending:
            try:
                summary = await self.llm.summarize(content.raw_text)
                topics = await self.llm.extract_topics(content.raw_text)
                content.ai_summary = summary
                content.so_what = _extract_so_what(summary)
                content.topics = topics
                count += 1
            except Exception as e:
                logger.error(f"Summarization failed for content {content.id}: {e}")
        db.commit()
        return count
