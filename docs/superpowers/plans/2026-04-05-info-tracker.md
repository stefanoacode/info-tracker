# Info Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local-first AI ecosystem tracker that aggregates content from X/Twitter, YouTube, Substack, and Reddit, summarizes it with Claude API using pyramid-principle formatting, serves it via a React dashboard, and integrates with Claude Code as a skill with Channel-based notifications.

**Architecture:** FastAPI backend with SQLite (SQLAlchemy ORM), pluggable collectors per platform, Claude API for summarization behind an LLM abstraction layer, APScheduler for periodic collection. React + Vite + Tailwind frontend consuming the REST API. Claude Code skill querying the same API.

**Tech Stack:** Python 3.12+, FastAPI, SQLAlchemy, APScheduler, anthropic SDK, React 18, Vite, TypeScript, Tailwind CSS, uv (Python package manager), npm (frontend)

---

## Phase 1: Project Scaffolding & Database

### Task 1: Initialize Python Project

**Files:**
- Create: `pyproject.toml`
- Create: `backend/__init__.py`
- Create: `.env.example`
- Create: `.gitignore`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "info-tracker"
version = "0.1.0"
description = "AI ecosystem content tracker and summarizer"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy>=2.0.0",
    "aiosqlite>=0.20.0",
    "apscheduler>=3.10.0",
    "anthropic>=0.40.0",
    "httpx>=0.27.0",
    "feedparser>=6.0.0",
    "youtube-transcript-api>=0.6.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-httpx>=0.30.0",
    "ruff>=0.6.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100
```

- [ ] **Step 2: Create .env.example**

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Optional — leave blank to skip platform
YOUTUBE_API_KEY=
X_API_BEARER_TOKEN=

# App config
DATABASE_URL=sqlite+aiosqlite:///./data/info_tracker.db
COLLECTION_INTERVAL_HOURS=6
API_HOST=127.0.0.1
API_PORT=8000
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.env
*.db
.venv/
node_modules/
dist/
.DS_Store
```

- [ ] **Step 4: Create backend/__init__.py**

```python
```

(Empty init file to make backend a package.)

- [ ] **Step 5: Install dependencies**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker && uv venv && uv pip install -e ".[dev]"`
Expected: All packages install successfully.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .env.example .gitignore backend/__init__.py
git commit -m "feat: initialize python project with dependencies"
```

---

### Task 2: Database Models

**Files:**
- Create: `backend/database.py`
- Create: `backend/models/__init__.py`
- Create: `backend/models/category.py`
- Create: `backend/models/person.py`
- Create: `backend/models/content.py`
- Create: `backend/models/trend.py`
- Create: `backend/config.py`
- Test: `tests/__init__.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

Create `tests/__init__.py` (empty) and `tests/test_models.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models.category import Category
from backend.models.person import Person
from backend.models.content import Content
from backend.models.trend import Trend


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_create_category(db):
    cat = Category(name="Builders", description="Engineers shipping AI products", sort_order=1)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    assert cat.id is not None
    assert cat.name == "Builders"
    assert cat.is_custom is False


