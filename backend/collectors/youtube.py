import logging
from datetime import datetime, timezone

import httpx
from youtube_transcript_api import YouTubeTranscriptApi

from backend.collectors.base import BaseCollector, CollectedItem

logger = logging.getLogger(__name__)
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


class YouTubeCollector(BaseCollector):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def collect(self, handle: str) -> list[CollectedItem]:
        if not self.api_key:
            logger.warning("YouTube API key not configured, skipping collection")
            return []
        try:
            params = {
                "key": self.api_key,
                "channelId": handle,
                "part": "snippet",
                "order": "date",
                "maxResults": 10,
                "type": "video",
            }
            async with httpx.AsyncClient() as client:
                response = await client.get(YOUTUBE_SEARCH_URL, params=params, timeout=30.0)
                response.raise_for_status()
            data = await response.json()
            items = []
            for video in data.get("items", []):
                video_id = video["id"]["videoId"]
                snippet = video["snippet"]
                title = snippet.get("title", "")
                published_at = None
                if "publishedAt" in snippet:
                    published_at = datetime.fromisoformat(
                        snippet["publishedAt"].replace("Z", "+00:00")
                    )
                transcript_text = ""
                try:
                    ytt_api = YouTubeTranscriptApi()
                    transcript = ytt_api.fetch(video_id)
                    parts = transcript.to_raw_data()
                    transcript_text = " ".join(part["text"] for part in parts)
                except Exception as e:
                    logger.debug(f"No transcript for {video_id}: {e}")
                raw_text = f"{title}\n\n{transcript_text}" if transcript_text else title
                items.append(CollectedItem(
                    source_platform="youtube",
                    original_url=f"https://www.youtube.com/watch?v={video_id}",
                    raw_text=raw_text,
                    published_at=published_at,
                ))
            return items
        except Exception as e:
            logger.warning(f"YouTube collection failed for {handle}: {e}")
            return []

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    YOUTUBE_SEARCH_URL,
                    params={"key": self.api_key, "part": "snippet", "q": "test", "maxResults": 1},
                    timeout=10.0,
                )
                return resp.status_code == 200
        except Exception:
            return False
