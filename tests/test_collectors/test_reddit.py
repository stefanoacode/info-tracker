import pytest
from unittest.mock import patch, AsyncMock

from backend.collectors.reddit import RedditCollector

SAMPLE_REDDIT_JSON = {
    "data": {
        "children": [
            {"kind": "t1", "data": {"body": "I think agents are overhyped right now. Most production use cases still need RAG.", "permalink": "/r/MachineLearning/comments/abc123/comment/def456/", "created_utc": 1743850000.0, "subreddit": "MachineLearning"}},
            {"kind": "t1", "data": {"body": "Fine-tuning Llama 3 on domain data works surprisingly well.", "permalink": "/r/LocalLLaMA/comments/xyz789/comment/ghi012/", "created_utc": 1743760000.0, "subreddit": "LocalLLaMA"}},
        ]
    }
}

@pytest.fixture
def collector():
    return RedditCollector()

@pytest.mark.asyncio
async def test_reddit_collect_parses_comments(collector):
    with patch("backend.collectors.reddit.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.json.return_value = SAMPLE_REDDIT_JSON
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client
        items = await collector.collect("karpathy")
        assert len(items) == 2
        assert items[0].source_platform == "reddit"
        assert "agents" in items[0].raw_text.lower()
        assert "reddit.com" in items[0].original_url

@pytest.mark.asyncio
async def test_reddit_collect_returns_empty_on_failure(collector):
    with patch("backend.collectors.reddit.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=Exception("Network error"))
        mock_client_cls.return_value = mock_client
        items = await collector.collect("someuser")
        assert items == []
