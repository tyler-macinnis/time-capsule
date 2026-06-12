"""Smoke test: SQLite storage, photos, update checks, and date utils (no UI)."""

import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from timecapsule import storage, updates
from timecapsule.models import Memory
from timecapsule.storage import Database
from timecapsule.utils import (
    milestones,
    next_occurrence,
    on_this_day,
    time_since,
    upcoming_anniversaries,
)

tmp = tempfile.mkdtemp()
storage.APP_DIR = tmp
storage.DB_FILE = os.path.join(tmp, "timecapsule.db")
storage.PHOTOS_DIR = os.path.join(tmp, "photos")
storage.THUMBS_DIR = os.path.join(tmp, "photos", "thumbs")

# --- fresh database seeds default categories
db = Database(storage.DB_FILE)
assert db.categories() == storage.DEFAULT_CATEGORIES
print("schema OK")

# --- memory round trip (notes survive, no photos required)
anniv = Memory.new("Anniversary", date(2023, 6, 15), "first date", "Us")
db.upsert_memory(anniv)
db.upsert_memory(Memory.new("Trip", date(2024, 12, 25), "snow", "Adventures"))
loaded = db.list_memories()
assert len(loaded) == 2
got = next(m for m in loaded if m.id == anniv.id)
assert got.title == "Anniversary" and got.day == date(2023, 6, 15)
assert got.notes == "first date" and got.category == "Us" and got.photos == []

# --- update keeps identity, changes fields
anniv.notes = "updated note"
anniv.photos = ["a.jpg", "b.jpg"]
db.upsert_memory(anniv)
got = next(m for m in db.list_memories() if m.id == anniv.id)
assert got.notes == "updated note" and got.photos == ["a.jpg", "b.jpg"]
assert len(db.list_memories()) == 2
print("round-trip OK")

# --- delete cascades photo rows
db.delete_memory(anniv.id)
assert len(db.list_memories()) == 1
remaining = db._conn.execute("SELECT COUNT(*) FROM photos").fetchone()[0]
assert remaining == 0, remaining
print("delete OK")

# --- categories and settings
db.set_category("Custom", "#123456")
assert db.categories()["Custom"] == "#123456"
db.set_category("Custom", "#654321")
assert db.categories()["Custom"] == "#654321"
trip = db.list_memories()[0]
db.delete_category("Adventures")
assert "Adventures" not in db.categories()
assert next(m for m in db.list_memories() if m.id == trip.id).category == ""
db.set_setting("accent", "#E91E63")
db.set_setting("accent", "#0288D1")
assert db.get_settings() == {"accent": "#0288D1"}
print("categories/settings OK")

# --- data persists across connections
db.close()
db2 = Database(storage.DB_FILE)
assert len(db2.list_memories()) == 1
assert db2.get_settings()["accent"] == "#0288D1"
db2.close()
print("persistence OK")

# --- photo import
from PIL import Image

src_img = os.path.join(tmp, "test.png")
Image.new("RGB", (800, 600), "#E91E63").save(src_img)
name = storage.import_photo(src_img)
assert name and os.path.exists(storage.photo_path(name))
assert os.path.exists(storage.thumb_path(name))
with Image.open(storage.thumb_path(name)) as t:
    assert max(t.size) <= 320, t.size
storage.delete_photo(name)
assert not os.path.exists(storage.photo_path(name))
print("photos OK")

# --- update version comparison (offline)
assert updates.parse_version("v3.0.0") == (3, 0, 0)
assert updates.parse_version("3.10.2") == (3, 10, 2)
assert updates.parse_version("not-a-version") is None
assert updates.is_newer("v3.0.1", "3.0.0")
assert updates.is_newer("v3.1.0", "3.0.9")
assert not updates.is_newer("v3.0.0", "3.0.0")
assert not updates.is_newer("v2.9.9", "3.0.0")
assert not updates.is_newer("garbage", "3.0.0")
print("updates OK")

# --- utils
today = date(2026, 6, 11)
assert time_since(date(2023, 6, 11), today) == "3 years ago"
assert time_since(today, today) == "Today"
assert "from now" in time_since(date(2026, 7, 1), today)

ms = [Memory.new("Match", date(2020, 6, 11)), Memory.new("Nope", date(2020, 6, 12))]
otd = on_this_day(ms, today)
assert [m.title for m in otd] == ["Match"]

assert next_occurrence(date(2020, 6, 11), today) == date(2026, 6, 11)
assert next_occurrence(date(2020, 6, 10), today) == date(2027, 6, 10)
assert next_occurrence(date(2020, 2, 29), date(2026, 2, 1)) == date(2026, 3, 1)

up = upcoming_anniversaries(ms, today)
assert up[0][0].title == "Match" and up[0][2] == 0

reached, nxt = milestones(date(2023, 6, 11), today)
assert "1,000 days together" in reached and nxt and "2,000 days" in nxt
print("utils OK")

print("ALL SMOKE TESTS PASSED")
