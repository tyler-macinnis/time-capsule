"""Shared fixtures: isolated temp storage for every test."""

from __future__ import annotations

import os
from datetime import date

import pytest
from PIL import Image

from timecapsule import storage
from timecapsule.models import Memory
from timecapsule.state import AppState
from timecapsule.storage import Database


@pytest.fixture(autouse=True)
def temp_storage(tmp_path, monkeypatch):
    """Point all storage paths at a per-test temp directory."""
    app_dir = tmp_path / "TimeCapsule"
    photos = app_dir / "photos"
    thumbs = photos / "thumbs"
    monkeypatch.setattr(storage, "APP_DIR", str(app_dir))
    monkeypatch.setattr(storage, "DB_FILE", str(app_dir / "timecapsule.db"))
    monkeypatch.setattr(storage, "PHOTOS_DIR", str(photos))
    monkeypatch.setattr(storage, "THUMBS_DIR", str(thumbs))
    os.makedirs(thumbs, exist_ok=True)
    yield app_dir


@pytest.fixture
def db():
    database = Database()
    yield database
    database.close()


@pytest.fixture
def state(db):
    return AppState(db)


@pytest.fixture
def make_memory():
    def factory(
        title: str = "A memory",
        day: date = date(2024, 6, 1),
        notes: str = "",
        category: str = "",
        photos: list[str] | None = None,
    ) -> Memory:
        return Memory.new(
            title=title, day=day, notes=notes, category=category, photos=photos
        )

    return factory


@pytest.fixture
def sample_png(tmp_path):
    path = tmp_path / "sample.png"
    Image.new("RGB", (800, 600), (200, 60, 120)).save(path, "PNG")
    return str(path)
