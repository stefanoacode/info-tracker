import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.llm.claude_provider import ClaudeProvider

@pytest.mark.asyncio
async def test_summarize_calls_claude_api():
    provider = ClaudeProvider(api_key="test-key")
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="**So what:** AI agents are now production-ready.\n\n- Key point 1\n- Key point 2")]
    with patch.object(provider, "client") as mock_client:
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        result = await provider.summarize("Long article about AI agents being deployed in production...")
        assert "So what" in result or "agents" in result.lower()
        mock_client.messages.create.assert_called_once()

@pytest.mark.asyncio
async def test_extract_topics():
    provider = ClaudeProvider(api_key="test-key")
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text='["agents", "production", "deployment"]')]
    with patch.object(provider, "client") as mock_client:
        mock_client.messages = MagicMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)
        topics = await provider.extract_topics("Article about deploying AI agents in production")
        assert isinstance(topics, list)
        assert len(topics) > 0
