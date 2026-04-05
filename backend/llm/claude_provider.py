import json
import logging
from pathlib import Path
from anthropic import AsyncAnthropic
from backend.llm.base import LLMProvider

logger = logging.getLogger(__name__)
PROMPTS_DIR = Path(__file__).parent.parent.parent / "data" / "prompts"

def _load_prompt(name: str) -> str:
    return (PROMPTS_DIR / f"{name}.md").read_text()

class ClaudeProvider:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def summarize(self, content: str) -> str:
        prompt = _load_prompt("summarize").replace("{content}", content)
        message = await self.client.messages.create(model=self.model, max_tokens=500, messages=[{"role": "user", "content": prompt}])
        return message.content[0].text

    async def extract_topics(self, content: str) -> list[str]:
        message = await self.client.messages.create(model=self.model, max_tokens=200, messages=[{"role": "user", "content": f'Extract 2-5 topic tags from this content. Return as a JSON array of lowercase strings.\n\nContent: {content}'}])
        try:
            return json.loads(message.content[0].text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse topics JSON, returning empty list")
            return []

    async def analyze_trends(self, contents_with_ids: str, time_range: str = "7d") -> str:
        prompt = _load_prompt("trends").replace("{content}", contents_with_ids).replace("{time_range}", time_range)
        message = await self.client.messages.create(model=self.model, max_tokens=2000, messages=[{"role": "user", "content": prompt}])
        return message.content[0].text
