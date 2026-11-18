"""Persistence: SQLite database in AppData plus photo file storage."""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import sqlite3
import sys
import uuid
import zipfile
from datetime import date

from PIL import Image, ImageOps

from .models import Memory

SCHEMA_VERSION = 1


def _default_app_dir() -> str:
    """Per-user data directory: %APPDATA%\\TimeCapsule on Windows."""
    base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "TimeCapsule")


APP_DIR = _default_app_dir()
DB_NAME = "timecapsule.db"
PHOTOS_NAME = "photos"
DB_FILE = os.path.join(APP_DIR, DB_NAME)
PHOTOS_DIR = os.path.join(APP_DIR, PHOTOS_NAME)
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
            self._conn.execute("DELETE FROM photos WHERE memory_id = ?", (memory.id,))
            self._conn.executemany(
                "INSERT INTO photos (name, memory_id, position) VALUES (?, ?, ?)",
                [(name, memory.id, i) for i, name in enumerate(memory.photos)],
            )

    def replace_all(
        self,
        memories: list[Memory],
        categories: dict[str, str],
        settings: dict[str, str],
    ) -> None:
        """Swap the entire contents for the given data, in one transaction."""
        with self._conn:
            for table in ("memories", "categories", "settings"):
                self._conn.execute(f"DELETE FROM {table}")
            self._conn.executemany(
                "INSERT INTO memories (id, title, day, notes, category, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        m.id,
                        m.title,
                        m.day.isoformat(),
                        m.notes,
                        m.category,
                        m.created_at,
                    )
                    for m in memories
                ],
            )
            self._conn.executemany(
                "INSERT INTO photos (name, memory_id, position) VALUES (?, ?, ?)",
                [(n, m.id, i) for m in memories for i, n in enumerate(m.photos)],
            )
            self._conn.executemany(
                "INSERT INTO categories (name, color) VALUES (?, ?)",
                categories.items(),
            )
            self._conn.executemany(
                "INSERT INTO settings (key, value) VALUES (?, ?)", settings.items()
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
            # Phone photos store rotation in EXIF; bake it in, since the
            # JPEG thumbnail is saved without that metadata.
            img = ImageOps.exif_transpose(img)
            img.thumbnail(THUMB_SIZE)
            img.convert("RGB").save(thumb_path(name), "JPEG", quality=85)
    except (OSError, ValueError, Image.DecompressionBombError):
        delete_photo(name)
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


# ---------------------------------------------------------------- backup

BACKUP_JSON = "backup.json"
BACKUP_FORMAT = 1


class BackupError(Exception):
    """The chosen file is not a usable Time Capsule backup."""


def create_backup(dest: str) -> None:
    """Write a zip at `dest`: backup.json (all data, readable) plus photos/.

    Opens its own connection, so it is safe to call from a worker thread.
    """
    db = Database()
    try:
        data = {
            "format": BACKUP_FORMAT,
            "memories": [
                {**dataclasses.asdict(m), "day": m.day.isoformat()}
                for m in sorted(db.list_memories(), key=lambda m: m.day)
            ],
            "categories": db.categories(),
            "settings": db.get_settings(),
        }
    finally:
        db.close()
    # Stored, not deflated: photos are already compressed.
    with zipfile.ZipFile(dest, "w") as zf:
        zf.writestr(
            BACKUP_JSON,
            json.dumps(data, indent=2, ensure_ascii=False),
            compress_type=zipfile.ZIP_DEFLATED,
        )
        for root, _, files in os.walk(PHOTOS_DIR):
            for name in files:
                path = os.path.join(root, name)
                zf.write(path, os.path.relpath(path, APP_DIR).replace(os.sep, "/"))


def restore_backup(source: str) -> None:
    """Replace the database and all photos with the contents of a backup.

    The caller must close its Database first. Raises BackupError, leaving
    current data untouched, if `source` is not a valid backup.
    """
    staging = os.path.join(APP_DIR, "restore.tmp")  # same drive, so moves are renames
    shutil.rmtree(staging, ignore_errors=True)
    try:
        try:
            with zipfile.ZipFile(source) as zf:
                data = json.loads(zf.read(BACKUP_JSON))
                if data["format"] != BACKUP_FORMAT:
                    raise ValueError(f"unsupported backup format {data['format']!r}")
                memories = [
                    Memory(**{**m, "day": date.fromisoformat(m["day"])})
                    for m in data["memories"]
                ]
                # Only our own layout; extractall() itself strips ".." and drives.
                zf.extractall(
                    staging,
                    [n for n in zf.namelist() if n.startswith(PHOTOS_NAME + "/")],
                )
            # Build the new database in staging so bad data fails before the swap.
            staged = Database(os.path.join(staging, DB_NAME))
            try:
                staged.replace_all(memories, data["categories"], data["settings"])
            finally:
                staged.close()
        except (
            zipfile.BadZipFile,
            sqlite3.Error,
            OSError,
            KeyError,  # includes backup.json missing from the zip
            TypeError,
            ValueError,  # includes malformed JSON and bad dates
            AttributeError,
        ) as exc:
            raise BackupError(str(exc)) from exc

        # shortcut: not atomic, a crash between here and the last move leaves
        # partial data; move the old files aside first if that ever bites.
        for suffix in ("", "-wal", "-shm"):
            if os.path.exists(DB_FILE + suffix):
                os.remove(DB_FILE + suffix)
        shutil.rmtree(PHOTOS_DIR, ignore_errors=True)
        shutil.move(os.path.join(staging, DB_NAME), DB_FILE)
        staged_photos = os.path.join(staging, PHOTOS_NAME)
        if os.path.isdir(staged_photos):
            shutil.move(staged_photos, PHOTOS_DIR)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
