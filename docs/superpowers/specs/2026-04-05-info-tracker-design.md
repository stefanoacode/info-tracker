# Info Tracker — Design Spec

**Date:** 2026-04-05
**Status:** Draft
**Author:** Co-designed with Claude

## Overview

Info Tracker is a local-first application that aggregates and summarizes first-hand content from key people in the AI ecosystem. It replaces relying on second-hand news by going straight to the source — tracking builders, researchers, founders, investors, and commentators across X/Twitter, YouTube, Substack/blogs, and Reddit.

The system consists of three components:
1. **FastAPI backend** — data collection, AI summarization, analytics, REST API
2. **React frontend** — minimalist read-only dashboard with trend analytics
3. **Claude Code skill** — query digests, trends, and manage people from the terminal; deliver notifications via Claude Code Channels (Telegram, Discord, iMessage)

## Goals

- Consume first-hand information directly from source, not n-th hand news
- Track anyone across multiple platforms with custom categories
- Get crisp, pyramid-principle summaries with actionable "so what" and source URLs
- Detect trends and topic momentum across the ecosystem
- Deliver digests via Claude Code Channels (Telegram, Discord, iMessage)
- Publishable on GitHub for others to use

## Non-Goals

- Social features (comments, sharing, upvoting)
- User accounts / multi-tenancy — this is a personal tool
- Cloud deployment (local-first, SQLite)
- Real-time streaming (scheduled + on-demand refresh)

---

## Categories (MECE)

Predefined categories covering the AI ecosystem. Users can add/remove people and create custom categories.

| Category | Description | Examples |
|----------|-------------|---------|
| **Builders** | Engineers, PMs, designers shipping AI products | Karpathy, Simon Willison, Swyx |
| **Researchers** | Scientists publishing papers, pushing SOTA | Ilya Sutskever, Yann LeCun, Sasha Rush |
| **Founders** | CEO/CTOs of AI-native startups | Dario Amodei, Sam Altman, Arthur Mensch |
| **Investors** | VCs and angels actively funding AI | Elad Gil, Sarah Guo, Vinod Khosla |
| **Commentators** | Journalists, analysts, policy thinkers covering AI | Zvi Mowshowitz, Gary Marcus, Jack Clark |

Each person belongs to one primary category. Content surfaces across categories via topic tags.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Claude Code Skill               │
│    (queries API, returns summaries, sends via    │
│     Channels: Telegram / Discord / iMessage)     │
└──────────────────────┬──────────────────────────┘
                       │ HTTP (localhost)
