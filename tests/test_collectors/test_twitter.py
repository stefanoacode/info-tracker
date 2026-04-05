import pytest
from unittest.mock import patch, AsyncMock
from backend.collectors.twitter import TwitterCollector

SAMPLE_TWEETS_RESPONSE = {
    "data": [
        {"id": "1234567890", "text": "Fine-tuning is all you need for most production use cases. Don't overthink it.", "created_at": "2026-04-05T10:00:00.000Z"},
        {"id": "1234567891", "text": "Just shipped a new feature using Claude. The code quality is impressive.", "created_at": "2026-04-04T15:30:00.000Z"},
    ]
}

@pytest.fixture
def collector():
    return TwitterCollector(bearer_token="test-token")

@pytest.mark.asyncio
async def test_twitter_collect_parses_tweets(collector):
    with patch("backend.collectors.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.json.return_value = SAMPLE_TWEETS_RESPONSE
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client
        items = await collector.collect("karpathy")
        assert len(items) == 2
        assert items[0].source_platform == "x"
        assert "Fine-tuning" in items[0].raw_text
        assert "x.com" in items[0].original_url

@pytest.mark.asyncio
async def test_twitter_collect_returns_empty_without_token():
    collector = TwitterCollector(bearer_token="")
    items = await collector.collect("karpathy")
    assert items == []
