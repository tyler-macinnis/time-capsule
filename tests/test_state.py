"""Tests for AppState: cache, mutations, filtering, and search."""

from __future__ import annotations

import os
from datetime import date

from timecapsule import storage
from timecapsule.state import AppState
from timecapsule.storage import DEFAULT_CATEGORIES


def test_state_loads_from_db(db, make_memory):
    m = make_memory(title="Preloaded")
    db.upsert_memory(m)
    db.set_setting("accent", "#FFB300")
    state = AppState(db)
    assert [x.title for x in state.memories] == ["Preloaded"]
    assert state.categories == DEFAULT_CATEGORIES
    assert state.settings == {"accent": "#FFB300"}
    assert state.search == ""


def test_add_persists(state, make_memory):
    state.add(make_memory(title="Added"))
    assert [m.title for m in state.db.list_memories()] == ["Added"]
    assert len(state.memories) == 1


def test_update_persists(state, make_memory):
    m = make_memory(title="Before")
    state.add(m)
    m.title = "After"
    state.update(m)
    assert state.db.list_memories()[0].title == "After"


def test_remove_deletes_row_and_photo_files(state, make_memory, sample_png):
    name = storage.import_photo(sample_png)
    m = make_memory(photos=[name])
    state.add(m)
    state.remove(m)
    assert state.memories == []
    assert state.db.list_memories() == []
    assert not os.path.exists(storage.photo_path(name))
    assert not os.path.exists(storage.thumb_path(name))


def test_get_by_id(state, make_memory):
    m = make_memory()
    state.add(m)
    assert state.get(m.id) is m
    assert state.get("nope") is None


def test_filtered_memories_sorted_newest_first(state, make_memory):
    state.add(make_memory(title="Oldest", day=date(2020, 1, 1)))
    state.add(make_memory(title="Newest", day=date(2025, 12, 31)))
    state.add(make_memory(title="Middle", day=date(2023, 6, 15)))
    titles = [m.title for m in state.filtered_memories()]
    assert titles == ["Newest", "Middle", "Oldest"]


def test_search_matches_title_notes_category_case_insensitive(state, make_memory):
    state.add(make_memory(title="Beach Day", day=date(2024, 7, 1)))
    state.add(
        make_memory(title="Dinner", notes="amazing BEACH sunset", day=date(2024, 7, 2))
    )
    state.add(make_memory(title="Hike", category="Adventures", day=date(2024, 7, 3)))
    state.add(make_memory(title="Movie night", day=date(2024, 7, 4)))

    state.search = "beach"
    assert {m.title for m in state.filtered_memories()} == {"Beach Day", "Dinner"}

    state.search = "ADVENT"
    assert {m.title for m in state.filtered_memories()} == {"Hike"}

    state.search = "   "  # whitespace-only -> no filter
    assert len(state.filtered_memories()) == 4

    state.search = "zzz-no-match"
    assert state.filtered_memories() == []


def test_all_photos_newest_memory_first(state, make_memory):
    state.add(make_memory(title="Old", day=date(2020, 1, 1), photos=["old1.jpg"]))
    state.add(
        make_memory(title="New", day=date(2024, 1, 1), photos=["new1.jpg", "new2.jpg"])
    )
    names = [name for name, _ in state.all_photos()]
    assert names == ["new1.jpg", "new2.jpg", "old1.jpg"]


def test_set_and_remove_category_updates_memories(state, make_memory):
    state.set_category("Trips", "#112233")
    assert state.categories["Trips"] == "#112233"
    assert state.db.categories()["Trips"] == "#112233"

    m = make_memory(category="Trips")
    state.add(m)
    state.remove_category("Trips")
    assert "Trips" not in state.categories
    assert m.category == ""
    assert state.db.list_memories()[0].category == ""


def test_set_setting_persists(state):
    state.set_setting("theme_mode", "light")
    assert state.settings["theme_mode"] == "light"
    assert state.db.get_settings()["theme_mode"] == "light"
