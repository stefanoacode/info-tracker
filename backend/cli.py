"""CLI for info-tracker. Called by the Claude Code skill."""
import asyncio
import json
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import Base, ensure_data_dir
from backend.models import Category, Person, Content, Trend
from backend.seed import seed_database


def get_db() -> Session:
    ensure_data_dir()
    engine = create_engine(settings.database_url, echo=False)
    Base.metadata.create_all(engine)
    session = Session(engine)
    seed_database(session)
    return session


def get_collectors() -> dict:
    from backend.collectors.rss import RSSCollector
    from backend.collectors.reddit import RedditCollector
    from backend.collectors.youtube import YouTubeCollector
    from backend.collectors.twitter import TwitterCollector

    collectors = {"substack": RSSCollector(), "reddit": RedditCollector()}
    if settings.youtube_api_key:
        collectors["youtube"] = YouTubeCollector(api_key=settings.youtube_api_key)
    if settings.x_api_bearer_token:
        collectors["x"] = TwitterCollector(bearer_token=settings.x_api_bearer_token)
    return collectors


# --- Commands ---


def cmd_digest(args: list[str]):
    """Show digest, optionally filtered by category."""
    db = get_db()
    category = args[0] if args else None
    from backend.services.digest import build_digest
    result = build_digest(db, category=category)
    if not result["items"]:
        print("No summarized content yet. Run: /info-tracker collect")
        return
    for item in result["items"]:
        print(f"**{item['person_name']}** ({item['category_name']}, {item['source_platform']})")
        if item["so_what"]:
            print(f"  {item['so_what']}")
        if item["ai_summary"]:
            for line in item["ai_summary"].split("\n"):
                if line.strip():
                    print(f"  {line.strip()}")
        print(f"  {item['original_url']}")
        print()
    db.close()


def cmd_collect(args: list[str]):
    """Collect content from all tracked people."""
    db = get_db()
    from backend.services.collector_service import CollectorService
    service = CollectorService(collectors=get_collectors())
    new_content = asyncio.run(service.collect_all(db))
    print(f"Collected {len(new_content)} new items.")
    db.close()


def cmd_summarize(args: list[str]):
    """Summarize unsummarized content using Claude API."""
    if not settings.anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY not set in .env")
        return
    db = get_db()
    from backend.llm.claude_provider import ClaudeProvider
    from backend.services.summarizer import SummarizerService
    llm = ClaudeProvider(api_key=settings.anthropic_api_key)
    service = SummarizerService(llm=llm)
    count = asyncio.run(service.summarize_pending(db))
    print(f"Summarized {count} items.")
    db.close()


def cmd_trends(args: list[str]):
    """Show trending topics."""
    db = get_db()
    trends = db.query(Trend).order_by(Trend.momentum_score.desc()).limit(20).all()
    if not trends:
        print("No trends yet. Run: /info-tracker collect then /info-tracker summarize")
        return
    for t in trends:
        sentiment = f"+{t.sentiment_score:.1f}" if t.sentiment_score > 0 else f"{t.sentiment_score:.1f}"
        print(f"**{t.topic}** (momentum: {t.momentum_score * 100:.0f}%, sentiment: {sentiment})")
        print(f"  {t.description}")
        print()
    db.close()


def cmd_people(args: list[str]):
    """List all tracked people, optionally filtered by category."""
    db = get_db()
    query = db.query(Person).join(Category)
    if args:
        query = query.filter(Category.name == args[0])
    people = query.order_by(Category.sort_order, Person.name).all()
    current_cat = None
    for p in people:
        if p.category.name != current_cat:
            current_cat = p.category.name
            print(f"\n## {current_cat}")
        handles = ", ".join(f"{k}: {v}" for k, v in p.platform_handles.items())
        print(f"  [{p.id}] {p.name} — {handles}")
    print(f"\n{len(people)} people tracked.")
    db.close()


def cmd_add(args: list[str]):
    """Add a person. Usage: add <name> <category> [--x handle] [--youtube channel_id] [--substack feed_url] [--reddit username]"""
    if len(args) < 2:
        print("Usage: add <name> <category> [--x handle] [--youtube channel_id] [--substack feed_url] [--reddit username]")
        return
    name = args[0]
    category_name = args[1]
    handles = {}
    i = 2
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            platform = args[i][2:]
            handles[platform] = args[i + 1]
            i += 2
        else:
            i += 1

    db = get_db()
    cat = db.query(Category).filter_by(name=category_name).first()
    if not cat:
        # Create custom category
        max_order = db.query(Category).count()
        cat = Category(name=category_name, is_custom=True, sort_order=max_order + 1)
        db.add(cat)
        db.commit()
        print(f"Created new category: {category_name}")

    existing = db.query(Person).filter_by(name=name).first()
    if existing:
        print(f"'{name}' already exists (id={existing.id}). Use 'update' to modify.")
        db.close()
        return

    person = Person(name=name, category_id=cat.id, platform_handles=handles, is_custom=True)
    db.add(person)
    db.commit()
    print(f"Added {name} to {category_name} with handles: {handles}")
    db.close()


