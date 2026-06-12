"""Persistence: SQLite database in AppData plus photo file storage."""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import uuid
from datetime import date

from PIL import Image

from .models import Memory

SCHEMA_VERSION = 1


def _default_app_dir() -> str:
    """Per-user data directory: %APPDATA%\\TimeCapsule on Windows."""
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "TimeCapsule")


APP_DIR = _default_app_dir()
DB_FILE = os.path.join(APP_DIR, "timecapsule.db")
PHOTOS_DIR = os.path.join(APP_DIR, "photos")
THUMBS_DIR = os.path.join(PHOTOS_DIR, "thumbs")

# Bundled resources (res/ at the repo root in dev, _MEIPASS when frozen)
if getattr(sys, "frozen", False):
    RES_DIR = os.path.join(
        getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)), "res"
    )
else:
    _SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    RES_DIR = os.path.join(os.path.dirname(_SRC_DIR), "res")


def res_path(name: str) -> str:
    return os.path.join(RES_DIR, name)


THUMB_SIZE = (320, 320)

DEFAULT_CATEGORIES = {
    "Us": "#E91E63",
    "Adventures": "#26A69A",
    "Milestones": "#FFB300",
}


_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    day         TEXT NOT NULL,
    notes       TEXT NOT NULL DEFAULT '',
    category    TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS photos (
    name       TEXT PRIMARY KEY,
    memory_id  TEXT NOT NULL REFERENCES memories(id) ON DELETE CASCADE,
    position   INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_photos_memory ON photos(memory_id);

CREATE TABLE IF NOT EXISTS categories (
    name   TEXT PRIMARY KEY,
    color  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);
"""


class Database:
    """All reads and writes go through one WAL-mode SQLite connection."""

    def __init__(self, path: str | None = None) -> None:
        self.path = path or DB_FILE
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self) -> None:
        with self._conn:
            self._conn.executescript(_SCHEMA)
            version = self._conn.execute("PRAGMA user_version").fetchone()[0]
            if version == 0:
                has_categories = self._conn.execute(
                    "SELECT COUNT(*) FROM categories"
                ).fetchone()[0]
                if not has_categories:
                    self._conn.executemany(
                        "INSERT INTO categories (name, color) VALUES (?, ?)",
                        DEFAULT_CATEGORIES.items(),
                    )
                self._conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------ memories

    def list_memories(self) -> list[Memory]:
        rows = self._conn.execute(
            "SELECT id, title, day, notes, category, created_at FROM memories"
        ).fetchall()
        photo_rows = self._conn.execute(
            "SELECT name, memory_id FROM photos ORDER BY memory_id, position"
        ).fetchall()
        photos: dict[str, list[str]] = {}
        for p in photo_rows:
            photos.setdefault(p["memory_id"], []).append(p["name"])
        return [
            Memory(
                id=r["id"],
                title=r["title"],
                day=date.fromisoformat(r["day"]),
                notes=r["notes"],
                category=r["category"],
                photos=photos.get(r["id"], []),
                created_at=r["created_at"],
            )
            for r in rows
        ]

    def upsert_memory(self, memory: Memory) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO memories (id, title, day, notes, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    day = excluded.day,
                    notes = excluded.notes,
                    category = excluded.category
                """,
                (
                    memory.id,
                    memory.title,
                    memory.day.isoformat(),
                    memory.notes,
                    memory.category,
                    memory.created_at,
                ),
            )
            self._conn.execute(
                "DELETE FROM photos WHERE memory_id = ?", (memory.id,)
            )
            self._conn.executemany(
                "INSERT INTO photos (name, memory_id, position) VALUES (?, ?, ?)",
                [(name, memory.id, i) for i, name in enumerate(memory.photos)],
            )

    def delete_memory(self, memory_id: str) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))

    # ---------------------------------------------------------- categories

    def categories(self) -> dict[str, str]:
        rows = self._conn.execute("SELECT name, color FROM categories ORDER BY name")
        return {r["name"]: r["color"] for r in rows}

    def set_category(self, name: str, color: str) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO categories (name, color) VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE SET color = excluded.color
                """,
                (name, color),
            )

    def delete_category(self, name: str) -> None:
        with self._conn:
            self._conn.execute("DELETE FROM categories WHERE name = ?", (name,))
            self._conn.execute(
                "UPDATE memories SET category = '' WHERE category = ?", (name,)
            )

    # ------------------------------------------------------------ settings

    def get_settings(self) -> dict[str, str]:
        rows = self._conn.execute("SELECT key, value FROM settings")
        return {r["key"]: r["value"] for r in rows}

    def set_setting(self, key: str, value: str) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (key, value),
            )


# ---------------------------------------------------------------- photos


def import_photo(source_path: str) -> str | None:
    """Copy a photo into photos/ and create a thumbnail.

    Returns the stored file name, or None if the image is unreadable.
    """
    os.makedirs(THUMBS_DIR, exist_ok=True)
    ext = os.path.splitext(source_path)[1].lower() or ".jpg"
    name = uuid.uuid4().hex + ext
    dest = os.path.join(PHOTOS_DIR, name)
    try:
        shutil.copyfile(source_path, dest)
        with Image.open(dest) as img:
            img.thumbnail(THUMB_SIZE)
            img.convert("RGB").save(thumb_path(name), "JPEG", quality=85)
    except (OSError, ValueError):
        if os.path.exists(dest):
            os.remove(dest)
        return None
    return name


def photo_path(name: str) -> str:
    return os.path.join(PHOTOS_DIR, name)


def thumb_path(name: str) -> str:
    return os.path.join(THUMBS_DIR, os.path.splitext(name)[0] + ".jpg")


def delete_photo(name: str) -> None:
    for path in (photo_path(name), thumb_path(name)):
        try:
            os.remove(path)
        except OSError:
            pass
