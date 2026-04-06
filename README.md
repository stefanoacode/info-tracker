# Info Tracker

A Claude Code skill that tracks AI ecosystem influencers across X/Twitter, YouTube, Substack, and Reddit. Collects first-hand content and Claude summarizes it directly — no API keys required for basic use.

## Setup

```bash
cd info-tracker
cp .env.example .env
# Optionally add YOUTUBE_API_KEY and X_API_BEARER_TOKEN
# RSS/Substack and Reddit work without any keys

uv venv && uv pip install -e .
```

## Usage

All commands via the Claude Code skill:

```
/info-tracker collect             # Fetch content from all platforms
/info-tracker                     # Claude reads + summarizes collected content
/info-tracker digest Builders     # Digest for a specific category
/info-tracker trends              # Claude identifies trending topics

/info-tracker people              # List tracked people
/info-tracker add "Name" "Category" --x handle --youtube channel_id --substack feed_url
/info-tracker update "Name" --reddit username
/info-tracker remove "Name"

/info-tracker categories          # List categories
/info-tracker status              # System status
```

## License

MIT
