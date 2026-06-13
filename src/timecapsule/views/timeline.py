"""Timeline view: a vertical rail of memories grouped by year and month.

Layout notes
------------
Every entry is an ``ft.Stack``. The card (the only *non-positioned* child)
determines the stack height; the rail line is a positioned child with
``top=0`` and ``bottom=0`` so it always matches the card height exactly.
This avoids ``CrossAxisAlignment.STRETCH`` inside ``ListView`` items, which
has unbounded height and breaks rendering of the whole list.
"""

from __future__ import annotations

import os
from typing import Callable

import flet as ft

from .. import storage
from ..models import Memory
from ..state import AppState
from ..theme import accent, category_color
from ..utils import time_since

# Rail geometry (px)
LINE_X = 19  # left edge of the 2px rail line (centered on x=20)
LINE_W = 2
DOT_SIZE = 14
CONTENT_LEFT = 48  # where cards / labels start
CARD_GAP = 14  # vertical gap between cards (drawn inside the stack)


def _rail_line() -> ft.Container:
    """A vertical line segment that fills its parent Stack's height."""
    return ft.Container(
        left=LINE_X,
        top=0,
        bottom=0,
        width=LINE_W,
        bgcolor=ft.Colors.OUTLINE_VARIANT,
    )


def _rail_dot(color: str, top: float, size: int = DOT_SIZE) -> ft.Container:
    return ft.Container(
        left=LINE_X + LINE_W / 2 - size / 2,
        top=top,
        width=size,
        height=size,
        border_radius=size / 2,
        bgcolor=color,
        border=ft.Border.all(2, ft.Colors.SURFACE),
    )


def _year_header(year: int) -> ft.Control:
    """An accent-tinted year pill with a horizontal rule trailing off."""
    pill = ft.Container(
        content=ft.Text(
            str(year),
            size=15,
            weight=ft.FontWeight.BOLD,
            color=accent(),
        ),
        bgcolor=ft.Colors.with_opacity(0.12, accent()),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.45, accent())),
        border_radius=20,
        padding=ft.Padding.symmetric(horizontal=16, vertical=5),
    )
    return ft.Container(
        content=ft.Row(
            [
                pill,
                ft.Container(
                    height=1,
                    bgcolor=ft.Colors.OUTLINE_VARIANT,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(top=18, bottom=10),
    )


def _month_label(month_name: str) -> ft.Control:
    """A small muted month marker sitting on the rail."""
    label = ft.Container(
        content=ft.Text(
            month_name.upper(),
            size=11,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.ON_SURFACE_VARIANT,
        ),
        margin=ft.Margin.only(left=CONTENT_LEFT, top=4, bottom=8),
    )
    return ft.Stack(
        [
            _rail_line(),
            _rail_dot(ft.Colors.OUTLINE_VARIANT, top=7, size=8),
            label,
        ]
    )


def _thumb_strip(memory: Memory) -> ft.Control | None:
    thumbs: list[ft.Control] = []
    shown = 0
    for name in memory.photos[:4]:
        path = storage.thumb_path(name)
        if os.path.exists(path):
            shown += 1
            thumbs.append(
                ft.Image(
                    src=path,
                    width=72,
                    height=72,
                    fit=ft.BoxFit.COVER,
                    border_radius=8,
                )
            )
    if not thumbs:
        return None
    extra = len(memory.photos) - shown
    if extra > 0:
        thumbs.append(
            ft.Container(
                content=ft.Text(f"+{extra}", weight=ft.FontWeight.BOLD),
                width=72,
                height=72,
                border_radius=8,
                bgcolor=ft.Colors.SECONDARY_CONTAINER,
                alignment=ft.Alignment.CENTER,
            )
        )
    return ft.Row(thumbs, spacing=6)


def memory_card(
    memory: Memory,
    state: AppState,
    on_open: Callable[[Memory], None],
    on_delete: Callable[[Memory], None],
) -> ft.Control:
    """The card body shown to the right of the rail."""
    color = category_color(state.categories, memory.category)
    body: list[ft.Control] = [
        ft.Row(
            [
                ft.Text(
                    memory.title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_size=18,
                    tooltip="Edit memory",
                    on_click=lambda _: on_open(memory),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=18,
                    tooltip="Delete memory",
                    on_click=lambda _: on_delete(memory),
                ),
            ],
            spacing=0,
        ),
        ft.Row(
            [
                ft.Text(
                    memory.day.strftime("%B %d, %Y"),
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Text("\u00b7", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(time_since(memory.day), size=12, italic=True, color=color),
            ],
            spacing=6,
        ),
    ]
    if memory.notes:
        body.append(
            ft.Text(
                memory.notes,
                size=13,
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS,
                color=ft.Colors.ON_SURFACE_VARIANT,
            )
        )
    strip = _thumb_strip(memory)
    if strip:
        body.append(strip)
    if memory.category:
        body.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            memory.category,
                            size=11,
                            weight=ft.FontWeight.W_600,
                            color=ft.Colors.WHITE,
                        ),
                        bgcolor=color,
                        border_radius=20,
                        padding=ft.Padding.symmetric(horizontal=10, vertical=3),
                    )
                ]
            )
        )
    return ft.Container(
        content=ft.Column(body, spacing=6),
        padding=ft.Padding.only(left=16, right=10, top=10, bottom=14),
        border_radius=14,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border=ft.Border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.ON_SURFACE)),
        ink=True,
        on_click=lambda _: on_open(memory),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )


