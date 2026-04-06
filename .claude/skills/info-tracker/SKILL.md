---
name: info-tracker
description: Track AI ecosystem influencers across X, YouTube, Substack, Reddit. Collect content, get digests, manage who you follow. Use when asking about AI builders, investors, researchers, or their content.
user-invocable: true
allowed-tools: Bash(cd *) Bash(uv run *)
---

# Info Tracker

Track and digest first-hand content from AI builders, researchers, founders, investors, and commentators. No server needed — runs directly against a local SQLite database.

**Project dir:** `${CLAUDE_SKILL_DIR}/../../..`

All commands run from the project root:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend <command> [args]
```

## Commands

Based on `$ARGUMENTS`, run the matching command:

### "today" or "digest" (default — no arguments)
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend digest
```
Present the output using pyramid principle: lead with what matters most, source URLs always included.

### "digest <Category>"
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend digest <Category>
```

### "collect" or "refresh"
Collect new content from all tracked people's platforms:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend collect
```

### "summarize"
Summarize collected content using Claude API:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend summarize
```

### "trends"
Show trending topics across the ecosystem:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend trends
```

### "people" or "list" [Category]
List all tracked people:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend people [Category]
```

### "add" — Add a person to track
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend add "<Name>" "<Category>" [--x handle] [--youtube channel_id] [--substack feed_url] [--reddit username]
```
- Category is created automatically if it doesn't exist
- Platform flags are optional — add whichever the user provides
- `--youtube` expects a YouTube channel ID (e.g., UCsBjURrPoezykLs9EqgamOA)
- `--substack` expects an RSS/Atom feed URL (e.g., https://example.substack.com/feed)
- `--x` expects a Twitter/X username without @
- `--reddit` expects a Reddit username without u/

If the user says "follow Andrej Karpathy on YouTube", extract the info and run:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend add "Andrej Karpathy" "Builders" --youtube UCsBjURrPoezykLs9EqgamOA
```

If you don't know the channel ID or feed URL, ask the user or help them find it.

### "update" — Update a person's platforms
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend update "<Name or ID>" --youtube <channel_id> --substack <feed_url>
```
Use `--<platform> remove` to untrack a platform.

### "remove" — Stop tracking someone
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend remove "<Name or ID>"
```

### "categories"
List all categories:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend categories
```

### "config" — Show or update configuration
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend config
```
To change digest frequency (for Channel notifications):
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend config frequency <hours>
```

### "status"
Show system status (people count, content stats, available collectors):
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend status
```

## Workflow: Collect + Summarize

When the user asks for a digest and there's no content yet, guide them:
1. `/info-tracker collect` — fetch content from all platforms
2. `/info-tracker summarize` — summarize with Claude API
3. `/info-tracker today` — view the digest

## Channel Notifications

For scheduled digests via Telegram/Discord/iMessage, the user should:
1. Set up Claude Code Channels (e.g., `/plugin install telegram@claude-plugins-official`)
2. Start Claude Code with `--channels`
3. From the channel, ask "give me my info-tracker digest"

The digest frequency in config controls how often to send — use with Claude Code scheduled tasks.

## Error Handling

If a command fails:
- Check that `.env` exists with API keys (`ANTHROPIC_API_KEY` required for summarize)
- Check `YOUTUBE_API_KEY` is set for YouTube collection
- Check `X_API_BEARER_TOKEN` is set for Twitter/X collection
- RSS/Substack and Reddit work without API keys
