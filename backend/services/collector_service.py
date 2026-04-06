from __future__ import annotations

import logging
from datetime import datetime, timezone

from backend.collectors.base import BaseCollector
from backend.store import get_people, add_content

logger = logging.getLogger(__name__)


class CollectorService:
    def __init__(self, collectors: dict[str, BaseCollector]):
        self.collectors = collectors

    async def collect_for_person(self, person: dict) -> list[dict]:
        new_items = []
        for platform, handle in person.get("platforms", {}).items():
            collector = self.collectors.get(platform)
            if not collector:
                continue
            try:
                items = await collector.collect(handle)
                for item in items:
                    new_items.append({
                        "person": person["name"],
                        "category": person["category"],
                        "platform": item.source_platform,
                        "url": item.original_url,
                        "text": item.raw_text,
                        "date": item.published_at.isoformat() if item.published_at else "",
                    })
            except Exception as e:
                logger.error(f"Collection failed for {person['name']} on {platform}: {e}")
        return new_items

    async def collect_all(self) -> int:
        people = get_people()
        all_items = []
        for person in people:
            items = await self.collect_for_person(person)
            all_items.extend(items)
        return add_content(all_items)
