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
