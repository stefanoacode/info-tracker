from __future__ import annotations

import logging
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from backend.collectors.base import BaseCollector, CollectedItem

logger = logging.getLogger(__name__)

# Public Nitter instances to try, in order of preference
DEFAULT_NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://xcancel.com",
    "https://nitter.privacyredirect.com",
]


class TwitterCollector(BaseCollector):
    def __init__(self, nitter_instance: str | None = None):
        self.instances = (
            [nitter_instance] if nitter_instance else DEFAULT_NITTER_INSTANCES
        )

    async def collect(self, handle: str) -> list[CollectedItem]:
        """Collect tweets via Nitter RSS. Handle is the X username (without @)."""
        for instance in self.instances:
            url = f"{instance.rstrip('/')}/{handle}/rss"
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    response = await client.get(
                        url,
                        timeout=30.0,
                        headers={"User-Agent": "InfoTracker/0.1"},
                    )
                    if response.status_code != 200:
                        logger.debug(f"Nitter {instance} returned {response.status_code} for {handle}")
                        continue

                feed = feedparser.parse(response.text)
                if not feed.entries:
                    logger.debug(f"Nitter {instance} returned empty feed for {handle}")
                    continue

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
                    raw_text = title if title else description

                    # Nitter links look like /username/status/123 — convert to x.com
                    link = getattr(entry, "link", "")
                    if link and not link.startswith("http"):
                        link = f"https://x.com{link}"
                    elif instance in link:
                        link = link.replace(instance, "https://x.com")

                    items.append(
                        CollectedItem(
                            source_platform="x",
                            original_url=link,
                            raw_text=raw_text,
                            published_at=published_at,
                        )
                    )
                logger.info(f"Collected {len(items)} tweets for @{handle} via {instance}")
                return items

            except Exception as e:
                logger.debug(f"Nitter {instance} failed for {handle}: {e}")
                continue

        logger.warning(f"All Nitter instances failed for @{handle}")
        return []

    async def health_check(self) -> bool:
        for instance in self.instances:
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    resp = await client.get(
                        f"{instance}/jack/rss",
                        headers={"User-Agent": "InfoTracker/0.1"},
                        timeout=10.0,
                    )
                    if resp.status_code == 200:
                        return True
            except Exception:
                continue
        return False
