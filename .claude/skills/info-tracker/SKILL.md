---
name: info-tracker
description: Track AI ecosystem influencers across X, YouTube, Substack, Reddit. Collect content, get digests, manage who you follow. Use when asking about AI builders, investors, researchers, or their content.
user-invocable: true
allowed-tools: Bash(cd *) Bash(uv run *)
---

# Info Tracker

Track and digest first-hand content from AI builders, researchers, founders, investors, and commentators. No server, no API keys required — Claude summarizes directly.

**Project dir:** `${CLAUDE_SKILL_DIR}/../../..`

All commands run from the project root:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend <command> [args]
```

## Commands

Based on `$ARGUMENTS`, run the matching command:

### "today" or "digest" (default — no arguments)
Fetch recent content and summarize it:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend digest
```
The CLI outputs raw collected content. **You (Claude) then summarize it** using pyramid principle:
1. Lead with top 3-5 takeaways across all content
2. Group by person: **Name** (category): one-line takeaway — [Source](url)
3. Skip trivial or promotional content
4. Always include the source URL

### "digest <Category>"
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend digest <Category>
```
Same summarization approach, filtered to one category.

### "collect" or "refresh"
Collect new content from all tracked people's platforms:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend collect
```
No API keys needed for RSS/Substack and Reddit. YouTube and X require keys in `.env`.

### "trends"
Fetch recent content and analyze trends:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend digest
```
Read the output and identify:
- Topics mentioned by multiple people
- Emerging themes gaining momentum
- Contrarian or surprising takes

Present as: **Topic** — what's happening, who's saying what, with URLs.

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

### "config"
Show configuration:
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend config
```

### "status"
Show system status (people count, content stats, available collectors):
```bash
cd ${CLAUDE_SKILL_DIR}/../../.. && uv run python -m backend status
```

## Workflow

When the user asks for a digest and there's no content yet:
1. `/info-tracker collect` — fetch content from all platforms
2. `/info-tracker today` — Claude reads raw content and summarizes

That's it. No separate summarize step needed.

## Channel Notifications

For scheduled digests via Telegram/Discord/iMessage:
1. Set up Claude Code Channels (e.g., `/plugin install telegram@claude-plugins-official`)
2. Start Claude Code with `--channels`
3. From the channel, ask "give me my info-tracker digest"

## Error Handling

If a command fails:
- RSS/Substack and Reddit work with **no API keys**
- YouTube needs `YOUTUBE_API_KEY` in `.env`
- X/Twitter needs `X_API_BEARER_TOKEN` in `.env`