def cmd_remove(args: list[str]):
    """Remove a person by ID or name."""
    if not args:
        print("Usage: remove <id or name>")
        return
    db = get_db()
    target = args[0]
    if target.isdigit():
        person = db.query(Person).get(int(target))
    else:
        person = db.query(Person).filter_by(name=target).first()
    if not person:
        print(f"Person not found: {target}")
        db.close()
        return
    name = person.name
    db.delete(person)
    db.commit()
    print(f"Removed {name}")
    db.close()


def cmd_update(args: list[str]):
    """Update a person's handles. Usage: update <id or name> --x handle --youtube channel_id ..."""
    if len(args) < 3:
        print("Usage: update <id or name> --x handle --youtube channel_id --substack feed_url --reddit username")
        return
    db = get_db()
    target = args[0]
    if target.isdigit():
        person = db.query(Person).get(int(target))
    else:
        person = db.query(Person).filter_by(name=target).first()
    if not person:
        print(f"Person not found: {target}")
        db.close()
        return

    handles = dict(person.platform_handles)
    i = 1
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            platform = args[i][2:]
            value = args[i + 1]
            if value.lower() == "remove":
                handles.pop(platform, None)
                print(f"  Removed {platform}")
            else:
                handles[platform] = value
                print(f"  Set {platform} = {value}")
            i += 2
        else:
            i += 1

    person.platform_handles = handles
    db.commit()
    print(f"Updated {person.name}: {handles}")
    db.close()


def cmd_categories(args: list[str]):
    """List all categories."""
    db = get_db()
    cats = db.query(Category).order_by(Category.sort_order).all()
    for c in cats:
        count = db.query(Person).filter_by(category_id=c.id).count()
        custom = " (custom)" if c.is_custom else ""
        print(f"  {c.name}{custom} — {count} people")
    db.close()


def cmd_config(args: list[str]):
    """Show or update config. Usage: config [frequency <hours>]"""
    if not args:
        print(f"ANTHROPIC_API_KEY: {'set' if settings.anthropic_api_key else 'not set'}")
        print(f"YOUTUBE_API_KEY: {'set' if settings.youtube_api_key else 'not set'}")
        print(f"X_API_BEARER_TOKEN: {'set' if settings.x_api_bearer_token else 'not set'}")
        print(f"Digest frequency: every {settings.digest_frequency_hours} hours")
        print(f"Database: {settings.database_url}")
        return
    if args[0] == "frequency" and len(args) > 1:
        print(f"To change digest frequency, edit .env and set DIGEST_FREQUENCY_HOURS={args[1]}")
        return
    print(f"Unknown config command: {args[0]}")


def cmd_status(args: list[str]):
    """Show system status."""
    db = get_db()
    people_count = db.query(Person).count()
    content_count = db.query(Content).count()
    summarized = db.query(Content).filter(Content.ai_summary.isnot(None)).count()
    unsummarized = content_count - summarized
    trend_count = db.query(Trend).count()
    print(f"People tracked: {people_count}")
    print(f"Content collected: {content_count} ({summarized} summarized, {unsummarized} pending)")
    print(f"Trends detected: {trend_count}")
    print(f"Collectors available: {', '.join(get_collectors().keys())}")
    db.close()


COMMANDS = {
    "digest": cmd_digest,
    "today": cmd_digest,
    "collect": cmd_collect,
    "refresh": cmd_collect,
    "summarize": cmd_summarize,
    "trends": cmd_trends,
    "people": cmd_people,
    "list": cmd_people,
    "add": cmd_add,
    "remove": cmd_remove,
    "update": cmd_update,
    "categories": cmd_categories,
    "config": cmd_config,
    "status": cmd_status,
}


def main():
    args = sys.argv[1:]
    if not args:
        cmd_digest([])
        return

    command = args[0].lower()
    handler = COMMANDS.get(command)
    if handler:
        handler(args[1:])
    else:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(sorted(set(COMMANDS.keys())))}")


if __name__ == "__main__":
    main()
