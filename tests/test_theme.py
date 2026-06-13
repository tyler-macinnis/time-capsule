"""Tests for theme accent handling and category colors."""

from __future__ import annotations

import pytest

from timecapsule import theme
from timecapsule.theme import (
    DEFAULT_ACCENT,
    FALLBACK_CATEGORY_COLOR,
    PRESETS,
    accent,
    category_color,
    is_valid_hex,
    set_accent,
)


@pytest.fixture(autouse=True)
def reset_accent():
    yield
    theme.set_accent(DEFAULT_ACCENT)


def test_set_accent_valid_hex():
    set_accent("#0288D1")
    assert accent() == "#0288D1"


@pytest.mark.parametrize("bad", ["red", "#12345", "#1234567", "0288D1", "", None])
def test_set_accent_invalid_falls_back_to_default(bad):
    set_accent("#0288D1")
    set_accent(bad)
    assert accent() == DEFAULT_ACCENT


@pytest.mark.parametrize(
    ("value", "valid"),
    [
        ("#E91E63", True),
        ("#abcdef", True),
        ("#ABCDEF", True),
        ("#GGGGGG", False),
        ("#FFF", False),
        ("FFFFFF", False),
        ("", False),
        (None, False),
    ],
)
def test_is_valid_hex(value, valid):
    assert is_valid_hex(value) is valid


def test_presets_are_valid_hex():
    assert PRESETS  # non-empty
    for name, color in PRESETS.items():
        assert is_valid_hex(color), f"preset {name} has invalid color {color}"


def test_category_color_lookup_and_fallback():
    categories = {"Us": "#E91E63"}
    assert category_color(categories, "Us") == "#E91E63"
    assert category_color(categories, "Unknown") == FALLBACK_CATEGORY_COLOR
    assert category_color(categories, "") == FALLBACK_CATEGORY_COLOR
