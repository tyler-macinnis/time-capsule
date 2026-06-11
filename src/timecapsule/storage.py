"""Persistence: JSON storage, settings, photo import, and v1 migration."""

from __future__ import annotations

import json
import os
import shutil
import sys
import uuid
from datetime import datetime

from PIL import Image

from .models import Memory

if getattr(sys, "frozen", False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
else:
    # src/ directory, same place v1 kept its data
    SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEMORIES_FILE = os.path.join(SCRIPT_DIR, "memories.json")
SETTINGS_FILE = os.path.join(SCRIPT_DIR, "settings.json")
PHOTOS_DIR = os.path.join(SCRIPT_DIR, "photos")
THUMBS_DIR = os.path.join(PHOTOS_DIR, "thumbs")

# Bundled resources (res/ at the repo root in dev, _MEIPASS when frozen)
if getattr(sys, "frozen", False):
    RES_DIR = os.path.join(getattr(sys, "_MEIPASS", SCRIPT_DIR), "res")
else:
    RES_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "res")


def res_path(name: str) -> str:
    return os.path.join(RES_DIR, name)


# Legacy v1 files
LEGACY_DATES_FILE = os.path.join(SCRIPT_DIR, "important_dates.json")
LEGACY_CATEGORIES_FILE = os.path.join(SCRIPT_DIR, "categories.json")
LEGACY_DATE_FORMAT = "%m-%d-%Y"

THUMB_SIZE = (320, 320)

DEFAULT_CATEGORIES = {
    "Us": "#E91E63",
    "Adventures": "#26A69A",
    "Milestones": "#FFB300",
}


# ---------------------------------------------------------------- settings


def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
        json.dump(settings, fh, indent=4)


# ---------------------------------------------------------------- memories


def load_store() -> tuple[list[Memory], dict[str, str]]:
    """Load memories and categories, migrating v1 data if needed."""
    if not os.path.exists(MEMORIES_FILE) and os.path.exists(LEGACY_DATES_FILE):
        _migrate_v1()
    try:
        with open(MEMORIES_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"memories": [], "categories": dict(DEFAULT_CATEGORIES)}
    memories = [Memory.from_dict(m) for m in data.get("memories", [])]
    categories = data.get("categories", {}) or dict(DEFAULT_CATEGORIES)
    return memories, categories


def save_store(memories: list[Memory], categories: dict[str, str]) -> None:
    data = {
        "schema": 2,
        "memories": [m.to_dict() for m in memories],
        "categories": categories,
    }
    tmp = MEMORIES_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=4)
    os.replace(tmp, MEMORIES_FILE)


# ---------------------------------------------------------------- migration


def _migrate_v1() -> None:
    """Convert v1 important_dates.json/categories.json into memories.json."""
    try:
        with open(LEGACY_DATES_FILE, "r", encoding="utf-8") as fh:
            old_dates = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return

    categories: dict[str, str] = {}
    try:
        with open(LEGACY_CATEGORIES_FILE, "r", encoding="utf-8") as fh:
            categories = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    memories: list[Memory] = []
    for name, value in old_dates.items():
        if isinstance(value, str):  # very old single-string format
            value = {"date": value, "notes": "", "category": ""}
        try:
            day = datetime.strptime(value["date"], LEGACY_DATE_FORMAT).date()
        except (KeyError, ValueError):
            continue
        memories.append(
            Memory.new(
                title=name,
                day=day,
                notes=value.get("notes", ""),
                category=value.get("category", ""),
            )
        )

    if not categories:
        categories = dict(DEFAULT_CATEGORIES)
    save_store(memories, categories)

    # Back up originals so v1 files don't shadow-edit silently
    shutil.move(LEGACY_DATES_FILE, LEGACY_DATES_FILE + ".bak")
    if os.path.exists(LEGACY_CATEGORIES_FILE):
        shutil.move(LEGACY_CATEGORIES_FILE, LEGACY_CATEGORIES_FILE + ".bak")


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