┌──────────────────────▼──────────────────────────┐
│              FastAPI Backend (Python)             │
│                                                  │
│  ┌──────────┐ ┌───────────┐ ┌────────────────┐  │
│  │ REST API │ │ Scheduler │ │ AI Summarizer  │  │
│  │ /api/*   │ │ APScheduler│ │ (Claude API)   │  │
│  └──────────┘ └───────────┘ └────────────────┘  │
│  ┌──────────┐ ┌───────────┐                      │
│  │Collectors│ │ Analytics │                      │
│  │X/YT/RSS/ │ │ Trends &  │                      │
│  │Reddit    │ │ Clustering│                      │
│  └──────────┘ └───────────┘                      │
└──────────────────────┬──────────────────────────┘
                       │
              ┌────────▼────────┐
              │  SQLite Database │
              └─────────────────┘

┌─────────────────────────────────────────────────┐
│            React Frontend (Vite + Tailwind)       │
│                                                  │
│  Feed View │ Trends │ People Manager │ Settings   │
└─────────────────────────────────────────────────┘
```

### Key Design Decisions

- **API-first**: The REST API serves the React frontend, Claude Code skill, and any future integrations through the same interface
- **Pluggable collectors**: Each data source is an independent module implementing `BaseCollector`
- **LLM abstraction**: Start with Claude API, swap to OpenAI or local models by implementing the `LLMProvider` protocol
- **Notifications via Channels**: No custom notification infrastructure — Claude Code Channels handle Telegram/Discord/iMessage delivery natively
- **Scheduled + on-demand**: APScheduler runs baseline collection on configurable intervals; manual refresh available per person or category

---

## Data Model

### Person
| Field | Type | Description |
|-------|------|-------------|
| id | int (PK) | Auto-increment |
| name | str | Display name |
| bio | str (nullable) | Short description |
| avatar_url | str (nullable) | Profile image URL |
| category_id | int (FK) | Primary category |
| platform_handles | JSON | `{"x": "@handle", "youtube": "channel_id", "substack": "url", "reddit": "u/name"}` |
| is_custom | bool | User-added vs preset |
| created_at | datetime | |
| updated_at | datetime | |

### Category
| Field | Type | Description |
|-------|------|-------------|
| id | int (PK) | Auto-increment |
| name | str (unique) | Category name |
| description | str (nullable) | What this category covers |
| is_custom | bool | User-created vs preset |
| sort_order | int | Display ordering |

### Content
| Field | Type | Description |
|-------|------|-------------|
| id | int (PK) | Auto-increment |
| person_id | int (FK) | Who created this content |
| source_platform | str | `x`, `youtube`, `substack`, `reddit` |
| original_url | str | Direct link to source |
| raw_text | text | Original content text |
| ai_summary | text (nullable) | Pyramid-principle summary |
| so_what | str (nullable) | One-line actionable takeaway |
| topics | JSON | `["agents", "reasoning", "regulation"]` |
| published_at | datetime | When originally published |
| collected_at | datetime | When we scraped it |
| is_read | bool | Read/unread tracking |

### Trend
| Field | Type | Description |
|-------|------|-------------|
| id | int (PK) | Auto-increment |
| topic | str | Topic name |
| description | text | What's happening with this topic |
| related_content_ids | JSON | Array of content IDs |
| detected_at | datetime | When trend was identified |
| time_range | str | `7d`, `30d` |
| sentiment_score | float | -1.0 to 1.0 |
| momentum_score | float | 0.0 to 1.0 (growing vs fading) |

---

## Collectors

Each collector implements a common interface:

```python
class BaseCollector(ABC):
    async def collect(self, person: Person) -> list[Content]
    async def health_check(self) -> bool
```

| Source | Method | Notes |
|--------|--------|-------|
| **X/Twitter** | Nitter scraping or X API free tier | Free tier: 1,500 reads/month. Nitter as fallback |
| **YouTube** | YouTube Data API v3 | 10,000 units/day free. Transcripts via `youtube-transcript-api` |
| **Substack/Blogs** | RSS/Atom feeds | Free, reliable, no rate limits |
| **Reddit** | Reddit JSON API (`.json` suffix) | Free, no auth needed, ~60 req/min |

- Each collector runs independently — if one source is down, others continue
- Raw content stored first, AI summarization runs as a separate pass
- Manual refresh triggers collection for a single person or entire category

---

## AI Summarization & Analytics

### LLM Abstraction

```python
class LLMProvider(Protocol):
    async def summarize(self, content: str, prompt: str) -> str
    async def extract_topics(self, content: str) -> list[str]
    async def analyze_trends(self, contents: list[str]) -> list[Trend]
```

Start with `ClaudeProvider` (Anthropic SDK). Swap providers by implementing the protocol.

### Summarization Principles

All summaries follow the **pyramid principle**:
1. **Lead with the conclusion** — the "so what" in one line
2. **Key supporting points** — 2-4 bullets, structural, crisp
3. **Source URL** — always included for direct access

No fluff, no restating obvious context. Tell the reader what matters and why.

### Analytics

- **Topic clustering**: Group content across people by topic (e.g., "agents", "reasoning", "regulation")
- **Trend detection**: Topics gaining momentum over a configurable time window (7d/30d)
- **Sentiment & momentum scores**: Is the conversation growing? Positive or critical?
- Computed periodically by the scheduler, stored in the Trend table

---

## Notifications via Claude Code Channels

No custom notification infrastructure. Claude Code Channels (research preview, v2.1.80+) natively support:

- **Telegram** — via BotFather bot token
- **Discord** — via Discord bot
- **iMessage** — macOS native, no external service

### How It Works

1. User sets up a Channel (e.g., `/plugin install telegram@claude-plugins-official`)
2. User starts Claude Code with `--channels plugin:telegram@claude-plugins-official`
3. The scheduler triggers the Claude Code skill at configured intervals
4. The skill fetches the digest from the FastAPI backend and replies through the channel
5. User can also send messages from Telegram/Discord to query the tracker interactively

### Fallback

If Channels are unavailable (e.g., Claude Code not running), the web dashboard is always available. Digests are stored in the database regardless of delivery method.

---

## Claude Code Skill

Located at `.claude/skills/info-tracker/SKILL.md`:

```yaml
---
name: info-tracker
description: Query your AI ecosystem tracker — get latest content, digests, trends, and manage tracked people. Use when asking about AI builders, investors, researchers, or their content.
user-invocable: true
allowed-tools: Bash(curl *)
---
```

### Commands

| Command | Description |
|---------|-------------|
| `/info-tracker today` | Today's digest across all categories |
| `/info-tracker trends` | Current trending topics |
| `/info-tracker digest <Category>` | Digest for a specific category |
| `/info-tracker add <handle> <Category>` | Add a person to track |
| `/info-tracker remove <handle>` | Stop tracking a person |
| `/info-tracker refresh` | Trigger manual data collection |
| `/info-tracker status` | Health check on collectors and last collection times |

The skill calls `curl localhost:8000/api/...` under the hood.

---

## Frontend

**Stack:** React + Vite + Tailwind CSS

**Design principles:** Minimalist, read-only, information-dense. No clutter.

### Pages

| Page | Purpose |
|------|---------|
| **Feed** | Main view. Content cards sorted by time, filterable by category/person/topic. Each card: so-what headline, summary bullets, source link, person avatar + name |
| **Trends** | Topic trend charts (momentum over time), topic clusters, sentiment visualization |
| **People** | Browse/search tracked people. Add/remove/recategorize. Create custom categories |
| **Settings** | Collection schedule config, API key management, notification preferences |

---

## Project Structure

```
info-tracker/
├── README.md
├── pyproject.toml
├── .env.example
├── .claude/
│   └── skills/
│       └── info-tracker/
│           └── SKILL.md
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── person.py
│   │   ├── category.py
│   │   ├── content.py
│   │   ├── trend.py
│   │   └── notification.py
│   ├── collectors/
│   │   ├── base.py
│   │   ├── twitter.py
│   │   ├── youtube.py
│   │   ├── rss.py
│   │   └── reddit.py
│   ├── llm/
│   │   ├── base.py
│   │   └── claude_provider.py
│   ├── services/
│   │   ├── summarizer.py
│   │   ├── analytics.py
│   │   └── digest.py
│   ├── api/
│   │   ├── feed.py
│   │   ├── people.py
│   │   ├── trends.py
│   │   └── digest.py
│   └── scheduler.py
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       │   ├── Feed.tsx
│       │   ├── Trends.tsx
│       │   ├── People.tsx
│       │   └── Settings.tsx
│       └── components/
│           ├── ContentCard.tsx
│           ├── TrendChart.tsx
│           ├── CategoryFilter.tsx
│           └── PersonManager.tsx
├── data/
│   ├── presets/
│   │   ├── builders.json
│   │   ├── researchers.json
│   │   ├── founders.json
│   │   ├── investors.json
│   │   └── commentators.json
│   └── prompts/
│       ├── summarize.md
│       ├── digest.md
│       └── trends.md
└── tests/
    ├── test_collectors/
    ├── test_services/
    └── test_api/
```

---

## Tech Stack Summary

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy, APScheduler |
| Database | SQLite |
| Frontend | React, Vite, TypeScript, Tailwind CSS |
| AI | Anthropic Claude API (pluggable via LLMProvider protocol) |
| Notifications | Claude Code Channels (Telegram, Discord, iMessage) |
| Skill | Claude Code skill (`.claude/skills/info-tracker/SKILL.md`) |
| Package management | uv (Python), npm (frontend) |
