import pytest
from unittest.mock import patch, AsyncMock
from backend.collectors.twitter import TwitterCollector

SAMPLE_NITTER_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>@karpathy</title>
    <item>
      <title>Fine-tuning is all you need for most production use cases. Don't overthink it.</title>
      <link>https://nitter.example.com/karpathy/status/1234567890</link>
      <pubDate>Sat, 05 Apr 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Just shipped a new feature using Claude. The code quality is impressive.</title>
      <link>https://nitter.example.com/karpathy/status/1234567891</link>
      <pubDate>Fri, 04 Apr 2026 15:30:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""


@pytest.fixture
def collector():
    return TwitterCollector(nitter_instance="https://nitter.example.com")


@pytest.mark.asyncio
async def test_twitter_collect_parses_nitter_rss(collector):
    with patch("backend.collectors.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_resp = AsyncMock()
        mock_resp.text = SAMPLE_NITTER_RSS
        mock_resp.status_code = 200
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value = mock_client

        items = await collector.collect("karpathy")
        assert len(items) == 2
        assert items[0].source_platform == "x"
        assert "Fine-tuning" in items[0].raw_text
        assert "x.com" in items[0].original_url


@pytest.mark.asyncio
async def test_twitter_collect_returns_empty_on_failure(collector):
    with patch("backend.collectors.twitter.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=Exception("Network error"))
        mock_client_cls.return_value = mock_client

        items = await collector.collect("karpathy")
        assert items == []
