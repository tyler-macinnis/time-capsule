"""Tests for SQLite persistence and photo file storage."""

from __future__ import annotations

import os
from datetime import date

from PIL import Image

from timecapsule import storage
from timecapsule.storage import DEFAULT_CATEGORIES, Database

# ------------------------------------------------------------------ schema


def test_fresh_db_seeds_default_categories(db):
    assert db.categories() == DEFAULT_CATEGORIES


def test_fresh_db_has_no_memories_or_settings(db):
    assert db.list_memories() == []
    assert db.get_settings() == {}


def test_reopen_does_not_reseed_deleted_categories(db, temp_storage):
    for name in DEFAULT_CATEGORIES:
        db.delete_category(name)
    db.close()
    db2 = Database()
    try:
        assert db2.categories() == {}
    finally:
        db2.close()


# ---------------------------------------------------------------- memories


def test_memory_round_trip(db, make_memory):
    m = make_memory(
        title="First date",
        day=date(2022, 2, 14),
        notes="Coffee downtown",
        category="Us",
        photos=["p1.jpg", "p2.jpg"],
    )
    db.upsert_memory(m)
    loaded = db.list_memories()
    assert len(loaded) == 1
    got = loaded[0]
    assert got.id == m.id
    assert got.title == "First date"
    assert got.day == date(2022, 2, 14)
    assert got.notes == "Coffee downtown"
    assert got.category == "Us"
    assert got.photos == ["p1.jpg", "p2.jpg"]
    assert got.created_at == m.created_at


def test_upsert_updates_existing_memory(db, make_memory):
    m = make_memory(title="Old", notes="old notes")
    db.upsert_memory(m)
    m.title = "New"
    m.notes = "new notes"
    m.photos = ["x.jpg"]
    db.upsert_memory(m)
    loaded = db.list_memories()
    assert len(loaded) == 1
    assert loaded[0].title == "New"
    assert loaded[0].notes == "new notes"
    assert loaded[0].photos == ["x.jpg"]


def test_photo_positions_preserve_order(db, make_memory):
    names = [f"photo-{i}.jpg" for i in range(6)]
    m = make_memory(photos=names)
    db.upsert_memory(m)
    assert db.list_memories()[0].photos == names


def test_delete_memory_cascades_photos(db, make_memory):
    m = make_memory(photos=["a.jpg", "b.jpg"])
    db.upsert_memory(m)
    db.delete_memory(m.id)
    assert db.list_memories() == []
    count = db._conn.execute("SELECT COUNT(*) FROM photos").fetchone()[0]
    assert count == 0


def test_delete_unknown_memory_is_noop(db, make_memory):
    m = make_memory()
    db.upsert_memory(m)
    db.delete_memory("does-not-exist")
    assert len(db.list_memories()) == 1


# -------------------------------------------------------------- categories


def test_set_category_inserts_and_overwrites(db):
    db.set_category("Trips", "#123456")
    assert db.categories()["Trips"] == "#123456"
    db.set_category("Trips", "#654321")
    assert db.categories()["Trips"] == "#654321"


def test_delete_category_clears_memory_references(db, make_memory):
    db.set_category("Trips", "#123456")
    m = make_memory(category="Trips")
    db.upsert_memory(m)
    db.delete_category("Trips")
    assert "Trips" not in db.categories()
    assert db.list_memories()[0].category == ""


# ---------------------------------------------------------------- settings


def test_settings_round_trip_and_overwrite(db):
    db.set_setting("accent", "#FFB300")
    db.set_setting("theme_mode", "light")
    db.set_setting("accent", "#E91E63")
    assert db.get_settings() == {"accent": "#E91E63", "theme_mode": "light"}


# ------------------------------------------------------------- persistence


def test_data_survives_reconnect(db, make_memory):
    m = make_memory(title="Durable", photos=["p.jpg"])
    db.upsert_memory(m)
    db.set_setting("accent", "#0288D1")
    db.close()
    db2 = Database()
    try:
        loaded = db2.list_memories()
        assert len(loaded) == 1
        assert loaded[0].title == "Durable"
        assert loaded[0].photos == ["p.jpg"]
        assert db2.get_settings()["accent"] == "#0288D1"
    finally:
        db2.close()


# -------------------------------------------------------------- photo files


def test_import_photo_creates_full_and_thumbnail(sample_png):
    name = storage.import_photo(sample_png)
    assert name is not None
    assert os.path.exists(storage.photo_path(name))
    thumb = storage.thumb_path(name)
    assert os.path.exists(thumb)
    with Image.open(thumb) as img:
        assert max(img.size) <= 320


def test_import_photo_unreadable_file_returns_none(tmp_path):
    bad = tmp_path / "not-an-image.png"
    bad.write_bytes(b"this is not an image")
    name = storage.import_photo(str(bad))
    assert name is None
    # No orphaned full-size copy left behind
    leftovers = [
        f
        for f in os.listdir(storage.PHOTOS_DIR)
        if os.path.isfile(os.path.join(storage.PHOTOS_DIR, f))
    ]
    assert leftovers == []


def test_delete_photo_removes_both_files(sample_png):
    name = storage.import_photo(sample_png)
    storage.delete_photo(name)
    assert not os.path.exists(storage.photo_path(name))
    assert not os.path.exists(storage.thumb_path(name))


def test_delete_photo_missing_files_is_noop():
    storage.delete_photo("nonexistent.jpg")  # must not raise


def test_thumb_path_always_jpg():
    assert storage.thumb_path("abc.png").endswith("abc.jpg")
    assert storage.thumb_path("abc.jpeg").endswith("abc.jpg")
