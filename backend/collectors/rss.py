import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from backend.collectors.base import BaseCollector, CollectedItem

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    async def collect(self, handle: str) -> list[CollectedItem]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(handle, timeout=30.0)
                response.raise_for_status()
            feed = feedparser.parse(response.text)
            items = []
            for entry in feed.entries:
                published_at = None
                if hasattr(entry, "published"):
                    try:
                        published_at = parsedate_to_datetime(entry.published)
                    except (ValueError, TypeError):
                        pass
                title = getattr(entry, "title", "")
                description = getattr(entry, "description", "")
                raw_text = f"{title}\n\n{description}" if title else description
                items.append(CollectedItem(
                    source_platform="substack",
                    original_url=getattr(entry, "link", ""),
                    raw_text=raw_text,
                    published_at=published_at,
                ))
            return items
        except Exception as e:
            logger.warning(f"RSS collection failed for {handle}: {e}")
            return []

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://simonwillison.net/atom/everything/", timeout=10.0
                )
                return resp.status_code == 200
        except Exception:
            return False
