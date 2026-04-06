import logging
from datetime import datetime, timezone

import httpx

from backend.collectors.base import BaseCollector, CollectedItem

logger = logging.getLogger(__name__)
REDDIT_USER_COMMENTS_URL = "https://www.reddit.com/user/{username}/comments.json"


class RedditCollector(BaseCollector):
    async def collect(self, handle: str) -> list[CollectedItem]:
        try:
            url = REDDIT_USER_COMMENTS_URL.format(username=handle)
            headers = {"User-Agent": "InfoTracker/0.1"}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
            data = await response.json()
            items = []
            for child in data.get("data", {}).get("children", []):
                comment = child.get("data", {})
                body = comment.get("body", "")
                permalink = comment.get("permalink", "")
                created_utc = comment.get("created_utc", 0)
                subreddit = comment.get("subreddit", "")
                published_at = (
                    datetime.fromtimestamp(created_utc, tz=timezone.utc)
                    if created_utc
                    else None
                )
                items.append(CollectedItem(
                    source_platform="reddit",
                    original_url=f"https://www.reddit.com{permalink}",
                    raw_text=f"[r/{subreddit}] {body}" if subreddit else body,
                    published_at=published_at,
                ))
            return items
        except Exception as e:
            logger.warning(f"Reddit collection failed for {handle}: {e}")
            return []

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://www.reddit.com/r/MachineLearning.json",
                    headers={"User-Agent": "InfoTracker/0.1"},
                    timeout=10.0,
                )
                return resp.status_code == 200
        except Exception:
            return False
