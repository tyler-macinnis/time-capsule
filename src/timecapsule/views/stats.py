"""Stats dashboard."""

from __future__ import annotations

from datetime import date

import flet as ft

from ..state import AppState
from ..theme import GOLD, accent, category_color
from ..utils import time_since, upcoming_anniversaries


def _stat_card(
    icon: str, label: str, value: str, color: str | None = None
) -> ft.Control:
    color = color or accent()
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(icon, size=30, color=color),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD),
                ft.Text(label, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        padding=20,
        border_radius=14,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        expand=True,
    )


def _section(title: str, *controls: ft.Control) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            [ft.Text(title, size=16, weight=ft.FontWeight.BOLD), *controls],
            spacing=10,
        ),
        padding=20,
        border_radius=14,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )


def build_stats(state: AppState) -> ft.Control:
    today = date.today()
    sections: list[ft.Control] = []

    # ---- headline cards
    total_photos = sum(len(m.photos) for m in state.memories)
    cards = [
        _stat_card(ft.Icons.AUTO_STORIES, "Memories", str(len(state.memories))),
        _stat_card(ft.Icons.PHOTO_CAMERA, "Photos", str(total_photos), GOLD),
    ]
    if state.memories:
        first = min(m.day for m in state.memories)
        span = (today - first).days
        if span > 0:
            cards.insert(
                0, _stat_card(ft.Icons.HISTORY, "Days of history", f"{span:,}")
            )
    sections.append(ft.Row(cards, spacing=12))

    # ---- memories by category
    if state.memories:
        counts: dict[str, int] = {}
        for m in state.memories:
            counts[m.category or "(none)"] = counts.get(m.category or "(none)", 0) + 1
        max_count = max(counts.values())
        bars = []
        for name, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            color = category_color(state.categories, name)
            bars.append(
                ft.Row(
                    [
                        ft.Text(
                            name, size=13, width=140, overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Container(
                            width=max(20, 360 * count / max_count),
                            height=16,
                            bgcolor=color,
                            border_radius=8,
                        ),
                        ft.Text(str(count), size=13),
                    ],
                    spacing=10,
                )
            )
        sections.append(_section("Memories by category", *bars))

    # ---- upcoming anniversaries
    upcoming = upcoming_anniversaries(state.memories, today, limit=5)
    if upcoming:
        rows = []
        for m, nxt_date, days_until in upcoming:
            when = (
                "Today!"
                if days_until == 0
                else ("Tomorrow" if days_until == 1 else f"in {days_until} days")
            )
            rows.append(
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.CAKE if days_until == 0 else ft.Icons.EVENT,
                            size=18,
                            color=accent()
                            if days_until == 0
                            else ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            m.title, expand=True, overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        ft.Text(
                            time_since(m.day),
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                        ),
                        ft.Text(
                            f"{nxt_date.strftime('%b %d')} · {when}",
                            size=12,
                            weight=ft.FontWeight.BOLD if days_until <= 7 else None,
                        ),
                    ],
                    spacing=10,
                )
            )
        sections.append(_section("Upcoming anniversaries", *rows))

    return ft.ListView(sections, spacing=14, padding=20, expand=True)
