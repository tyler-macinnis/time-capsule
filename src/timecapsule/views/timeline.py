"""Timeline view: memories grouped by year, newest first."""

from __future__ import annotations

import os
from typing import Callable

import flet as ft

from .. import storage
from ..models import Memory
from ..state import AppState
from ..theme import category_color
from ..utils import time_since


def _thumb_strip(memory: Memory) -> ft.Control | None:
    thumbs = []
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
) -> ft.Control:
    color = category_color(state.categories, memory.category)
    body: list[ft.Control] = [
        ft.Row(
            [
                ft.Text(memory.title, size=17, weight=ft.FontWeight.BOLD, expand=True),
                ft.Text(
                    memory.day.strftime("%B %d, %Y"),
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
            ]
        ),
        ft.Text(time_since(memory.day), size=12, italic=True, color=color),
    ]
    if memory.notes:
        body.append(
            ft.Text(
                memory.notes,
                size=13,
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        )
    strip = _thumb_strip(memory)
    if strip:
        body.append(strip)
    if memory.category:
        body.append(
            ft.Container(
                content=ft.Text(memory.category, size=11, color=ft.Colors.WHITE),
                bgcolor=color,
                border_radius=20,
                padding=ft.Padding.symmetric(horizontal=10, vertical=3),
            )
        )
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(width=5, border_radius=4, bgcolor=color),
                ft.Column(body, spacing=6, expand=True),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        padding=14,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        ink=True,
        on_click=lambda _: on_open(memory),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )


def build_timeline(
    state: AppState,
    on_open: Callable[[Memory], None],
    header: ft.Control | None = None,
) -> ft.Control:
    memories = state.filtered_memories()
    controls: list[ft.Control] = []
    if header:
        controls.append(header)
    if not memories:
        controls.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.FAVORITE_BORDER, size=64, color=ft.Colors.OUTLINE),
                        ft.Text(
                            "No memories yet — add your first one with the + button",
                            color=ft.Colors.OUTLINE,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                alignment=ft.Alignment.CENTER,
                padding=60,
            )
        )
    year = None
    for m in memories:
        if m.day.year != year:
            year = m.day.year
            controls.append(
                ft.Container(
                    content=ft.Text(str(year), size=22, weight=ft.FontWeight.BOLD),
                    padding=ft.Padding.only(top=10),
                )
            )
        controls.append(memory_card(m, state, on_open))
    return ft.ListView(controls, spacing=10, padding=20, expand=True)
