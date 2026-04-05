from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CollectedItem:
    """Raw item from a collector before it becomes a Content record."""
    source_platform: str
    original_url: str
    raw_text: str
    published_at: datetime | None = None


class BaseCollector(ABC):
    @abstractmethod
    async def collect(self, handle: str) -> list[CollectedItem]:
        """Collect content for a given platform handle."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the collector's data source is reachable."""
        ...
