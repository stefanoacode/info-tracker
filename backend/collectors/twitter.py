import logging
from datetime import datetime, timezone

import httpx

from backend.collectors.base import BaseCollector, CollectedItem

logger = logging.getLogger(__name__)
TWITTER_USER_LOOKUP_URL = "https://api.x.com/2/users/by/username/{username}"
TWITTER_USER_TWEETS_URL = "https://api.x.com/2/users/{user_id}/tweets"


class TwitterCollector(BaseCollector):
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token

    async def collect(self, handle: str) -> list[CollectedItem]:
        if not self.bearer_token:
            logger.warning("X API bearer token not configured, skipping collection")
            return []
        try:
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            async with httpx.AsyncClient() as client:
                user_resp = await client.get(
                    TWITTER_USER_LOOKUP_URL.format(username=handle),
                    headers=headers,
                    timeout=30.0,
                )
                user_resp.raise_for_status()
                user_data = await user_resp.json()
                raw_user = user_data["data"]
                user_id = raw_user["id"] if isinstance(raw_user, dict) else raw_user[0]["id"]
                tweets_resp = await client.get(
                    TWITTER_USER_TWEETS_URL.format(user_id=user_id),
                    headers=headers,
                    params={"max_results": 10, "tweet.fields": "created_at"},
                    timeout=30.0,
                )
                tweets_resp.raise_for_status()
                data = await tweets_resp.json()
            items = []
            for tweet in data.get("data", []):
                published_at = None
                if "created_at" in tweet:
                    published_at = datetime.fromisoformat(
                        tweet["created_at"].replace("Z", "+00:00")
                    )
                items.append(CollectedItem(
                    source_platform="x",
                    original_url=f"https://x.com/{handle}/status/{tweet['id']}",
                    raw_text=tweet["text"],
                    published_at=published_at,
                ))
            return items
        except Exception as e:
            logger.warning(f"Twitter collection failed for {handle}: {e}")
            return []

    async def health_check(self) -> bool:
        if not self.bearer_token:
            return False
        try:
            headers = {"Authorization": f"Bearer {self.bearer_token}"}
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.x.com/2/users/me",
                    headers=headers,
                    timeout=10.0,
                )
                return resp.status_code == 200
        except Exception:
            return False
