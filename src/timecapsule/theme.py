"""Theme: user-customizable accent palette for light and dark modes."""

from __future__ import annotations

import re

import flet as ft

DEFAULT_ACCENT = "#E91E63"  # rose
GOLD = "#FFB300"

FALLBACK_CATEGORY_COLOR = "#9E9E9E"

# Named theme presets the user can pick from
PRESETS: dict[str, str] = {
    "Rose": "#E91E63",
    "Lavender": "#9575CD",
    "Ocean": "#0288D1",
    "Forest": "#388E3C",
    "Sunset": "#F4511E",
    "Gold": "#FFB300",
    "Plum": "#8E24AA",
    "Slate": "#546E7A",
}

_accent = DEFAULT_ACCENT


def accent() -> str:
    """The current accent color (hex)."""
    return _accent


def set_accent(color: str) -> None:
    global _accent
    _accent = color if is_valid_hex(color) else DEFAULT_ACCENT


def is_valid_hex(color: str) -> bool:
    return bool(re.fullmatch(r"#[0-9A-Fa-f]{6}", color or ""))


def apply_theme(page: ft.Page) -> None:
    page.theme = ft.Theme(
        color_scheme_seed=_accent,
        use_material3=True,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    page.dark_theme = ft.Theme(
        color_scheme_seed=_accent,
        use_material3=True,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def category_color(categories: dict[str, str], name: str) -> str:
    return categories.get(name, FALLBACK_CATEGORY_COLOR)
