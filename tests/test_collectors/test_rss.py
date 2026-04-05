import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from backend.collectors.rss import RSSCollector

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Blog</title>
    <item>
      <title>AI Agents Are Changing Everything</title>
      <link>https://example.com/post/1</link>
      <description>A deep dive into how AI agents are reshaping software development workflows.</description>
      <pubDate>Sat, 05 Apr 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Fine-tuning Tips</title>
      <link>https://example.com/post/2</link>
      <description>Practical advice for fine-tuning LLMs on custom data.</description>
      <pubDate>Fri, 04 Apr 2026 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>"""

@pytest.fixture
def collector():
    return RSSCollector()

@pytest.mark.asyncio
async def test_rss_collect_parses_items(collector):
    with patch("backend.collectors.rss.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock()
        mock_client.get.return_value.text = SAMPLE_RSS
        mock_client.get.return_value.status_code = 200
        mock_client_cls.return_value = mock_client
        items = await collector.collect("https://example.com/feed")
        assert len(items) == 2
        assert items[0].source_platform == "substack"
        assert "AI Agents" in items[0].raw_text
        assert items[0].original_url == "https://example.com/post/1"

@pytest.mark.asyncio
async def test_rss_collect_returns_empty_on_failure(collector):
    with patch("backend.collectors.rss.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=Exception("Network error"))
        mock_client_cls.return_value = mock_client
        items = await collector.collect("https://example.com/feed")
        assert items == []
