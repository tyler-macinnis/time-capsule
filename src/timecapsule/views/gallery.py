"""Gallery view: photo grid with a full-size viewer."""

from __future__ import annotations

import os
from typing import Callable

import flet as ft

from .. import storage
from ..models import Memory
from ..state import AppState
from ..utils import time_since


def build_gallery(
    page: ft.Page,
    state: AppState,
    on_open_memory: Callable[[Memory], None],
) -> ft.Control:
    photos = state.all_photos()
    if not photos:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.PHOTO_LIBRARY_OUTLINED, size=64, color=ft.Colors.OUTLINE),
                    ft.Text(
                        "No photos yet — attach some to a memory",
                        color=ft.Colors.OUTLINE,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

    def show_viewer(name: str, memory: Memory) -> None:
        viewer = ft.AlertDialog(
            content=ft.Column(
                [
                    ft.Image(
                        src=storage.photo_path(name),
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=8,
                        expand=True,
                    ),
                    ft.Text(memory.title, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        f"{memory.day.strftime('%B %d, %Y')} · {time_since(memory.day)}",
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                tight=True,
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            actions=[
                ft.TextButton(
                    "Open memory",
                    on_click=lambda _: (page.close(viewer), on_open_memory(memory)),
                ),
                ft.TextButton("Close", on_click=lambda _: page.close(viewer)),
            ],
        )
        page.open(viewer)

    tiles = []
    for name, memory in photos:
        thumb = storage.thumb_path(name)
        if not os.path.exists(thumb):
            continue
        tiles.append(
            ft.Container(
                content=ft.Image(src=thumb, fit=ft.ImageFit.COVER, border_radius=10),
                tooltip=memory.title,
                ink=True,
                border_radius=10,
                on_click=lambda _, n=name, m=memory: show_viewer(n, m),
            )
        )

    return ft.GridView(
        tiles,
        expand=True,
        runs_count=0,
        max_extent=180,
        spacing=10,
        run_spacing=10,
        padding=20,
        child_aspect_ratio=1,
    )
