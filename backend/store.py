"""JSON file-based storage for info-tracker."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR

PEOPLE_FILE = DATA_DIR / "people.json"
CONTENT_FILE = DATA_DIR / "content.json"
CONFIG_FILE = DATA_DIR / "config.json"
PRESETS_DIR = Path(__file__).parent.parent / "data" / "presets"

PRESET_CATEGORIES = [
    {"name": "Builders", "description": "Engineers, PMs, designers shipping AI products"},
    {"name": "Researchers", "description": "Scientists publishing papers, pushing SOTA"},
    {"name": "Founders", "description": "CEO/CTOs of AI-native startups"},
    {"name": "Investors", "description": "VCs and angels actively funding AI"},
    {"name": "Commentators", "description": "Journalists, analysts, policy thinkers covering AI"},
]


def _read_json(path: Path, default: Any = None) -> Any:
    if path.exists():
        return json.loads(path.read_text())
    return default if default is not None else {}


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str))


# --- People & Categories ---


def _ensure_people() -> dict:
    """Load people.json, seeding from presets if it doesn't exist."""
    if PEOPLE_FILE.exists():
        return _read_json(PEOPLE_FILE)

    data = {"categories": PRESET_CATEGORIES, "people": [], "next_id": 1}

    for cat in PRESET_CATEGORIES:
        preset_file = PRESETS_DIR / f"{cat['name'].lower()}.json"
        if preset_file.exists():
            for p in json.loads(preset_file.read_text()):
                data["people"].append({
                    "id": data["next_id"],
                    "name": p["name"],
                    "bio": p.get("bio", ""),
                    "category": cat["name"],
                    "platforms": p.get("platform_handles", {}),
                })
                data["next_id"] += 1

    _write_json(PEOPLE_FILE, data)
    return data


def load_people() -> dict:
    return _ensure_people()


def save_people(data: dict) -> None:
    _write_json(PEOPLE_FILE, data)


def get_people(category: str | None = None) -> list[dict]:
    data = load_people()
    people = data["people"]
    if category:
        people = [p for p in people if p["category"] == category]
    return people


def find_person(target: str) -> dict | None:
    data = load_people()
    for p in data["people"]:
        if str(p["id"]) == target or p["name"] == target:
            return p
    return None


def add_person(name: str, category: str, platforms: dict, bio: str = "") -> dict:
    data = load_people()

    # Auto-create category if needed
    cat_names = [c["name"] for c in data["categories"]]
    if category not in cat_names:
        data["categories"].append({"name": category, "description": ""})

    person = {
        "id": data["next_id"],
        "name": name,
        "bio": bio,
        "category": category,
        "platforms": platforms,
    }
    data["people"].append(person)
    data["next_id"] += 1
    save_people(data)
    return person


def remove_person(target: str) -> str | None:
    data = load_people()
    for i, p in enumerate(data["people"]):
        if str(p["id"]) == target or p["name"] == target:
            removed = data["people"].pop(i)
            save_people(data)
            return removed["name"]
    return None


def update_person(target: str, platform_updates: dict) -> dict | None:
    data = load_people()
    for p in data["people"]:
        if str(p["id"]) == target or p["name"] == target:
            for platform, value in platform_updates.items():
                if value.lower() == "remove":
                    p["platforms"].pop(platform, None)
                else:
                    p["platforms"][platform] = value
            save_people(data)
            return p
    return None


def get_categories() -> list[dict]:
    data = load_people()
    cats = []
    for c in data["categories"]:
        count = sum(1 for p in data["people"] if p["category"] == c["name"])
        cats.append({**c, "count": count})
    return cats


def add_category(name: str, description: str = "") -> bool:
    data = load_people()
    if any(c["name"] == name for c in data["categories"]):
        return False
    data["categories"].append({"name": name, "description": description})
    save_people(data)
    return True


def remove_category(name: str) -> str | None:
    data = load_people()
    has_people = any(p["category"] == name for p in data["people"])
    if has_people:
        return None
    for i, c in enumerate(data["categories"]):
        if c["name"] == name:
            data["categories"].pop(i)
            save_people(data)
            return name
    return None


# --- Content ---


def load_content() -> list[dict]:
    return _read_json(CONTENT_FILE, [])


def save_content(items: list[dict]) -> None:
    _write_json(CONTENT_FILE, items)


def add_content(items: list[dict]) -> int:
    """Add new content items, deduplicating by URL. Returns count of new items."""
    existing = load_content()
    existing_urls = {c["url"] for c in existing}
    new_count = 0
    for item in items:
        if item["url"] not in existing_urls:
            existing.append(item)
            existing_urls.add(item["url"])
            new_count += 1
    if new_count:
        save_content(existing)
    return new_count


def get_content(category: str | None = None, limit: int = 30) -> list[dict]:
    items = load_content()
    if category:
        items = [c for c in items if c.get("category") == category]
    # Sort by date descending
    items.sort(key=lambda x: x.get("date", ""), reverse=True)
    return items[:limit]


# --- Config ---


def load_config() -> dict:
    return _read_json(CONFIG_FILE, {})


def save_config(data: dict) -> None:
    _write_json(CONFIG_FILE, data)


def get_config_value(key: str, default: str = "") -> str:
    return load_config().get(key, default)


def set_config_value(key: str, value: str) -> None:
    config = load_config()
    config[key] = value
    save_config(config)
