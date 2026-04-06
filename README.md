# Info Tracker

A Claude Code skill that tracks AI ecosystem influencers across X/Twitter, YouTube, Substack, and Reddit. Collects first-hand content, summarizes it with Claude API using pyramid-principle formatting, and delivers digests via Claude Code Channels.

No server, no web app — just a skill.

## Setup

```bash
cd info-tracker
cp .env.example .env
# Add your ANTHROPIC_API_KEY (required for summarization)
# Optionally add YOUTUBE_API_KEY and X_API_BEARER_TOKEN

uv venv && uv pip install -e ".[dev]"
```

## Usage

All commands via the Claude Code skill:

```
/info-tracker                     # Today's digest
/info-tracker collect             # Fetch content from all platforms
/info-tracker summarize           # Summarize with Claude API
/info-tracker trends              # Trending topics

/info-tracker people              # List tracked people
/info-tracker add "Name" "Category" --x handle --youtube channel_id --substack feed_url
/info-tracker update "Name" --reddit username
/info-tracker remove "Name"

/info-tracker categories          # List categories
/info-tracker config              # Show configuration
/info-tracker status              # System status
```

## Channels (Notifications)

For digests via Telegram/Discord/iMessage:

```bash
/plugin install telegram@claude-plugins-official
/telegram:configure <bot-token>
claude --channels plugin:telegram@claude-plugins-official
```

Then from Telegram: "give me my info-tracker digest"

## License

MIT
