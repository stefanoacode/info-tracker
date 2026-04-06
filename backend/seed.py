import json
from pathlib import Path

from sqlalchemy.orm import Session

from backend.models.category import Category
from backend.models.person import Person

PRESETS_DIR = Path(__file__).parent.parent / "data" / "presets"

CATEGORIES = [
    {"name": "Builders", "description": "Engineers, PMs, designers shipping AI products", "sort_order": 1},
    {"name": "Researchers", "description": "Scientists publishing papers, pushing SOTA", "sort_order": 2},
    {"name": "Founders", "description": "CEO/CTOs of AI-native startups", "sort_order": 3},
    {"name": "Investors", "description": "VCs and angels actively funding AI", "sort_order": 4},
    {"name": "Commentators", "description": "Journalists, analysts, policy thinkers covering AI", "sort_order": 5},
]


def seed_database(db: Session) -> None:
    """Seed categories and preset people. Idempotent — skips existing records."""
    for cat_data in CATEGORIES:
        existing = db.query(Category).filter_by(name=cat_data["name"]).first()
        if not existing:
            db.add(Category(**cat_data))
    db.commit()

    for cat in db.query(Category).filter_by(is_custom=False).all():
        filename = cat.name.lower() + ".json"
        preset_file = PRESETS_DIR / filename
        if not preset_file.exists():
            continue

        with open(preset_file) as f:
            people_data = json.load(f)

        for person_data in people_data:
            existing = db.query(Person).filter_by(name=person_data["name"]).first()
            if not existing:
                db.add(
                    Person(
                        name=person_data["name"],
                        bio=person_data.get("bio", ""),
                        category_id=cat.id,
                        platform_handles=person_data.get("platform_handles", {}),
                    )
                )
    db.commit()
