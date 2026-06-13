"""On This Day: surprise memories from past years."""

from __future__ import annotations

import os
from typing import Callable

import flet as ft

from .. import storage
from ..models import Memory
from ..state import AppState
from ..theme import accent
from ..utils import on_this_day, years_ago_text


def build_banner(
    state: AppState,
    on_open: Callable[[Memory], None],
) -> ft.Control | None:
    """A dismissible card shown at the top of the timeline when today matches."""
    matches = on_this_day(state.memories)
    if not matches:
        return None

    rows: list[ft.Control] = [
        ft.Row(
            [
                ft.Icon(ft.Icons.AUTO_AWESOME, color=accent()),
                ft.Text("On this day", size=16, weight=ft.FontWeight.BOLD),
            ],
            spacing=8,
        )
    ]
    for m in matches:
        thumb = None
        if m.photos:
            path = storage.thumb_path(m.photos[0])
            if os.path.exists(path):
                thumb = ft.Image(
                    src=path, width=48, height=48,
                    fit=ft.BoxFit.COVER, border_radius=8,
                )
        rows.append(
            ft.Container(
                content=ft.Row(
                    [
                        thumb or ft.Icon(ft.Icons.FAVORITE, color=accent(), size=28),
                        ft.Column(
                            [
                                ft.Text(m.title, weight=ft.FontWeight.BOLD),
                                ft.Text(years_ago_text(m.day), size=12, italic=True),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, size=18),
                    ],
                    spacing=12,
                ),
                ink=True,
                border_radius=10,
                padding=8,
                on_click=lambda _, m=m: on_open(m),
            )
        )

    return ft.Container(
        content=ft.Column(rows, spacing=6),
        padding=14,
        border_radius=12,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[ft.Colors.with_opacity(0.25, accent()), ft.Colors.SURFACE_CONTAINER_HIGHEST],
        ),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.5, accent())),
    )


def maybe_show_dialog(page: ft.Page, state: AppState) -> None:
    """One-shot greeting dialog at startup when there are matches today."""
    matches = on_this_day(state.memories)
    if not matches:
        return
    first = matches[0]
    body: list[ft.Control] = []
    if first.photos:
        path = storage.photo_path(first.photos[0])
        if os.path.exists(path):
            body.append(
                ft.Image(src=path, height=240, fit=ft.BoxFit.COVER, border_radius=10)
            )
    body.append(ft.Text(first.title, size=18, weight=ft.FontWeight.BOLD))
    body.append(ft.Text(years_ago_text(first.day), italic=True, color=accent()))
    if first.notes:
        body.append(ft.Text(first.notes, size=13, max_lines=4,
                            overflow=ft.TextOverflow.ELLIPSIS))
    if len(matches) > 1:
        body.append(
            ft.Text(f"…and {len(matches) - 1} more from this day", size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT)
        )

    dlg = ft.AlertDialog(
        title=ft.Row(
            [ft.Icon(ft.Icons.AUTO_AWESOME, color=accent()), ft.Text("On this day…")],
            spacing=8,
        ),
        content=ft.Container(
            width=420,
            content=ft.Column(body, tight=True, spacing=8,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ),
        actions=[ft.FilledButton("Relive it", on_click=lambda _: page.pop_dialog())],
    )
    page.show_dialog(dlg)
