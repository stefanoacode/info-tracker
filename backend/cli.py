"""CLI for info-tracker. Called by the Claude Code skill."""
from __future__ import annotations

import asyncio
import sys

from backend.config import settings
from backend.store import (
    get_people, find_person, add_person, remove_person, update_person,
    get_categories, add_category, remove_category,
    get_content, load_config, get_config_value, set_config_value,
)


def get_collectors() -> dict:
    from backend.collectors.rss import RSSCollector
    from backend.collectors.reddit import RedditCollector
    from backend.collectors.twitter import TwitterCollector

    return {
        "substack": RSSCollector(),
        "reddit": RedditCollector(),
        "x": TwitterCollector(nitter_instance=settings.nitter_instance),
    }


# --- Commands ---


def cmd_digest(args: list[str]):
    """Show recent content for Claude to summarize inline."""
    category = args[0] if args else None
    items = get_content(category=category)
    if not items:
        print("No content yet. Run: /info-tracker collect")
        return
    for c in items:
        print(f"--- [{c['person']}] ({c['category']}, {c['platform']}) ---")
        print(f"URL: {c['url']}")
        if c.get("date"):
            print(f"Date: {c['date'][:10]}")
        text = c["text"]
        if len(text) > 1000:
            text = text[:1000] + "... [truncated]"
        print(text)
        print()
    print(f"({len(items)} items)")


def cmd_collect(args: list[str]):
    """Collect content from all tracked people."""
    from backend.services.collector_service import CollectorService
    service = CollectorService(collectors=get_collectors())
    new_count = asyncio.run(service.collect_all())
    print(f"Collected {new_count} new items.")


def cmd_people(args: list[str]):
    """List all tracked people."""
    category = args[0] if args else None
    people = get_people(category=category)
    if not people:
        print("No people tracked.")
        return
    current_cat = None
    for p in people:
        if p["category"] != current_cat:
            current_cat = p["category"]
            print(f"\n## {current_cat}")
        handles = ", ".join(f"{k}: {v}" for k, v in p["platforms"].items())
        print(f"  [{p['id']}] {p['name']} — {handles}")
    print(f"\n{len(people)} people tracked.")


def cmd_add(args: list[str]):
    """Add a person. Usage: add <name> <category> [--x handle] [--substack feed_url] [--reddit username]"""
    if len(args) < 2:
        print("Usage: add <name> <category> [--x handle] [--substack feed_url] [--reddit username]")
        return
    name, category_name = args[0], args[1]
    platforms = {}
    i = 2
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            platforms[args[i][2:]] = args[i + 1]
            i += 2
        else:
            i += 1

    existing = find_person(name)
    if existing:
        print(f"'{name}' already exists (id={existing['id']}). Use 'update' to modify.")
        return

    person = add_person(name, category_name, platforms)
    print(f"Added {name} to {category_name} with platforms: {platforms}")


def cmd_remove(args: list[str]):
    """Remove a person by ID or name."""
    if not args:
        print("Usage: remove <id or name>")
        return
    name = remove_person(args[0])
    if name:
        print(f"Removed {name}")
    else:
        print(f"Person not found: {args[0]}")


def cmd_update(args: list[str]):
    """Update a person's platforms. Usage: update <name or id> --x handle --substack url ..."""
    if len(args) < 3:
        print("Usage: update <name or id> --x handle --substack feed_url --reddit username")
        return
    target = args[0]
    updates = {}
    i = 1
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            updates[args[i][2:]] = args[i + 1]
            i += 2
        else:
            i += 1

    person = update_person(target, updates)
    if person:
        print(f"Updated {person['name']}: {person['platforms']}")
    else:
        print(f"Person not found: {target}")


def cmd_categories(args: list[str]):
    """List, add, or remove categories."""
    if not args:
        for c in get_categories():
            desc = f" — {c['description']}" if c.get("description") else ""
            print(f"  {c['name']}{desc} ({c['count']} people)")
        return

    action = args[0].lower()
    if action == "add" and len(args) >= 2:
        name = args[1]
        description = " ".join(args[2:]) if len(args) > 2 else ""
        if add_category(name, description):
            print(f"Created category: {name}")
        else:
            print(f"Category '{name}' already exists.")
    elif action == "remove" and len(args) >= 2:
        result = remove_category(args[1])
        if result:
            print(f"Removed category: {result}")
        elif result is None:
            print(f"Cannot remove '{args[1]}' — it has people. Remove them first.")
        else:
            print(f"Category '{args[1]}' not found.")
    else:
        print("Usage: categories [add <name> [description] | remove <name>]")


def cmd_config(args: list[str]):
    """Show or update config."""
    if not args:
        nitter = settings.nitter_instance or "auto (public instances)"
        freq = get_config_value("digest_frequency", "not set")
        print(f"Nitter instance: {nitter}")
        print(f"Digest frequency: {freq}")
        config = load_config()
        for k, v in config.items():
            if k != "digest_frequency":
                print(f"{k}: {v}")
        return

    if args[0] == "set" and len(args) >= 3:
        key, value = args[1], " ".join(args[2:])
        set_config_value(key, value)
        print(f"Set {key} = {value}")
        return

    if args[0] == "frequency" and len(args) >= 2:
        set_config_value("digest_frequency", " ".join(args[1:]))
        print(f"Digest frequency set to: {' '.join(args[1:])}")
        return

    value = get_config_value(args[0])
    if value:
        print(f"{args[0]} = {value}")
    else:
        print(f"No config value for '{args[0]}'")


def cmd_status(args: list[str]):
    """Show system status."""
    people = get_people()
    content = get_content(limit=99999)
    print(f"People tracked: {len(people)}")
    print(f"Content collected: {len(content)}")
    print(f"Collectors available: {', '.join(get_collectors().keys())}")


COMMANDS = {
    "digest": cmd_digest,
    "today": cmd_digest,
    "collect": cmd_collect,
    "refresh": cmd_collect,
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
