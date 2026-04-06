import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from backend.collectors.youtube import YouTubeCollector

SAMPLE_SEARCH_RESPONSE = {
    "items": [
        {"id": {"videoId": "abc123"}, "snippet": {"title": "The State of AI Agents in 2026", "publishedAt": "2026-04-01T10:00:00Z"}},
        {"id": {"videoId": "def456"}, "snippet": {"title": "Fine-tuning vs Prompting", "publishedAt": "2026-03-28T10:00:00Z"}},
    ]
}

@pytest.fixture
def collector():
    return YouTubeCollector(api_key="test-key")

@pytest.mark.asyncio
async def test_youtube_collect_fetches_videos(collector):
    with patch("backend.collectors.youtube.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.json.return_value = SAMPLE_SEARCH_RESPONSE
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client
        with patch("backend.collectors.youtube.YouTubeTranscriptApi") as mock_transcript:
            mock_fetcher = MagicMock()
            mock_transcript.return_value = mock_fetcher
            mock_fetcher.fetch.return_value.to_raw_data.return_value = [
                {"text": "Welcome to the video about AI agents."},
                {"text": "Today we discuss the future."},
            ]
            items = await collector.collect("UCsBjURrPoezykLs9EqgamOA")
            assert len(items) == 2
            assert items[0].source_platform == "youtube"
            assert "abc123" in items[0].original_url
            assert "AI agents" in items[0].raw_text.lower() or "State of AI" in items[0].raw_text

@pytest.mark.asyncio
async def test_youtube_collect_returns_empty_without_api_key():
    collector = YouTubeCollector(api_key="")
    items = await collector.collect("some-channel")
    assert items == []
