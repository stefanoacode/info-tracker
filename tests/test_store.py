"""Tests for JSON store."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from backend import store


@pytest.fixture(autouse=True)
def tmp_data_dir(tmp_path):
    """Redirect all store files to a temp directory."""
    with patch.object(store, "PEOPLE_FILE", tmp_path / "people.json"), \
         patch.object(store, "CONTENT_FILE", tmp_path / "content.json"), \
         patch.object(store, "CONFIG_FILE", tmp_path / "config.json"):
        yield tmp_path


def test_initial_seed_creates_people():
    people = store.get_people()
    assert len(people) > 0
    names = {p["name"] for p in people}
    assert "Andrej Karpathy" in names


def test_initial_seed_creates_categories():
    cats = store.get_categories()
    names = {c["name"] for c in cats}
    assert "Builders" in names
    assert "Investors" in names
    assert len(cats) == 5


def test_add_person():
    store.add_person("New Person", "Builders", {"x": "newperson"})
    person = store.find_person("New Person")
    assert person is not None
    assert person["platforms"]["x"] == "newperson"


def test_add_person_creates_category():
    store.add_person("VC Guy", "VCs", {"x": "vcguy"})
    cats = store.get_categories()
    names = {c["name"] for c in cats}
    assert "VCs" in names


def test_remove_person():
    name = store.remove_person("Andrej Karpathy")
    assert name == "Andrej Karpathy"
    assert store.find_person("Andrej Karpathy") is None


def test_update_person():
    person = store.update_person("Andrej Karpathy", {"substack": "https://karpathy.ai/feed"})
    assert person is not None
    assert person["platforms"]["substack"] == "https://karpathy.ai/feed"


def test_update_person_remove_platform():
    person = store.update_person("Andrej Karpathy", {"x": "remove"})
    assert "x" not in person["platforms"]


def test_add_and_remove_category():
    assert store.add_category("Podcasters", "AI podcast hosts")
    cats = store.get_categories()
    assert any(c["name"] == "Podcasters" for c in cats)

    result = store.remove_category("Podcasters")
    assert result == "Podcasters"


def test_cannot_remove_category_with_people():
    result = store.remove_category("Builders")
    assert result is None


def test_content_deduplication():
    items = [{"url": "https://example.com/1", "text": "Hello", "person": "Test", "category": "Builders", "platform": "substack", "date": ""}]
    count1 = store.add_content(items)
    assert count1 == 1
    count2 = store.add_content(items)
    assert count2 == 0


def test_get_content_filtered():
    store.add_content([
        {"url": "https://a.com/1", "text": "A", "person": "P1", "category": "Builders", "platform": "x", "date": "2026-04-05"},
        {"url": "https://b.com/1", "text": "B", "person": "P2", "category": "Investors", "platform": "x", "date": "2026-04-04"},
    ])
    builders = store.get_content(category="Builders")
    assert len(builders) == 1
    assert builders[0]["person"] == "P1"


def test_config():
    store.set_config_value("digest_frequency", "every 6 hours")
    assert store.get_config_value("digest_frequency") == "every 6 hours"
    assert store.get_config_value("nonexistent", "default") == "default"
