"""Appearance dialog: theme presets, custom accent color, light/dark mode."""

from __future__ import annotations

from typing import Callable

import flet as ft

from ..state import AppState
from ..theme import PRESETS, accent, apply_theme, is_valid_hex, set_accent


class ThemeDialog:
    """Lets the user pick a preset theme or enter a custom accent color."""

    def __init__(self, page: ft.Page, state: AppState, on_change: Callable[[], None]):
        self.page = page
        self.state = state
        self.on_change = on_change

        self.swatch_row = ft.Row(wrap=True, spacing=10)
        self.hex_field = ft.TextField(
            label="Custom color (hex)",
            value=accent(),
            width=200,
            max_length=7,
            on_submit=self._apply_hex,
        )
        self.mode_group = ft.RadioGroup(
            value=self.state.settings.get("theme_mode", "dark"),
            content=ft.Row(
                [
                    ft.Radio(value="light", label="Light"),
                    ft.Radio(value="dark", label="Dark"),
                ]
            ),
            on_change=self._mode_changed,
        )
        self._rebuild_swatches()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Appearance"),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    [
                        ft.Text("Theme", weight=ft.FontWeight.BOLD),
                        self.swatch_row,
                        ft.Row(
                            [
                                self.hex_field,
                                ft.FilledTonalButton("Apply", on_click=self._apply_hex),
                            ],
                            spacing=10,
                        ),
                        ft.Divider(),
                        ft.Text("Mode", weight=ft.FontWeight.BOLD),
                        self.mode_group,
                    ],
                    tight=True,
                    spacing=12,
                ),
            ),
            actions=[ft.TextButton("Done", on_click=lambda _: self.page.pop_dialog())],
        )

    def open(self) -> None:
        self.page.show_dialog(self.dialog)

    def _rebuild_swatches(self) -> None:
        tiles = []
        for name, color in PRESETS.items():
            selected = color.lower() == accent().lower()
            tiles.append(
                ft.Column(
                    [
                        ft.Container(
                            width=44,
                            height=44,
                            bgcolor=color,
                            border_radius=22,
                            border=ft.Border.all(3, ft.Colors.ON_SURFACE) if selected else None,
                            content=ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=20)
                            if selected
                            else None,
                            alignment=ft.Alignment.CENTER,
                            tooltip=name,
                            on_click=lambda _, c=color: self._set_color(c),
                        ),
                        ft.Text(name, size=10),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        self.swatch_row.controls = tiles

    def _set_color(self, color: str) -> None:
        set_accent(color)
        self.state.set_setting("accent", color)
        apply_theme(self.page)
        self.hex_field.value = color
        self.hex_field.error = None
        self._rebuild_swatches()
        self.dialog.update()
        self.on_change()

    def _apply_hex(self, _) -> None:
        raw = (self.hex_field.value or "").strip()
        if not raw.startswith("#"):
            raw = "#" + raw
        if not is_valid_hex(raw):
            self.hex_field.error = "Use a 6-digit hex color, e.g. #E91E63"
            self.hex_field.update()
            return
        self._set_color(raw.upper())

    def _mode_changed(self, e: ft.ControlEvent) -> None:
        mode = e.control.value
        self.state.set_setting("theme_mode", mode)
        self.page.theme_mode = (
            ft.ThemeMode.LIGHT if mode == "light" else ft.ThemeMode.DARK
        )
        self.page.update()
