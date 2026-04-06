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