def test_create_person_with_category(db):
    cat = Category(name="Investors", sort_order=1)
    db.add(cat)
    db.commit()

    person = Person(
        name="Elad Gil",
        bio="Investor and author",
        category_id=cat.id,
        platform_handles={"x": "@elogoism", "substack": "https://blog.eladgil.com"},
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    assert person.id is not None
    assert person.category.name == "Investors"
    assert person.platform_handles["x"] == "@elogoism"


def test_create_content(db):
    cat = Category(name="Builders", sort_order=1)
    db.add(cat)
    db.commit()

    person = Person(name="Karpathy", category_id=cat.id, platform_handles={"x": "@karpathy"})
    db.add(person)
    db.commit()

    content = Content(
        person_id=person.id,
        source_platform="x",
        original_url="https://x.com/karpathy/status/123",
        raw_text="Fine-tuning is all you need for most use cases.",
        so_what="Fine-tuning beats prompting for production use cases",
        topics=["fine-tuning", "llm"],
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    assert content.id is not None
    assert content.person.name == "Karpathy"
    assert "fine-tuning" in content.topics


def test_create_trend(db):
    trend = Trend(
        topic="agents",
        description="Agent frameworks gaining momentum across builders and founders",
        related_content_ids=[1, 2, 3],
        time_range="7d",
        sentiment_score=0.7,
        momentum_score=0.85,
    )
    db.add(trend)
    db.commit()
    db.refresh(trend)
    assert trend.id is not None
    assert trend.momentum_score == 0.85
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker && uv run pytest tests/test_models.py -v`
Expected: FAIL — cannot import backend.database, backend.models.*

- [ ] **Step 3: Create backend/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/info_tracker.db"
    anthropic_api_key: str = ""
    youtube_api_key: str = ""
    x_api_bearer_token: str = ""
    collection_interval_hours: int = 6
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 4: Create backend/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings


class Base(DeclarativeBase):
    pass


# Async engine for FastAPI
async_engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


# Sync engine for tests and scripts
def get_sync_engine(url: str = "sqlite:///:memory:"):
    return create_engine(url)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

- [ ] **Step 5: Create backend/models/__init__.py**

```python
from backend.models.category import Category
from backend.models.person import Person
from backend.models.content import Content
from backend.models.trend import Trend

__all__ = ["Category", "Person", "Content", "Trend"]
```

- [ ] **Step 6: Create backend/models/category.py**

```python
from datetime import datetime, timezone

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    people: Mapped[list["Person"]] = relationship("Person", back_populates="category")
```

- [ ] **Step 7: Create backend/models/person.py**

```python
from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"), nullable=False)
    platform_handles: Mapped[dict] = mapped_column(JSON, default=dict)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    category: Mapped["Category"] = relationship("Category", back_populates="people")
    contents: Mapped[list["Content"]] = relationship("Content", back_populates="person")
```

- [ ] **Step 8: Create backend/models/content.py**

```python
from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Content(Base):
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("people.id"), nullable=False)
    source_platform: Mapped[str] = mapped_column(String(50), nullable=False)
    original_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    so_what: Mapped[str | None] = mapped_column(String(500), nullable=True)
    topics: Mapped[list] = mapped_column(JSON, default=list)
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    collected_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    person: Mapped["Person"] = relationship("Person", back_populates="contents")
```

- [ ] **Step 9: Create backend/models/trend.py**

```python
from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class Trend(Base):
    __tablename__ = "trends"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    related_content_ids: Mapped[list] = mapped_column(JSON, default=list)
    detected_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    time_range: Mapped[str] = mapped_column(String(10), default="7d")
    sentiment_score: Mapped[float] = mapped_column(Float, default=0.0)
    momentum_score: Mapped[float] = mapped_column(Float, default=0.0)
```

- [ ] **Step 10: Run tests to verify they pass**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker && uv run pytest tests/test_models.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 11: Commit**

```bash
git add backend/ tests/
git commit -m "feat: add database models for category, person, content, trend"
```

---

### Task 3: Preset Data & Database Seeding

**Files:**
- Create: `data/presets/builders.json`
- Create: `data/presets/researchers.json`
- Create: `data/presets/founders.json`
- Create: `data/presets/investors.json`
- Create: `data/presets/commentators.json`
- Create: `backend/seed.py`
- Test: `tests/test_seed.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_seed.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models import Category, Person
from backend.seed import seed_database


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    Base.metadata.drop_all(engine)


def test_seed_creates_categories(db):
    seed_database(db)
    categories = db.query(Category).all()
    names = {c.name for c in categories}
    assert "Builders" in names
    assert "Researchers" in names
    assert "Founders" in names
    assert "Investors" in names
    assert "Commentators" in names


def test_seed_creates_people(db):
    seed_database(db)
    people = db.query(Person).all()
    assert len(people) > 0
    # Check at least one known person exists
    names = {p.name for p in people}
    assert "Andrej Karpathy" in names


def test_seed_is_idempotent(db):
    seed_database(db)
    count_first = db.query(Person).count()
    seed_database(db)
    count_second = db.query(Person).count()
    assert count_first == count_second
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_seed.py -v`
Expected: FAIL — cannot import backend.seed

- [ ] **Step 3: Create preset JSON files**

Create `data/presets/builders.json`:

```json
[
    {
        "name": "Andrej Karpathy",
        "bio": "Former Tesla AI Director, OpenAI founding member, AI educator",
        "platform_handles": {
            "x": "karpathy",
            "youtube": "UCsBjURrPoezykLs9EqgamOA"
        }
    },
    {
        "name": "Simon Willison",
        "bio": "Creator of Datasette, Django co-creator, LLM tools builder",
        "platform_handles": {
            "x": "simonw",
            "substack": "https://simonwillison.net/atom/everything/"
        }
    },
    {
        "name": "Swyx",
        "bio": "AI Engineer, writer, founder of Latent Space",
        "platform_handles": {
            "x": "swyx",
            "youtube": "UCVIyBFAnEHPBMOQ7r3GxnOg",
            "substack": "https://www.latent.space/feed"
        }
    }
]
```

Create `data/presets/researchers.json`:

```json
[
    {
        "name": "Yann LeCun",
        "bio": "VP & Chief AI Scientist at Meta, Turing Award winner",
        "platform_handles": {
            "x": "ylecun"
        }
    },
    {
        "name": "Sasha Rush",
        "bio": "Cornell professor, open-source ML researcher",
        "platform_handles": {
            "x": "sraborern"
        }
    }
]
```

Create `data/presets/founders.json`:

```json
[
    {
        "name": "Dario Amodei",
        "bio": "CEO of Anthropic",
        "platform_handles": {
            "x": "DarioAmodei"
        }
    },
    {
        "name": "Sam Altman",
        "bio": "CEO of OpenAI",
        "platform_handles": {
            "x": "sama",
            "substack": "https://blog.samaltman.com/feed"
        }
    },
    {
        "name": "Arthur Mensch",
        "bio": "CEO of Mistral AI",
        "platform_handles": {
            "x": "arthurmensch"
        }
    }
]
```

Create `data/presets/investors.json`:

```json
[
    {
        "name": "Elad Gil",
        "bio": "Investor, author of High Growth Handbook",
        "platform_handles": {
            "x": "elogoism",
            "substack": "https://blog.eladgil.com/feed"
        }
    },
    {
        "name": "Sarah Guo",
        "bio": "Founder of Conviction VC, AI-focused investor",
        "platform_handles": {
            "x": "saranormous",
            "youtube": "UCkJB8czhGqnMTE-bmbBReLA"
        }
    }
]
```

Create `data/presets/commentators.json`:

```json
[
    {
        "name": "Zvi Mowshowitz",
        "bio": "AI policy analyst, writes weekly AI roundups",
        "platform_handles": {
            "x": "TheZvi",
            "substack": "https://thezvi.substack.com/feed"
        }
    },
    {
        "name": "Gary Marcus",
        "bio": "NYU professor emeritus, AI critic and commentator",
        "platform_handles": {
            "x": "GaryMarcus",
            "substack": "https://garymarcus.substack.com/feed"
        }
    }
]
```

- [ ] **Step 4: Create backend/seed.py**

```python
import json
from pathlib import Path

from sqlalchemy.orm import Session

from backend.models.category import Category
from backend.models.person import Person

PRESETS_DIR = Path(__file__).parent.parent / "data" / "presets"

CATEGORIES = [
    {"name": "Builders", "description": "Engineers, PMs, designers shipping AI products", "sort_order": 1},
    {"name": "Researchers", "description": "Scientists publishing papers, pushing SOTA", "sort_order": 2},
    {"name": "Founders", "description": "CEO/CTOs of AI-native startups", "sort_order": 3},
    {"name": "Investors", "description": "VCs and angels actively funding AI", "sort_order": 4},
    {"name": "Commentators", "description": "Journalists, analysts, policy thinkers covering AI", "sort_order": 5},
]


def seed_database(db: Session) -> None:
    """Seed categories and preset people. Idempotent — skips existing records."""
    # Seed categories
    for cat_data in CATEGORIES:
        existing = db.query(Category).filter_by(name=cat_data["name"]).first()
        if not existing:
            db.add(Category(**cat_data))
    db.commit()

    # Seed people from preset files
    for cat in db.query(Category).filter_by(is_custom=False).all():
        filename = cat.name.lower() + ".json"
        preset_file = PRESETS_DIR / filename
        if not preset_file.exists():
            continue

        with open(preset_file) as f:
            people_data = json.load(f)

        for person_data in people_data:
            existing = db.query(Person).filter_by(name=person_data["name"]).first()
            if not existing:
                db.add(
                    Person(
                        name=person_data["name"],
                        bio=person_data.get("bio", ""),
                        category_id=cat.id,
                        platform_handles=person_data.get("platform_handles", {}),
                    )
                )
    db.commit()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_seed.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add data/presets/ backend/seed.py tests/test_seed.py
git commit -m "feat: add preset data and database seeding"
```

---

## Phase 2: Collectors

### Task 4: Base Collector Interface

**Files:**
- Create: `backend/collectors/__init__.py`
- Create: `backend/collectors/base.py`

- [ ] **Step 1: Create backend/collectors/__init__.py**

```python
```

- [ ] **Step 2: Create backend/collectors/base.py**

```python
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
```

- [ ] **Step 3: Commit**

```bash
git add backend/collectors/
git commit -m "feat: add base collector interface"
```

---

### Task 5: RSS Collector (Substack/Blogs)

**Files:**
- Create: `backend/collectors/rss.py`
- Test: `tests/test_collectors/__init__.py`
- Test: `tests/test_collectors/test_rss.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_collectors/__init__.py` (empty) and `tests/test_collectors/test_rss.py`:

```python
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone

from backend.collectors.rss import RSSCollector

# Minimal valid RSS feed
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_collectors/test_rss.py -v`
Expected: FAIL — cannot import backend.collectors.rss

- [ ] **Step 3: Create backend/collectors/rss.py**

```python
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from backend.collectors.base import BaseCollector, CollectedItem

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    async def collect(self, handle: str) -> list[CollectedItem]:
        """Collect from an RSS/Atom feed URL. Handle is the feed URL."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(handle, timeout=30.0)
                response.raise_for_status()

            feed = feedparser.parse(response.text)
            items = []
            for entry in feed.entries:
                published_at = None
                if hasattr(entry, "published"):
                    try:
                        published_at = parsedate_to_datetime(entry.published)
                    except (ValueError, TypeError):
                        pass

                title = getattr(entry, "title", "")
                description = getattr(entry, "description", "")
                raw_text = f"{title}\n\n{description}" if title else description

                items.append(
                    CollectedItem(
                        source_platform="substack",
                        original_url=getattr(entry, "link", ""),
                        raw_text=raw_text,
                        published_at=published_at,
                    )
                )
            return items

        except Exception as e:
            logger.warning(f"RSS collection failed for {handle}: {e}")
            return []

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://simonwillison.net/atom/everything/", timeout=10.0)
                return resp.status_code == 200
        except Exception:
            return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_collectors/test_rss.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/collectors/rss.py tests/test_collectors/
git commit -m "feat: add RSS collector for Substack and blogs"
```

---

### Task 6: Reddit Collector

**Files:**
- Create: `backend/collectors/reddit.py`
- Test: `tests/test_collectors/test_reddit.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_collectors/test_reddit.py`:

```python
import pytest
from unittest.mock import patch, AsyncMock
import json

from backend.collectors.reddit import RedditCollector

SAMPLE_REDDIT_JSON = {
    "data": {
        "children": [
            {
                "kind": "t1",
                "data": {
                    "body": "I think agents are overhyped right now. Most production use cases still need RAG.",
                    "permalink": "/r/MachineLearning/comments/abc123/comment/def456/",
                    "created_utc": 1743850000.0,
                    "subreddit": "MachineLearning",
                },
            },
            {
                "kind": "t1",
                "data": {
                    "body": "Fine-tuning Llama 3 on domain data works surprisingly well.",
                    "permalink": "/r/LocalLLaMA/comments/xyz789/comment/ghi012/",
                    "created_utc": 1743760000.0,
                    "subreddit": "LocalLLaMA",
                },
            },
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_collectors/test_reddit.py -v`
Expected: FAIL — cannot import backend.collectors.reddit

- [ ] **Step 3: Create backend/collectors/reddit.py**

```python
import logging
from datetime import datetime, timezone

import httpx

from backend.collectors.base import BaseCollector, CollectedItem

logger = logging.getLogger(__name__)

REDDIT_USER_COMMENTS_URL = "https://www.reddit.com/user/{username}/comments.json"


class RedditCollector(BaseCollector):
    async def collect(self, handle: str) -> list[CollectedItem]:
        """Collect recent comments from a Reddit user. Handle is the username (without u/)."""
        try:
            url = REDDIT_USER_COMMENTS_URL.format(username=handle)
            headers = {"User-Agent": "InfoTracker/0.1"}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()

            data = response.json()
            items = []
            for child in data.get("data", {}).get("children", []):
                comment = child.get("data", {})
                body = comment.get("body", "")
                permalink = comment.get("permalink", "")
                created_utc = comment.get("created_utc", 0)
                subreddit = comment.get("subreddit", "")

                published_at = datetime.fromtimestamp(created_utc, tz=timezone.utc) if created_utc else None

                items.append(
                    CollectedItem(
                        source_platform="reddit",
                        original_url=f"https://www.reddit.com{permalink}",
                        raw_text=f"[r/{subreddit}] {body}" if subreddit else body,
                        published_at=published_at,
                    )
                )
            return items

        except Exception as e:
            logger.warning(f"Reddit collection failed for {handle}: {e}")
            return []

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://www.reddit.com/r/MachineLearning.json",
                    headers={"User-Agent": "InfoTracker/0.1"},
                    timeout=10.0,
                )
                return resp.status_code == 200
        except Exception:
            return False
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_collectors/test_reddit.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/collectors/reddit.py tests/test_collectors/test_reddit.py
git commit -m "feat: add Reddit comments collector"
```

---

### Task 7: YouTube Collector

**Files:**
- Create: `backend/collectors/youtube.py`
- Test: `tests/test_collectors/test_youtube.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_collectors/test_youtube.py`:

```python
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from backend.collectors.youtube import YouTubeCollector

SAMPLE_SEARCH_RESPONSE = {
    "items": [
        {
            "id": {"videoId": "abc123"},
            "snippet": {
                "title": "The State of AI Agents in 2026",
                "publishedAt": "2026-04-01T10:00:00Z",
            },
        },
        {
            "id": {"videoId": "def456"},
            "snippet": {
                "title": "Fine-tuning vs Prompting",
                "publishedAt": "2026-03-28T10:00:00Z",
            },
        },
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_collectors/test_youtube.py -v`
Expected: FAIL — cannot import backend.collectors.youtube

- [ ] **Step 3: Create backend/collectors/youtube.py**

```python
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
        """Collect recent videos from a YouTube channel. Handle is the channel ID."""
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

            data = response.json()
            items = []

            for video in data.get("items", []):
                video_id = video["id"]["videoId"]
                snippet = video["snippet"]
                title = snippet.get("title", "")
                published_at = None
                if "publishedAt" in snippet:
                    published_at = datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00"))

                # Try to get transcript
                transcript_text = ""
                try:
                    ytt_api = YouTubeTranscriptApi()
                    transcript = ytt_api.fetch(video_id)
                    parts = transcript.to_raw_data()
                    transcript_text = " ".join(part["text"] for part in parts)
                except Exception as e:
                    logger.debug(f"No transcript for {video_id}: {e}")

                raw_text = f"{title}\n\n{transcript_text}" if transcript_text else title

                items.append(
                    CollectedItem(
                        source_platform="youtube",
                        original_url=f"https://www.youtube.com/watch?v={video_id}",
                        raw_text=raw_text,
                        published_at=published_at,
                    )
                )

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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_collectors/test_youtube.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/collectors/youtube.py tests/test_collectors/test_youtube.py
git commit -m "feat: add YouTube collector with transcript support"
```

---

### Task 8: Twitter/X Collector

**Files:**
- Create: `backend/collectors/twitter.py`
- Test: `tests/test_collectors/test_twitter.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_collectors/test_twitter.py`:

```python
import pytest
from unittest.mock import patch, AsyncMock

from backend.collectors.twitter import TwitterCollector

SAMPLE_TWEETS_RESPONSE = {
    "data": [
        {
            "id": "1234567890",
            "text": "Fine-tuning is all you need for most production use cases. Don't overthink it.",
            "created_at": "2026-04-05T10:00:00.000Z",
        },
        {
            "id": "1234567891",
            "text": "Just shipped a new feature using Claude. The code quality is impressive.",
            "created_at": "2026-04-04T15:30:00.000Z",
        },
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_collectors/test_twitter.py -v`
Expected: FAIL — cannot import backend.collectors.twitter

- [ ] **Step 3: Create backend/collectors/twitter.py**

```python
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
        """Collect recent tweets. Handle is the X/Twitter username (without @)."""
        if not self.bearer_token:
            logger.warning("X API bearer token not configured, skipping collection")
            return []

        try:
            headers = {"Authorization": f"Bearer {self.bearer_token}"}

            async with httpx.AsyncClient() as client:
                # Look up user ID
                user_resp = await client.get(
                    TWITTER_USER_LOOKUP_URL.format(username=handle),
                    headers=headers,
                    timeout=30.0,
                )
                user_resp.raise_for_status()
                user_id = user_resp.json()["data"]["id"]

                # Fetch tweets
                tweets_resp = await client.get(
                    TWITTER_USER_TWEETS_URL.format(user_id=user_id),
                    headers=headers,
                    params={"max_results": 10, "tweet.fields": "created_at"},
                    timeout=30.0,
                )
                tweets_resp.raise_for_status()

            data = tweets_resp.json()
            items = []
            for tweet in data.get("data", []):
                published_at = None
                if "created_at" in tweet:
                    published_at = datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00"))

                items.append(
                    CollectedItem(
                        source_platform="x",
                        original_url=f"https://x.com/{handle}/status/{tweet['id']}",
                        raw_text=tweet["text"],
                        published_at=published_at,
                    )
                )
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_collectors/test_twitter.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/collectors/twitter.py tests/test_collectors/test_twitter.py
git commit -m "feat: add Twitter/X collector"
```

---

### Task 9: Collection Orchestrator

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/collector_service.py`
- Test: `tests/test_services/__init__.py`
- Test: `tests/test_services/test_collector_service.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_services/__init__.py` (empty) and `tests/test_services/test_collector_service.py`:

```python
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models import Category, Person, Content
from backend.collectors.base import CollectedItem
from backend.services.collector_service import CollectorService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        cat = Category(name="Builders", sort_order=1)
        session.add(cat)
        session.commit()

        person = Person(
            name="Simon Willison",
            category_id=cat.id,
            platform_handles={
                "substack": "https://simonwillison.net/atom/everything/",
                "reddit": "simonw",
            },
        )
        session.add(person)
        session.commit()
        yield session
    Base.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_collect_for_person(db):
    mock_rss = AsyncMock()
    mock_rss.collect.return_value = [
        CollectedItem(
            source_platform="substack",
            original_url="https://example.com/post/1",
            raw_text="New blog post about AI",
            published_at=datetime(2026, 4, 5, tzinfo=timezone.utc),
        )
    ]

    mock_reddit = AsyncMock()
    mock_reddit.collect.return_value = [
        CollectedItem(
            source_platform="reddit",
            original_url="https://reddit.com/r/ml/comment/1",
            raw_text="Interesting comment about LLMs",
            published_at=datetime(2026, 4, 4, tzinfo=timezone.utc),
        )
    ]

    service = CollectorService(
        collectors={"substack": mock_rss, "reddit": mock_reddit},
    )

    person = db.query(Person).first()
    new_content = await service.collect_for_person(db, person)
    assert len(new_content) == 2
    assert db.query(Content).count() == 2


@pytest.mark.asyncio
async def test_collect_skips_duplicates(db):
    mock_rss = AsyncMock()
    item = CollectedItem(
        source_platform="substack",
        original_url="https://example.com/post/1",
        raw_text="Blog post",
    )
    mock_rss.collect.return_value = [item]

    service = CollectorService(collectors={"substack": mock_rss})

    person = db.query(Person).first()
    await service.collect_for_person(db, person)
    await service.collect_for_person(db, person)
    assert db.query(Content).count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_services/test_collector_service.py -v`
Expected: FAIL — cannot import backend.services.collector_service

- [ ] **Step 3: Create backend/services/__init__.py (empty) and backend/services/collector_service.py**

```python
import logging

from sqlalchemy.orm import Session

from backend.collectors.base import BaseCollector, CollectedItem
from backend.models.content import Content
from backend.models.person import Person

logger = logging.getLogger(__name__)


class CollectorService:
    def __init__(self, collectors: dict[str, BaseCollector]):
        self.collectors = collectors

    async def collect_for_person(self, db: Session, person: Person) -> list[Content]:
        """Run all matching collectors for a person and store new content."""
        new_contents = []

        for platform, handle in person.platform_handles.items():
            collector = self.collectors.get(platform)
            if not collector:
                continue

            try:
                items = await collector.collect(handle)
                for item in items:
                    existing = (
                        db.query(Content)
                        .filter_by(person_id=person.id, original_url=item.original_url)
                        .first()
                    )
                    if existing:
                        continue

                    content = Content(
                        person_id=person.id,
                        source_platform=item.source_platform,
                        original_url=item.original_url,
                        raw_text=item.raw_text,
                        published_at=item.published_at,
                    )
                    db.add(content)
                    new_contents.append(content)
            except Exception as e:
                logger.error(f"Collection failed for {person.name} on {platform}: {e}")

        db.commit()
        return new_contents

    async def collect_all(self, db: Session) -> list[Content]:
        """Run collection for all tracked people."""
        all_new = []
        for person in db.query(Person).all():
            new = await self.collect_for_person(db, person)
            all_new.extend(new)
        return all_new
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_services/test_collector_service.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/ tests/test_services/
git commit -m "feat: add collection orchestrator service"
```

---

## Phase 3: AI Summarization

### Task 10: LLM Provider Interface & Claude Implementation

**Files:**
- Create: `backend/llm/__init__.py`
- Create: `backend/llm/base.py`
- Create: `backend/llm/claude_provider.py`
- Create: `data/prompts/summarize.md`
- Create: `data/prompts/digest.md`
- Create: `data/prompts/trends.md`
- Test: `tests/test_llm/__init__.py`
- Test: `tests/test_llm/test_claude_provider.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_llm/__init__.py` (empty) and `tests/test_llm/test_claude_provider.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_llm/test_claude_provider.py -v`
Expected: FAIL — cannot import backend.llm.claude_provider

- [ ] **Step 3: Create prompt templates**

Create `data/prompts/summarize.md`:

```markdown
You are a concise analyst. Summarize the following content using the pyramid principle.

Structure your response EXACTLY as:
**So what:** [One sentence — the key takeaway and why it matters]

- [Supporting point 1]
- [Supporting point 2]
- [Supporting point 3 if needed, max 4 bullets]

Rules:
- Lead with the conclusion, not the setup
- Each bullet is one crisp sentence
- No fluff, no restating the obvious
- If the content is trivial or promotional, say so in one line

Content to summarize:
{content}
```

Create `data/prompts/digest.md`:

```markdown
You are creating a digest of recent AI ecosystem content. Group and summarize the following items into a crisp briefing.

Structure:
## Top Takeaways
- [3-5 most important things across all content]

## By Category
### [Category Name]
- **[Person Name]**: [One-line summary] — [URL]

Rules:
- Pyramid principle: lead with what matters most
- Each person gets ONE line unless they said something exceptionally important
- Include the original URL for every item
- Skip trivial or promotional content entirely

Content items:
{content}
```

Create `data/prompts/trends.md`:

```markdown
Analyze the following content items collected over the past {time_range} and identify trending topics.

For each trend, provide:
- **Topic**: [Short name]
- **Description**: [1-2 sentences on what's happening]
- **Sentiment**: [Score from -1.0 to 1.0, negative = critical, positive = optimistic]
- **Momentum**: [Score from 0.0 to 1.0, 0 = fading, 1 = accelerating]
- **Related content IDs**: [List of content IDs that relate to this trend]

Return as a JSON array of objects with keys: topic, description, sentiment_score, momentum_score, related_content_ids.

Content items (each prefixed with [ID]):
{content}
```

- [ ] **Step 4: Create backend/llm/__init__.py (empty), backend/llm/base.py**

```python
from typing import Protocol


class LLMProvider(Protocol):
    async def summarize(self, content: str) -> str:
        """Return a pyramid-principle summary of the content."""
        ...

    async def extract_topics(self, content: str) -> list[str]:
        """Extract topic tags from content."""
        ...

    async def analyze_trends(self, contents_with_ids: str, time_range: str) -> str:
        """Analyze content items and return trend JSON."""
        ...
```

- [ ] **Step 5: Create backend/llm/claude_provider.py**

```python
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
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    async def extract_topics(self, content: str) -> list[str]:
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": f'Extract 2-5 topic tags from this content. Return as a JSON array of lowercase strings.\n\nContent: {content}',
                }
            ],
        )
        try:
            return json.loads(message.content[0].text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse topics JSON, returning empty list")
            return []

    async def analyze_trends(self, contents_with_ids: str, time_range: str = "7d") -> str:
        prompt = _load_prompt("trends").replace("{content}", contents_with_ids).replace("{time_range}", time_range)
        message = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_llm/test_claude_provider.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/llm/ data/prompts/ tests/test_llm/
git commit -m "feat: add LLM abstraction layer with Claude provider and prompt templates"
```

---

### Task 11: Summarizer Service

**Files:**
- Create: `backend/services/summarizer.py`
- Test: `tests/test_services/test_summarizer.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_services/test_summarizer.py`:

```python
import pytest
from unittest.mock import AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.database import Base
from backend.models import Category, Person, Content
from backend.services.summarizer import SummarizerService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        cat = Category(name="Builders", sort_order=1)
        session.add(cat)
        session.commit()

        person = Person(name="Karpathy", category_id=cat.id, platform_handles={"x": "karpathy"})
        session.add(person)
        session.commit()

        content = Content(
            person_id=person.id,
            source_platform="x",
            original_url="https://x.com/karpathy/status/123",
            raw_text="Fine-tuning is all you need for most production use cases. Don't overthink it.",
        )
        session.add(content)
        session.commit()
        yield session
    Base.metadata.drop_all(engine)


@pytest.mark.asyncio
async def test_summarize_unsummarized_content(db):
    mock_llm = AsyncMock()
    mock_llm.summarize.return_value = "**So what:** Fine-tuning beats prompting for production.\n\n- Simple and effective\n- Most teams overthink this"
    mock_llm.extract_topics.return_value = ["fine-tuning", "llm", "production"]

    service = SummarizerService(llm=mock_llm)
    count = await service.summarize_pending(db)
    assert count == 1

    content = db.query(Content).first()
    assert content.ai_summary is not None
    assert "So what" in content.ai_summary
    assert content.so_what is not None
    assert len(content.topics) > 0


@pytest.mark.asyncio
async def test_summarize_skips_already_summarized(db):
    content = db.query(Content).first()
    content.ai_summary = "Already done"
    content.so_what = "Already extracted"
    db.commit()

    mock_llm = AsyncMock()
    service = SummarizerService(llm=mock_llm)
    count = await service.summarize_pending(db)
    assert count == 0
    mock_llm.summarize.assert_not_called()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_services/test_summarizer.py -v`
Expected: FAIL — cannot import backend.services.summarizer

- [ ] **Step 3: Create backend/services/summarizer.py**

```python
import logging
import re

from sqlalchemy.orm import Session

from backend.llm.base import LLMProvider
from backend.models.content import Content

logger = logging.getLogger(__name__)


def _extract_so_what(summary: str) -> str:
    """Extract the 'So what' line from a pyramid-principle summary."""
    match = re.search(r"\*\*So what:\*\*\s*(.+?)(?:\n|$)", summary)
    if match:
        return match.group(1).strip()
    # Fallback: first non-empty line
    for line in summary.split("\n"):
        line = line.strip()
        if line and not line.startswith("-") and not line.startswith("#"):
            return line
    return ""


class SummarizerService:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def summarize_pending(self, db: Session) -> int:
        """Summarize all content that hasn't been summarized yet. Returns count."""
        pending = db.query(Content).filter(Content.ai_summary.is_(None)).all()
        count = 0

        for content in pending:
            try:
                summary = await self.llm.summarize(content.raw_text)
                topics = await self.llm.extract_topics(content.raw_text)

                content.ai_summary = summary
                content.so_what = _extract_so_what(summary)
                content.topics = topics
                count += 1
            except Exception as e:
                logger.error(f"Summarization failed for content {content.id}: {e}")

        db.commit()
        return count
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_services/test_summarizer.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/services/summarizer.py tests/test_services/test_summarizer.py
git commit -m "feat: add summarizer service with pyramid-principle extraction"
```

---

## Phase 4: REST API

### Task 12: FastAPI App & People API

**Files:**
- Create: `backend/main.py`
- Create: `backend/api/__init__.py`
- Create: `backend/api/people.py`
- Test: `tests/test_api/__init__.py`
- Test: `tests/test_api/test_people.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_api/__init__.py` (empty) and `tests/test_api/test_people.py`:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base, get_db
from backend.main import app
from backend.seed import seed_database


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    seed_database(session)
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_list_categories(client):
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 5
    names = {c["name"] for c in data}
    assert "Builders" in names


def test_list_people(client):
    resp = client.get("/api/people")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 0


def test_list_people_by_category(client):
    resp = client.get("/api/people?category=Builders")
    assert resp.status_code == 200
    data = resp.json()
    assert all(p["category_name"] == "Builders" for p in data)


def test_add_person(client):
    resp = client.post(
        "/api/people",
        json={
            "name": "New Person",
            "bio": "A new person to track",
            "category_name": "Investors",
            "platform_handles": {"x": "newperson"},
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "New Person"
    assert data["is_custom"] is True


def test_delete_person(client):
    # Add then delete
    resp = client.post(
        "/api/people",
        json={"name": "Temporary", "category_name": "Builders", "platform_handles": {}},
    )
    person_id = resp.json()["id"]

    resp = client.delete(f"/api/people/{person_id}")
    assert resp.status_code == 204
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_api/test_people.py -v`
Expected: FAIL — cannot import backend.main

- [ ] **Step 3: Create backend/main.py**

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.api.people import router as people_router
from backend.api.feed import router as feed_router
from backend.api.trends import router as trends_router
from backend.api.digest import router as digest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Info Tracker", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(people_router, prefix="/api")
app.include_router(feed_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
app.include_router(digest_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 4: Create backend/api/__init__.py (empty) and backend/api/people.py**

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.category import Category
from backend.models.person import Person

router = APIRouter()


class PersonCreate(BaseModel):
    name: str
    bio: str = ""
    category_name: str
    platform_handles: dict = {}


class PersonResponse(BaseModel):
    id: int
    name: str
    bio: str | None
    avatar_url: str | None
    category_name: str
    platform_handles: dict
    is_custom: bool

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_custom: bool
    sort_order: int

    model_config = {"from_attributes": True}


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.sort_order).all()


@router.get("/people", response_model=list[PersonResponse])
def list_people(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Person)
    if category:
        query = query.join(Category).filter(Category.name == category)
    people = query.all()
    return [
        PersonResponse(
            id=p.id,
            name=p.name,
            bio=p.bio,
            avatar_url=p.avatar_url,
            category_name=p.category.name,
            platform_handles=p.platform_handles,
            is_custom=p.is_custom,
        )
        for p in people
    ]


@router.post("/people", response_model=PersonResponse, status_code=201)
def add_person(data: PersonCreate, db: Session = Depends(get_db)):
    category = db.query(Category).filter_by(name=data.category_name).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{data.category_name}' not found")

    person = Person(
        name=data.name,
        bio=data.bio,
        category_id=category.id,
        platform_handles=data.platform_handles,
        is_custom=True,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return PersonResponse(
        id=person.id,
        name=person.name,
        bio=person.bio,
        avatar_url=person.avatar_url,
        category_name=category.name,
        platform_handles=person.platform_handles,
        is_custom=person.is_custom,
    )


@router.delete("/people/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).get(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()
```

- [ ] **Step 5: Create stub routers for feed, trends, digest**

Create `backend/api/feed.py`:

```python
from fastapi import APIRouter

router = APIRouter()
```

Create `backend/api/trends.py`:

```python
from fastapi import APIRouter

router = APIRouter()
```

Create `backend/api/digest.py`:

```python
from fastapi import APIRouter

router = APIRouter()
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_api/test_people.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add backend/main.py backend/api/ tests/test_api/
git commit -m "feat: add FastAPI app with people and categories CRUD API"
```

---

### Task 13: Feed API

**Files:**
- Modify: `backend/api/feed.py`
- Test: `tests/test_api/test_feed.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_api/test_feed.py`:

```python
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base, get_db
from backend.main import app
from backend.models import Category, Person, Content


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    cat = Category(name="Builders", sort_order=1)
    session.add(cat)
    session.commit()

    person = Person(name="Karpathy", category_id=cat.id, platform_handles={"x": "karpathy"})
    session.add(person)
    session.commit()

    for i in range(3):
        session.add(
            Content(
                person_id=person.id,
                source_platform="x",
                original_url=f"https://x.com/karpathy/status/{i}",
                raw_text=f"Post {i} about AI",
                ai_summary=f"**So what:** Point {i}\n\n- Detail",
                so_what=f"Point {i}",
                topics=["ai", "llm"],
                published_at=datetime(2026, 4, 5 - i, tzinfo=timezone.utc),
            )
        )
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_feed(client):
    resp = client.get("/api/feed")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    # Sorted by published_at descending
    assert data[0]["so_what"] == "Point 0"


def test_get_feed_filter_by_category(client):
    resp = client.get("/api/feed?category=Builders")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


def test_get_feed_filter_by_platform(client):
    resp = client.get("/api/feed?platform=x")
    assert resp.status_code == 200
    assert len(resp.json()) == 3

    resp = client.get("/api/feed?platform=youtube")
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_get_feed_pagination(client):
    resp = client.get("/api/feed?limit=2&offset=0")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_api/test_feed.py -v`
Expected: FAIL — endpoints not defined

- [ ] **Step 3: Implement backend/api/feed.py**

```python
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.category import Category
from backend.models.content import Content
from backend.models.person import Person

router = APIRouter()


class FeedItem(BaseModel):
    id: int
    person_name: str
    person_id: int
    category_name: str
    source_platform: str
    original_url: str
    ai_summary: str | None
    so_what: str | None
    topics: list[str]
    published_at: datetime | None
    collected_at: datetime
    is_read: bool

    model_config = {"from_attributes": True}


@router.get("/feed", response_model=list[FeedItem])
def get_feed(
    category: str | None = None,
    platform: str | None = None,
    person_id: int | None = None,
    topic: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Content).join(Person).join(Category)

    if category:
        query = query.filter(Category.name == category)
    if platform:
        query = query.filter(Content.source_platform == platform)
    if person_id:
        query = query.filter(Content.person_id == person_id)

    query = query.order_by(Content.published_at.desc().nullslast())
    contents = query.offset(offset).limit(limit).all()

    return [
        FeedItem(
            id=c.id,
            person_name=c.person.name,
            person_id=c.person_id,
            category_name=c.person.category.name,
            source_platform=c.source_platform,
            original_url=c.original_url,
            ai_summary=c.ai_summary,
            so_what=c.so_what,
            topics=c.topics or [],
            published_at=c.published_at,
            collected_at=c.collected_at,
            is_read=c.is_read,
        )
        for c in contents
    ]


@router.patch("/feed/{content_id}/read")
def mark_as_read(content_id: int, db: Session = Depends(get_db)):
    content = db.query(Content).get(content_id)
    if not content:
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    content.is_read = True
    db.commit()
    return {"status": "ok"}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_api/test_feed.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/api/feed.py tests/test_api/test_feed.py
git commit -m "feat: add feed API with filtering and pagination"
```

---

### Task 14: Trends API

**Files:**
- Modify: `backend/api/trends.py`
- Create: `backend/services/analytics.py`
- Test: `tests/test_api/test_trends.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_api/test_trends.py`:

```python
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base, get_db
from backend.main import app
from backend.models.trend import Trend


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    session.add(
        Trend(
            topic="agents",
            description="Agent frameworks gaining traction",
            related_content_ids=[1, 2, 3],
            time_range="7d",
            sentiment_score=0.8,
            momentum_score=0.9,
        )
    )
    session.add(
        Trend(
            topic="fine-tuning",
            description="More teams adopting fine-tuning",
            related_content_ids=[4, 5],
            time_range="7d",
            sentiment_score=0.6,
            momentum_score=0.5,
        )
    )
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_trends(client):
    resp = client.get("/api/trends")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    # Sorted by momentum descending
    assert data[0]["topic"] == "agents"


def test_get_trends_filter_by_time_range(client):
    resp = client.get("/api/trends?time_range=7d")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_api/test_trends.py -v`
Expected: FAIL — endpoints not defined

- [ ] **Step 3: Implement backend/api/trends.py**

```python
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.trend import Trend

router = APIRouter()


class TrendResponse(BaseModel):
    id: int
    topic: str
    description: str
    related_content_ids: list[int]
    detected_at: datetime
    time_range: str
    sentiment_score: float
    momentum_score: float

    model_config = {"from_attributes": True}


@router.get("/trends", response_model=list[TrendResponse])
def get_trends(
    time_range: str | None = None,
    limit: int = Query(default=20, le=50),
    db: Session = Depends(get_db),
):
    query = db.query(Trend)
    if time_range:
        query = query.filter(Trend.time_range == time_range)
    trends = query.order_by(Trend.momentum_score.desc()).limit(limit).all()
    return trends
```

- [ ] **Step 4: Create backend/services/analytics.py**

```python
import json
import logging

from sqlalchemy.orm import Session

from backend.llm.base import LLMProvider
from backend.models.content import Content
from backend.models.trend import Trend

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def detect_trends(self, db: Session, time_range: str = "7d") -> list[Trend]:
        """Analyze recent content and detect trending topics."""
        contents = db.query(Content).filter(Content.ai_summary.isnot(None)).limit(100).all()

        if not contents:
            return []

        # Format content for LLM analysis
        formatted = "\n\n".join(
            f"[{c.id}] {c.person.name} ({c.source_platform}): {c.ai_summary}"
            for c in contents
        )

        try:
            result = await self.llm.analyze_trends(formatted, time_range)
            trends_data = json.loads(result)
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Trend analysis failed: {e}")
            return []

        # Clear old trends for this time range and insert new ones
        db.query(Trend).filter(Trend.time_range == time_range).delete()

        new_trends = []
        for t in trends_data:
            trend = Trend(
                topic=t["topic"],
                description=t["description"],
                related_content_ids=t.get("related_content_ids", []),
                time_range=time_range,
                sentiment_score=t.get("sentiment_score", 0.0),
                momentum_score=t.get("momentum_score", 0.0),
            )
            db.add(trend)
            new_trends.append(trend)

        db.commit()
        return new_trends
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_api/test_trends.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/api/trends.py backend/services/analytics.py tests/test_api/test_trends.py
git commit -m "feat: add trends API and analytics service"
```

---

### Task 15: Digest API

**Files:**
- Modify: `backend/api/digest.py`
- Create: `backend/services/digest.py`
- Test: `tests/test_api/test_digest.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_api/test_digest.py`:

```python
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base, get_db
from backend.main import app
from backend.models import Category, Person, Content


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    cat = Category(name="Builders", sort_order=1)
    session.add(cat)
    session.commit()

    person = Person(name="Karpathy", category_id=cat.id, platform_handles={"x": "karpathy"})
    session.add(person)
    session.commit()

    session.add(
        Content(
            person_id=person.id,
            source_platform="x",
            original_url="https://x.com/karpathy/status/1",
            raw_text="Fine-tuning is great",
            ai_summary="**So what:** Fine-tuning works.\n\n- Simple\n- Effective",
            so_what="Fine-tuning works",
            topics=["fine-tuning"],
            published_at=datetime(2026, 4, 5, tzinfo=timezone.utc),
        )
    )
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_get_digest(client):
    resp = client.get("/api/digest")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert data["items"][0]["so_what"] is not None
    assert data["items"][0]["original_url"] is not None


def test_get_digest_by_category(client):
    resp = client.get("/api/digest?category=Builders")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_api/test_digest.py -v`
Expected: FAIL — endpoints not defined

- [ ] **Step 3: Create backend/services/digest.py**

```python
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models.category import Category
from backend.models.content import Content
from backend.models.person import Person


def build_digest(db: Session, category: str | None = None, days: int = 1) -> dict:
    """Build a digest of recent summarized content."""
    query = (
        db.query(Content)
        .join(Person)
        .join(Category)
        .filter(Content.ai_summary.isnot(None))
    )

    if category:
        query = query.filter(Category.name == category)

    contents = query.order_by(Content.published_at.desc().nullslast()).limit(50).all()

    items = [
        {
            "person_name": c.person.name,
            "category_name": c.person.category.name,
            "source_platform": c.source_platform,
            "original_url": c.original_url,
            "so_what": c.so_what,
            "ai_summary": c.ai_summary,
            "topics": c.topics or [],
            "published_at": c.published_at.isoformat() if c.published_at else None,
        }
        for c in contents
    ]

    return {"items": items, "count": len(items)}
```

- [ ] **Step 4: Implement backend/api/digest.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.digest import build_digest

router = APIRouter()


@router.get("/digest")
def get_digest(
    category: str | None = None,
    days: int = 1,
    db: Session = Depends(get_db),
):
    return build_digest(db, category=category, days=days)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/test_api/test_digest.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add backend/api/digest.py backend/services/digest.py tests/test_api/test_digest.py
git commit -m "feat: add digest API and service"
```

---

## Phase 5: Scheduler

### Task 16: APScheduler Integration

**Files:**
- Create: `backend/scheduler.py`
- Test: `tests/test_scheduler.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_scheduler.py`:

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend.scheduler import create_scheduler, run_collection_job, run_summarization_job


def test_create_scheduler():
    scheduler = create_scheduler(interval_hours=6)
    assert scheduler is not None
    jobs = scheduler.get_jobs()
    assert len(jobs) == 3  # collection, summarization, trends
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_scheduler.py -v`
Expected: FAIL — cannot import backend.scheduler

- [ ] **Step 3: Create backend/scheduler.py**

```python
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.collectors.rss import RSSCollector
from backend.collectors.reddit import RedditCollector
from backend.collectors.youtube import YouTubeCollector
from backend.collectors.twitter import TwitterCollector
from backend.config import settings
from backend.llm.claude_provider import ClaudeProvider
from backend.services.collector_service import CollectorService
from backend.services.summarizer import SummarizerService
from backend.services.analytics import AnalyticsService

logger = logging.getLogger(__name__)


def _get_sync_db() -> Session:
    sync_url = settings.database_url.replace("+aiosqlite", "")
    engine = create_engine(sync_url)
    return Session(engine)


def _get_collectors() -> dict:
    collectors = {
        "substack": RSSCollector(),
        "reddit": RedditCollector(),
    }
    if settings.youtube_api_key:
        collectors["youtube"] = YouTubeCollector(api_key=settings.youtube_api_key)
    if settings.x_api_bearer_token:
        collectors["x"] = TwitterCollector(bearer_token=settings.x_api_bearer_token)
    return collectors


async def run_collection_job():
    logger.info("Starting scheduled collection...")
    db = _get_sync_db()
    try:
        service = CollectorService(collectors=_get_collectors())
        new_content = await service.collect_all(db)
        logger.info(f"Collected {len(new_content)} new items")
    finally:
        db.close()


async def run_summarization_job():
    logger.info("Starting scheduled summarization...")
    if not settings.anthropic_api_key:
        logger.warning("No Anthropic API key configured, skipping summarization")
        return
    db = _get_sync_db()
    try:
        llm = ClaudeProvider(api_key=settings.anthropic_api_key)
        service = SummarizerService(llm=llm)
        count = await service.summarize_pending(db)
        logger.info(f"Summarized {count} items")
    finally:
        db.close()


async def run_trend_analysis_job():
    logger.info("Starting scheduled trend analysis...")
    if not settings.anthropic_api_key:
        return
    db = _get_sync_db()
    try:
        llm = ClaudeProvider(api_key=settings.anthropic_api_key)
        service = AnalyticsService(llm=llm)
        trends = await service.detect_trends(db)
        logger.info(f"Detected {len(trends)} trends")
    finally:
        db.close()


def create_scheduler(interval_hours: int = 6) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_collection_job, "interval", hours=interval_hours, id="collection")
    scheduler.add_job(
        run_summarization_job, "interval", hours=interval_hours, minutes=15, id="summarization"
    )
    scheduler.add_job(run_trend_analysis_job, "interval", hours=24, id="trends")
    return scheduler
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_scheduler.py -v`
Expected: All 1 test PASS.

- [ ] **Step 5: Wire scheduler into FastAPI lifespan**

Update `backend/main.py` lifespan:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import init_db
from backend.scheduler import create_scheduler
from backend.api.people import router as people_router
from backend.api.feed import router as feed_router
from backend.api.trends import router as trends_router
from backend.api.digest import router as digest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler = create_scheduler(interval_hours=settings.collection_interval_hours)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Info Tracker", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(people_router, prefix="/api")
app.include_router(feed_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
app.include_router(digest_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 6: Add manual refresh endpoint to feed API**

Add to `backend/api/feed.py`:

```python
@router.post("/collect/refresh")
async def refresh_collection(db: Session = Depends(get_db)):
    from backend.scheduler import _get_collectors
    from backend.services.collector_service import CollectorService

    service = CollectorService(collectors=_get_collectors())
    new_content = await service.collect_all(db)
    return {"new_items": len(new_content)}
```

- [ ] **Step 7: Commit**

```bash
git add backend/scheduler.py backend/main.py backend/api/feed.py tests/test_scheduler.py
git commit -m "feat: add APScheduler with collection, summarization, and trend jobs"
```

---

## Phase 6: Frontend

### Task 17: Scaffold React Frontend

**Files:**
- Create: `frontend/` (via Vite scaffolding)
- Modify: `frontend/package.json` (add Tailwind, react-router, recharts)

- [ ] **Step 1: Scaffold with Vite**

Run:
```bash
cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker
npm create vite@latest frontend -- --template react-ts
```
Expected: Vite creates the frontend directory with React + TypeScript template.

- [ ] **Step 2: Install dependencies**

Run:
```bash
cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker/frontend
npm install
npm install -D tailwindcss @tailwindcss/vite
npm install react-router-dom recharts
```
Expected: All packages install successfully.

- [ ] **Step 3: Configure Tailwind**

Replace `frontend/src/index.css` with:

```css
@import "tailwindcss";
```

Update `frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
```

- [ ] **Step 4: Commit**

```bash
cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker
git add frontend/
git commit -m "feat: scaffold React frontend with Vite, Tailwind, and recharts"
```

---

### Task 18: API Client & Types

**Files:**
- Create: `frontend/src/api.ts`
- Create: `frontend/src/types.ts`

- [ ] **Step 1: Create frontend/src/types.ts**

```typescript
export interface Category {
  id: number
  name: string
  description: string | null
  is_custom: boolean
  sort_order: number
}

export interface Person {
  id: number
  name: string
  bio: string | null
  avatar_url: string | null
  category_name: string
  platform_handles: Record<string, string>
  is_custom: boolean
}

export interface FeedItem {
  id: number
  person_name: string
  person_id: number
  category_name: string
  source_platform: string
  original_url: string
  ai_summary: string | null
  so_what: string | null
  topics: string[]
  published_at: string | null
  collected_at: string
  is_read: boolean
}

export interface Trend {
  id: number
  topic: string
  description: string
  related_content_ids: number[]
  detected_at: string
  time_range: string
  sentiment_score: number
  momentum_score: number
}

export interface Digest {
  items: DigestItem[]
  count: number
}

export interface DigestItem {
  person_name: string
  category_name: string
  source_platform: string
  original_url: string
  so_what: string | null
  ai_summary: string | null
  topics: string[]
  published_at: string | null
}
```

- [ ] **Step 2: Create frontend/src/api.ts**

```typescript
import type { Category, Person, FeedItem, Trend, Digest } from './types'

const BASE = '/api'

async function fetchJSON<T>(url: string): Promise<T> {
  const resp = await fetch(`${BASE}${url}`)
  if (!resp.ok) throw new Error(`API error: ${resp.status}`)
  return resp.json()
}

export const api = {
  getCategories: () => fetchJSON<Category[]>('/categories'),
  getPeople: (category?: string) =>
    fetchJSON<Person[]>(category ? `/people?category=${category}` : '/people'),
  addPerson: async (data: { name: string; bio?: string; category_name: string; platform_handles: Record<string, string> }) => {
    const resp = await fetch(`${BASE}/people`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!resp.ok) throw new Error(`API error: ${resp.status}`)
    return resp.json() as Promise<Person>
  },
  deletePerson: async (id: number) => {
    await fetch(`${BASE}/people/${id}`, { method: 'DELETE' })
  },
  getFeed: (params?: { category?: string; platform?: string; limit?: number; offset?: number }) => {
    const qs = new URLSearchParams()
    if (params?.category) qs.set('category', params.category)
    if (params?.platform) qs.set('platform', params.platform)
    if (params?.limit) qs.set('limit', String(params.limit))
    if (params?.offset) qs.set('offset', String(params.offset))
    const query = qs.toString()
    return fetchJSON<FeedItem[]>(`/feed${query ? `?${query}` : ''}`)
  },
  getTrends: (timeRange?: string) =>
    fetchJSON<Trend[]>(timeRange ? `/trends?time_range=${timeRange}` : '/trends'),
  getDigest: (category?: string) =>
    fetchJSON<Digest>(category ? `/digest?category=${category}` : '/digest'),
  refreshCollection: async () => {
    const resp = await fetch(`${BASE}/collect/refresh`, { method: 'POST' })
    return resp.json()
  },
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/types.ts frontend/src/api.ts
git commit -m "feat: add TypeScript types and API client"
```

---

### Task 19: App Layout & Routing

**Files:**
- Modify: `frontend/src/App.tsx`
- Create: `frontend/src/pages/Feed.tsx`
- Create: `frontend/src/pages/Trends.tsx`
- Create: `frontend/src/pages/People.tsx`
- Create: `frontend/src/pages/Settings.tsx`

- [ ] **Step 1: Create frontend/src/App.tsx**

```tsx
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import Feed from './pages/Feed'
import Trends from './pages/Trends'
import People from './pages/People'
import Settings from './pages/Settings'

const navItems = [
  { to: '/', label: 'Feed' },
  { to: '/trends', label: 'Trends' },
  { to: '/people', label: 'People' },
  { to: '/settings', label: 'Settings' },
]

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950 text-gray-100">
        <nav className="border-b border-gray-800 px-6 py-3 flex items-center gap-6">
          <span className="text-lg font-semibold text-white">Info Tracker</span>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `text-sm ${isActive ? 'text-white font-medium' : 'text-gray-400 hover:text-gray-200'}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <main className="max-w-6xl mx-auto px-6 py-6">
          <Routes>
            <Route path="/" element={<Feed />} />
            <Route path="/trends" element={<Trends />} />
            <Route path="/people" element={<People />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
```

- [ ] **Step 2: Create frontend/src/pages/Feed.tsx**

```tsx
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { FeedItem, Category } from '../types'
import ContentCard from '../components/ContentCard'
import CategoryFilter from '../components/CategoryFilter'

export default function Feed() {
  const [items, setItems] = useState<FeedItem[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getCategories().then(setCategories)
  }, [])

  useEffect(() => {
    setLoading(true)
    api.getFeed({ category: selectedCategory }).then((data) => {
      setItems(data)
      setLoading(false)
    })
  }, [selectedCategory])

  const handleRefresh = async () => {
    setLoading(true)
    await api.refreshCollection()
    const data = await api.getFeed({ category: selectedCategory })
    setItems(data)
    setLoading(false)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Feed</h1>
        <button
          onClick={handleRefresh}
          className="px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 rounded-md"
        >
          Refresh
        </button>
      </div>
      <CategoryFilter
        categories={categories}
        selected={selectedCategory}
        onSelect={setSelectedCategory}
      />
      {loading ? (
        <p className="text-gray-500 mt-8">Loading...</p>
      ) : items.length === 0 ? (
        <p className="text-gray-500 mt-8">No content yet. Try refreshing to collect data.</p>
      ) : (
        <div className="space-y-4 mt-4">
          {items.map((item) => (
            <ContentCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Create frontend/src/pages/Trends.tsx**

```tsx
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Trend } from '../types'
import TrendChart from '../components/TrendChart'

export default function Trends() {
  const [trends, setTrends] = useState<Trend[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getTrends().then((data) => {
      setTrends(data)
      setLoading(false)
    })
  }, [])

  if (loading) return <p className="text-gray-500">Loading trends...</p>

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Trending Topics</h1>
      {trends.length === 0 ? (
        <p className="text-gray-500">No trends detected yet. Check back after more content is collected.</p>
      ) : (
        <>
          <TrendChart trends={trends} />
          <div className="space-y-4 mt-8">
            {trends.map((trend) => (
              <div key={trend.id} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-white">{trend.topic}</h3>
                  <div className="flex gap-3 text-xs text-gray-400">
                    <span>Momentum: {(trend.momentum_score * 100).toFixed(0)}%</span>
                    <span>Sentiment: {trend.sentiment_score > 0 ? '+' : ''}{trend.sentiment_score.toFixed(1)}</span>
                  </div>
                </div>
                <p className="text-sm text-gray-300">{trend.description}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Create frontend/src/pages/People.tsx**

```tsx
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { Person, Category } from '../types'
import PersonManager from '../components/PersonManager'
import CategoryFilter from '../components/CategoryFilter'

export default function People() {
  const [people, setPeople] = useState<Person[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>()

  const loadPeople = () => {
    api.getPeople(selectedCategory).then(setPeople)
  }

  useEffect(() => {
    api.getCategories().then(setCategories)
  }, [])

  useEffect(() => {
    loadPeople()
  }, [selectedCategory])

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">People</h1>
      <CategoryFilter
        categories={categories}
        selected={selectedCategory}
        onSelect={setSelectedCategory}
      />
      <PersonManager
        people={people}
        categories={categories}
        onUpdate={loadPeople}
      />
    </div>
  )
}
```

- [ ] **Step 5: Create frontend/src/pages/Settings.tsx**

```tsx
export default function Settings() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <p className="text-gray-400 text-sm">
          Configure API keys and collection schedules in <code className="text-gray-300">.env</code> file.
          Restart the backend to apply changes.
        </p>
        <div className="mt-4 space-y-3 text-sm">
          <div>
            <span className="text-gray-400">Backend: </span>
            <code className="text-gray-300">uvicorn backend.main:app --reload</code>
          </div>
          <div>
            <span className="text-gray-400">Frontend: </span>
            <code className="text-gray-300">cd frontend && npm run dev</code>
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Remove default Vite boilerplate**

Delete `frontend/src/App.css` and `frontend/src/assets/` if they exist. Update `frontend/src/main.tsx`:

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/
git commit -m "feat: add app layout, routing, and page components"
```

---

### Task 20: Frontend Components

**Files:**
- Create: `frontend/src/components/ContentCard.tsx`
- Create: `frontend/src/components/CategoryFilter.tsx`
- Create: `frontend/src/components/TrendChart.tsx`
- Create: `frontend/src/components/PersonManager.tsx`

- [ ] **Step 1: Create frontend/src/components/ContentCard.tsx**

```tsx
import type { FeedItem } from '../types'

const platformColors: Record<string, string> = {
  x: 'text-blue-400',
  youtube: 'text-red-400',
  substack: 'text-orange-400',
  reddit: 'text-yellow-400',
}

export default function ContentCard({ item }: { item: FeedItem }) {
  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-medium text-white">{item.person_name}</span>
          <span className="text-xs text-gray-500">{item.category_name}</span>
          <span className={`text-xs ${platformColors[item.source_platform] || 'text-gray-400'}`}>
            {item.source_platform}
          </span>
        </div>
        {item.published_at && (
          <span className="text-xs text-gray-500">
            {new Date(item.published_at).toLocaleDateString()}
          </span>
        )}
      </div>

      {item.so_what && (
        <p className="text-sm font-medium text-gray-200 mb-2">{item.so_what}</p>
      )}

      {item.ai_summary && (
        <p className="text-sm text-gray-400 mb-3 whitespace-pre-line">{item.ai_summary}</p>
      )}

      <div className="flex items-center justify-between">
        <div className="flex gap-1.5">
          {item.topics.map((topic) => (
            <span key={topic} className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded">
              {topic}
            </span>
          ))}
        </div>
        <a
          href={item.original_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-blue-400 hover:text-blue-300"
        >
          Source
        </a>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create frontend/src/components/CategoryFilter.tsx**

```tsx
import type { Category } from '../types'

interface Props {
  categories: Category[]
  selected: string | undefined
  onSelect: (category: string | undefined) => void
}

export default function CategoryFilter({ categories, selected, onSelect }: Props) {
  return (
    <div className="flex gap-2 mb-4">
      <button
        onClick={() => onSelect(undefined)}
        className={`px-3 py-1 text-sm rounded-md ${
          !selected ? 'bg-gray-700 text-white' : 'bg-gray-900 text-gray-400 hover:text-gray-200'
        }`}
      >
        All
      </button>
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onSelect(cat.name)}
          className={`px-3 py-1 text-sm rounded-md ${
            selected === cat.name ? 'bg-gray-700 text-white' : 'bg-gray-900 text-gray-400 hover:text-gray-200'
          }`}
        >
          {cat.name}
        </button>
      ))}
    </div>
  )
}
```

- [ ] **Step 3: Create frontend/src/components/TrendChart.tsx**

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { Trend } from '../types'

export default function TrendChart({ trends }: { trends: Trend[] }) {
  const data = trends.map((t) => ({
    name: t.topic,
    momentum: Math.round(t.momentum_score * 100),
    sentiment: Math.round((t.sentiment_score + 1) * 50), // normalize -1..1 to 0..100
  }))

  return (
    <div className="bg-gray-900 rounded-lg p-4 border border-gray-800">
      <h3 className="text-sm font-medium text-gray-400 mb-4">Topic Momentum</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
            labelStyle={{ color: '#f3f4f6' }}
          />
          <Bar dataKey="momentum" fill="#3b82f6" name="Momentum %" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
```

- [ ] **Step 4: Create frontend/src/components/PersonManager.tsx**

```tsx
import { useState } from 'react'
import { api } from '../api'
import type { Person, Category } from '../types'

interface Props {
  people: Person[]
  categories: Category[]
  onUpdate: () => void
}

export default function PersonManager({ people, categories, onUpdate }: Props) {
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [bio, setBio] = useState('')
  const [categoryName, setCategoryName] = useState('')
  const [handles, setHandles] = useState<Record<string, string>>({ x: '', youtube: '', substack: '', reddit: '' })

  const handleAdd = async () => {
    if (!name || !categoryName) return
    const platform_handles: Record<string, string> = {}
    for (const [k, v] of Object.entries(handles)) {
      if (v.trim()) platform_handles[k] = v.trim()
    }
    await api.addPerson({ name, bio, category_name: categoryName, platform_handles })
    setName('')
    setBio('')
    setHandles({ x: '', youtube: '', substack: '', reddit: '' })
    setShowForm(false)
    onUpdate()
  }

  const handleDelete = async (id: number) => {
    await api.deletePerson(id)
    onUpdate()
  }

  return (
    <div className="mt-4">
      <button
        onClick={() => setShowForm(!showForm)}
        className="px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-500 rounded-md mb-4"
      >
        {showForm ? 'Cancel' : '+ Add Person'}
      </button>

      {showForm && (
        <div className="bg-gray-900 rounded-lg p-4 border border-gray-800 mb-4 space-y-3">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm"
          />
          <input
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Bio (optional)"
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm"
          />
          <select
            value={categoryName}
            onChange={(e) => setCategoryName(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm"
          >
            <option value="">Select category</option>
            {categories.map((c) => (
              <option key={c.id} value={c.name}>{c.name}</option>
            ))}
          </select>
          <div className="grid grid-cols-2 gap-2">
            {Object.keys(handles).map((platform) => (
              <input
                key={platform}
                value={handles[platform]}
                onChange={(e) => setHandles({ ...handles, [platform]: e.target.value })}
                placeholder={`${platform} handle`}
                className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm"
              />
            ))}
          </div>
          <button onClick={handleAdd} className="px-3 py-1.5 text-sm bg-green-600 hover:bg-green-500 rounded-md">
            Save
          </button>
        </div>
      )}

      <div className="space-y-2">
        {people.map((p) => (
          <div key={p.id} className="flex items-center justify-between bg-gray-900 rounded-lg px-4 py-3 border border-gray-800">
            <div>
              <span className="font-medium text-white">{p.name}</span>
              <span className="text-xs text-gray-500 ml-2">{p.category_name}</span>
              {p.bio && <p className="text-xs text-gray-400 mt-0.5">{p.bio}</p>}
              <div className="flex gap-2 mt-1">
                {Object.entries(p.platform_handles).map(([platform, handle]) => (
                  <span key={platform} className="text-xs text-gray-500">{platform}: {handle}</span>
                ))}
              </div>
            </div>
            <button
              onClick={() => handleDelete(p.id)}
              className="text-xs text-red-400 hover:text-red-300"
            >
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Verify frontend builds**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker/frontend && npm run build`
Expected: Build succeeds with no TypeScript errors.

- [ ] **Step 6: Commit**

```bash
cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker
git add frontend/src/components/
git commit -m "feat: add ContentCard, CategoryFilter, TrendChart, PersonManager components"
```

---

## Phase 7: Claude Code Skill

### Task 21: Claude Code Skill

**Files:**
- Create: `.claude/skills/info-tracker/SKILL.md`

- [ ] **Step 1: Create .claude/skills/info-tracker/SKILL.md**

```markdown
---
name: info-tracker
description: Query your AI ecosystem tracker — get latest content, digests, trends, and manage tracked people. Use when asking about AI builders, investors, researchers, or their content.
user-invocable: true
allowed-tools: Bash(curl *)
---

# Info Tracker Skill

Query your local Info Tracker instance (FastAPI at http://127.0.0.1:8000).

## Commands

Based on `$ARGUMENTS`, perform ONE of these actions:

### "today" or "digest" (default)
Fetch today's digest:
```bash
curl -s http://127.0.0.1:8000/api/digest
```
Format the response as a structured briefing using pyramid principle:
- Lead with top 3-5 takeaways across all categories
- Then list by person: **Name**: so_what — [Source](url)
- Skip items with no summary

### "digest <Category>"
Fetch digest for a specific category:
```bash
curl -s "http://127.0.0.1:8000/api/digest?category=$1"
```
Format the same way as above.

### "trends"
Fetch current trends:
```bash
curl -s http://127.0.0.1:8000/api/trends
```
Format as:
- **Topic** (momentum: X%, sentiment: +/-Y) — description

### "add <handle> <Category>"
Add a new person:
```bash
curl -s -X POST http://127.0.0.1:8000/api/people \
  -H "Content-Type: application/json" \
  -d '{"name": "$1", "category_name": "$2", "platform_handles": {}}'
```
Confirm the addition. Ask the user for platform handles to add.

### "remove <id>"
Delete a person:
```bash
curl -s -X DELETE "http://127.0.0.1:8000/api/people/$1"
```

### "refresh"
Trigger manual collection:
```bash
curl -s -X POST http://127.0.0.1:8000/api/collect/refresh
```
Report how many new items were collected.

### "status"
Health check:
```bash
curl -s http://127.0.0.1:8000/api/health
```

### "people" or "list"
List all tracked people:
```bash
curl -s http://127.0.0.1:8000/api/people
```
Format as a table grouped by category.

## Error Handling

If curl fails or returns an error, tell the user:
- Check that the backend is running: `uvicorn backend.main:app --reload`
- Check that they're in the info-tracker project directory

## Formatting Rules

All output follows the pyramid principle:
1. Lead with the conclusion / most important thing
2. Supporting details as bullets
3. Source URLs always included
```

- [ ] **Step 2: Commit**

```bash
git add .claude/
git commit -m "feat: add Claude Code skill for info-tracker"
```

---

## Phase 8: Integration & Polish

### Task 22: End-to-End Wiring & Seed on Startup

**Files:**
- Modify: `backend/main.py`

- [ ] **Step 1: Update backend/main.py to seed on startup**

Update the lifespan function in `backend/main.py`:

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import init_db
from backend.scheduler import create_scheduler
from backend.seed import seed_database
from backend.api.people import router as people_router
from backend.api.feed import router as feed_router
from backend.api.trends import router as trends_router
from backend.api.digest import router as digest_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    # Seed preset data
    sync_url = settings.database_url.replace("+aiosqlite", "")
    engine = create_engine(sync_url)
    with Session(engine) as db:
        seed_database(db)

    scheduler = create_scheduler(interval_hours=settings.collection_interval_hours)
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Info Tracker", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(people_router, prefix="/api")
app.include_router(feed_router, prefix="/api")
app.include_router(trends_router, prefix="/api")
app.include_router(digest_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 2: Create data/ directory for SQLite**

Run: `mkdir -p /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker/data`

- [ ] **Step 3: Run the full test suite**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker && uv run pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 4: Test the backend starts**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker && uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000`
Expected: Server starts, seeds data, scheduler begins. Verify with `curl http://127.0.0.1:8000/api/health` returning `{"status":"ok"}` and `curl http://127.0.0.1:8000/api/categories` returning 5 categories.

- [ ] **Step 5: Commit**

```bash
git add backend/main.py
git commit -m "feat: seed database on startup and wire scheduler"
```

---

### Task 23: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create README.md**

```markdown
# Info Tracker

Local-first AI ecosystem tracker. Aggregates content from AI builders, researchers, founders, investors, and commentators across X/Twitter, YouTube, Substack, and Reddit. Summarizes with Claude API using pyramid-principle formatting. Includes a web dashboard and Claude Code skill.

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- [uv](https://github.com/astral-sh/uv) (Python package manager)

### Setup

```bash
# Clone and enter project
cd info-tracker

# Copy and edit env
cp .env.example .env
# Add your ANTHROPIC_API_KEY (required) and optional platform keys

# Install Python deps
uv venv && uv pip install -e ".[dev]"

# Start backend
uv run uvicorn backend.main:app --reload

# In another terminal — start frontend
cd frontend && npm install && npm run dev
```

Open http://localhost:5173

### Claude Code Skill

From any Claude Code session in this project:

```
/info-tracker today          # Today's digest
/info-tracker trends         # Trending topics
/info-tracker people         # List tracked people
/info-tracker add "Name" Builders  # Add someone
/info-tracker refresh        # Manual collection
```

### Channels (Notifications)

Set up Claude Code Channels for Telegram/Discord/iMessage delivery:

```bash
/plugin install telegram@claude-plugins-official
/telegram:configure <bot-token>
claude --channels plugin:telegram@claude-plugins-official
```

Then ask: "Send me today's info-tracker digest"

## Architecture

- **Backend**: FastAPI + SQLite + APScheduler
- **Frontend**: React + Vite + Tailwind
- **AI**: Claude API (pluggable via LLMProvider)
- **Skill**: Claude Code skill querying the REST API

## License

MIT
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup and usage instructions"
```

---

### Task 24: Run Full Test Suite & Final Verification

- [ ] **Step 1: Run all tests**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker && uv run pytest tests/ -v --tb=short`
Expected: All tests PASS.

- [ ] **Step 2: Verify frontend builds**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker/frontend && npm run build`
Expected: Build succeeds.

- [ ] **Step 3: Verify backend starts and serves API**

Run: `cd /Users/sunsiyuan/Downloads/Calude_Cowork_Master/info-tracker && timeout 10 uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000 || true`
Then: `curl -s http://127.0.0.1:8000/api/health` should return `{"status":"ok"}`

- [ ] **Step 4: Final commit if any fixes needed**

```bash
git add -A && git commit -m "fix: address issues found during final verification"
```
