"""Smoke test: migration, storage round-trip, and date utils (no UI)."""

import json
import os
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from timecapsule import storage
from timecapsule.models import Memory
from timecapsule.utils import (
    milestones,
    next_occurrence,
    on_this_day,
    time_since,
    upcoming_anniversaries,
)

tmp = tempfile.mkdtemp()
storage.SCRIPT_DIR = tmp
storage.MEMORIES_FILE = os.path.join(tmp, "memories.json")
storage.SETTINGS_FILE = os.path.join(tmp, "settings.json")
storage.PHOTOS_DIR = os.path.join(tmp, "photos")
storage.THUMBS_DIR = os.path.join(tmp, "photos", "thumbs")
storage.LEGACY_DATES_FILE = os.path.join(tmp, "important_dates.json")
storage.LEGACY_CATEGORIES_FILE = os.path.join(tmp, "categories.json")

# --- v1 migration
legacy = {
    "Anniversary": {"date": "06-15-2023", "notes": "first date", "category": "Us"},
    "Old format": "01-02-2020",
    "Bad date": {"date": "99-99-9999", "notes": "", "category": ""},
}
with open(storage.LEGACY_DATES_FILE, "w") as fh:
    json.dump(legacy, fh)
with open(storage.LEGACY_CATEGORIES_FILE, "w") as fh:
    json.dump({"Us": "#FF6B9D"}, fh)

memories, categories = storage.load_store()
assert len(memories) == 2, memories
titles = {m.title for m in memories}
assert titles == {"Anniversary", "Old format"}, titles
anniv = next(m for m in memories if m.title == "Anniversary")
assert anniv.day == date(2023, 6, 15) and anniv.category == "Us"
assert categories == {"Us": "#FF6B9D"}
assert os.path.exists(storage.LEGACY_DATES_FILE + ".bak")
assert not os.path.exists(storage.LEGACY_DATES_FILE)
print("migration OK")

# --- round trip
memories.append(Memory.new("Trip", date(2024, 12, 25), "snow", "Adventures", []))
storage.save_store(memories, categories)
loaded, cats = storage.load_store()
assert len(loaded) == 3 and loaded[-1].title == "Trip"
print("round-trip OK")

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
