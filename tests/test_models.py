"""Tests for the Memory data model."""

from __future__ import annotations

from datetime import date, datetime

from timecapsule.models import Memory


def test_new_generates_unique_ids():
    a = Memory.new("First", date(2024, 1, 1))
    b = Memory.new("Second", date(2024, 1, 1))
    assert a.id != b.id
    assert len(a.id) == 32  # uuid4 hex


def test_new_sets_created_at_iso_seconds():
    m = Memory.new("Stamped", date(2024, 1, 1))
    parsed = datetime.fromisoformat(m.created_at)
    assert abs((datetime.now() - parsed).total_seconds()) < 60


def test_new_defaults():
    m = Memory.new("Bare", date(2023, 5, 4))
    assert m.notes == ""
    assert m.category == ""
    assert m.photos == []
    assert m.day == date(2023, 5, 4)


def test_new_copies_photo_list():
    photos = ["a.jpg", "b.jpg"]
    m = Memory.new("Pics", date(2024, 1, 1), photos=photos)
    photos.append("c.jpg")
    assert m.photos == ["a.jpg", "b.jpg"]


def test_photo_lists_independent_between_instances():
    a = Memory.new("A", date(2024, 1, 1))
    b = Memory.new("B", date(2024, 1, 1))
    a.photos.append("only-a.jpg")
    assert b.photos == []