def _timeline_entry(
    memory: Memory,
    state: AppState,
    on_open: Callable[[Memory], None],
    on_delete: Callable[[Memory], None],
) -> ft.Control:
    """A memory card on the rail: line + category dot + card."""
    color = category_color(state.categories, memory.category)
    card = ft.Container(
        content=memory_card(memory, state, on_open, on_delete),
        margin=ft.Margin.only(left=CONTENT_LEFT, bottom=CARD_GAP),
    )
    return ft.Stack(
        [
            _rail_line(),
            _rail_dot(color, top=16),
            card,
        ]
    )


def _empty_state(searching: bool, query: str) -> ft.Control:
    if searching:
        icon, text = ft.Icons.SEARCH_OFF, f"No memories match \u201c{query}\u201d"
    else:
        icon, text = (
            ft.Icons.FAVORITE_BORDER,
            "No memories yet \u2014 add your first one with the + button",
        )
    return ft.Container(
        content=ft.Column(
            [
                ft.Icon(icon, size=64, color=ft.Colors.OUTLINE),
                ft.Text(text, color=ft.Colors.OUTLINE),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        ),
        alignment=ft.Alignment.CENTER,
        padding=60,
    )


def build_timeline(
    state: AppState,
    on_open: Callable[[Memory], None],
    on_delete: Callable[[Memory], None],
    header: ft.Control | None = None,
) -> ft.Control:
    memories = state.filtered_memories()
    query = state.search.strip()
    controls: list[ft.Control] = []
    if header:
        controls.append(ft.Container(content=header, margin=ft.Margin.only(bottom=14)))
    if query and memories:
        count = len(memories)
        controls.append(
            ft.Container(
                content=ft.Text(
                    f"{count} memor{'y' if count == 1 else 'ies'}"
                    f" match \u201c{query}\u201d",
                    size=12,
                    italic=True,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                margin=ft.Margin.only(bottom=6),
            )
        )
    if not memories:
        controls.append(_empty_state(bool(query), query))
    year: int | None = None
    month: int | None = None
    for m in memories:
        if m.day.year != year:
            year = m.day.year
            month = None
            controls.append(_year_header(year))
        if m.day.month != month:
            month = m.day.month
            controls.append(_month_label(m.day.strftime("%B")))
        controls.append(_timeline_entry(m, state, on_open, on_delete))
    return ft.ListView(controls, spacing=0, padding=20, expand=True)
