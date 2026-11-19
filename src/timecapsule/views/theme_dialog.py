"""Appearance dialog: accent and highlight colors, light/dark/system mode."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from ..state import AppState
from ..theme import (
    DEFAULT_ACCENT,
    GOLD,
    PRESETS,
    accent,
    apply_theme,
    highlight,
    is_valid_hex,
    set_accent,
    set_highlight,
    theme_mode,
)


class ThemeDialog:
    """Lets the user recolor the app from presets or custom hex colors."""

    def __init__(self, page: ft.Page, state: AppState, on_change: Callable[[], None]):
        self.page = page
        self.state = state
        self.on_change = on_change
        self.target = "accent"  # which color the swatches and hex field edit

        self.target_group = ft.RadioGroup(
            value=self.target,
            content=ft.Row(
                [
                    ft.Radio(value="accent", label="Accent"),
                    ft.Radio(value="highlight", label="Highlight"),
                ]
            ),
            on_change=self._target_changed,
        )
        self.swatch_row = ft.Row(wrap=True, spacing=10)
        self.hex_field = ft.TextField(
            label="Custom color (hex)",
            value=accent(),
            width=200,
            max_length=7,
            on_submit=self._apply_hex,
        )
        self.mode_group = ft.RadioGroup(
            value=theme_mode(self.state.settings.get("theme_mode")).value,
            content=ft.Row(
                [
                    ft.Radio(value="light", label="Light"),
                    ft.Radio(value="dark", label="Dark"),
                    ft.Radio(value="system", label="System"),
                ]
            ),
            on_change=self._mode_changed,
        )
        self._rebuild_swatches()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Appearance"),
            content=ft.Container(
                width=460,
                content=ft.Column(
                    [
                        ft.Text("Color", weight=ft.FontWeight.BOLD),
                        self.target_group,
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
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton("Reset colors", on_click=self._reset),
                ft.TextButton("Done", on_click=lambda _: self.page.pop_dialog()),
            ],
        )

    def open(self) -> None:
        self.page.show_dialog(self.dialog)

    def _current(self) -> str:
        return accent() if self.target == "accent" else highlight()

    def _rebuild_swatches(self) -> None:
        tiles = []
        for name, color in PRESETS.items():
            selected = color.lower() == self._current().lower()
            tiles.append(
                ft.Column(
                    [
                        ft.Container(
                            width=44,
                            height=44,
                            bgcolor=color,
                            border_radius=22,
                            border=ft.Border.all(3, ft.Colors.ON_SURFACE)
                            if selected
                            else None,
                            content=ft.Icon(
                                ft.Icons.CHECK, color=ft.Colors.WHITE, size=20
                            )
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

    def _refresh(self) -> None:
        """Re-theme the page and re-sync the dialog after a color change."""
        apply_theme(self.page)
        self.hex_field.value = self._current()
        self.hex_field.error = None
        self._rebuild_swatches()
        self.dialog.update()
        self.on_change()

    def _set_color(self, color: str) -> None:
        (set_accent if self.target == "accent" else set_highlight)(color)
        self.state.set_setting(self.target, color)
        self._refresh()

    def _reset(self, _) -> None:
        set_accent(DEFAULT_ACCENT)
        set_highlight(GOLD)
        self.state.set_setting("accent", DEFAULT_ACCENT)
        self.state.set_setting("highlight", GOLD)
        self._refresh()

    def _target_changed(self, e: ft.ControlEvent) -> None:
        self.target = e.control.value
        self.hex_field.value = self._current()
        self.hex_field.error = None
        self._rebuild_swatches()
        self.dialog.update()

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
        self.page.theme_mode = theme_mode(mode)
        self.page.update()
