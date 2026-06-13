"""Application shell: navigation, search, CSV, updates, and wiring."""

from __future__ import annotations

import asyncio
import csv
import os
import webbrowser
from datetime import date, datetime

import flet as ft

from . import APP_NAME, VERSION, updates
from .models import Memory
from .state import AppState
from .storage import res_path
from .theme import accent, apply_theme, set_accent
from .views.gallery import build_gallery
from .views.memory_dialog import CategoryManager, MemoryDialog
from .views.on_this_day import build_banner, maybe_show_dialog
from .views.stats import build_stats
from .views.theme_dialog import ThemeDialog
from .views.timeline import build_timeline

CSV_FIELDS = ["Title", "Date", "Notes", "Category"]


class TimeCapsuleApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.state = AppState()
        self.tab_index = 0

        page.title = f"{APP_NAME} v{VERSION}"
        page.window.min_width = 760
        page.window.min_height = 560
        icon = res_path("time.ico")
        if os.path.exists(icon):
            page.window.icon = icon
        set_accent(self.state.settings.get("accent", accent()))
        apply_theme(page)
        page.theme_mode = (
            ft.ThemeMode.LIGHT
            if self.state.settings.get("theme_mode") == "light"
            else ft.ThemeMode.DARK
        )

        self.file_picker = ft.FilePicker()
        page.services.append(self.file_picker)

        self.search_field = ft.TextField(
            hint_text="Search memories…",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=24,
            dense=True,
            width=280,
            on_change=self._on_search,
        )

        self.rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=88,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.TIMELINE_OUTLINED,
                    selected_icon=ft.Icons.TIMELINE,
                    label="Timeline",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PHOTO_LIBRARY_OUTLINED,
                    selected_icon=ft.Icons.PHOTO_LIBRARY,
                    label="Gallery",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FAVORITE_OUTLINE,
                    selected_icon=ft.Icons.FAVORITE,
                    label="Stats",
                ),
            ],
            on_change=self._on_nav,
        )

        self.content = ft.Container(expand=True)

        page.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.HOURGLASS_TOP, color=accent()),
            title=ft.Row(
                [
                    ft.Text(APP_NAME, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        f"v{VERSION}",
                        size=11,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.END,
            ),
            center_title=False,
            actions=[
                self.search_field,
                ft.IconButton(
                    icon=ft.Icons.BRIGHTNESS_6,
                    tooltip="Toggle light/dark",
                    on_click=self._toggle_theme,
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            content="Manage categories",
                            icon=ft.Icons.LABEL_OUTLINE,
                            on_click=lambda _: CategoryManager(
                                self.page, self.state, self.refresh
                            ).open(),
                        ),
                        ft.PopupMenuItem(
                            content="Appearance",
                            icon=ft.Icons.PALETTE_OUTLINED,
                            on_click=lambda _: ThemeDialog(
                                self.page, self.state, self._on_theme_change
                            ).open(),
                        ),
                        ft.PopupMenuItem(),
                        ft.PopupMenuItem(
                            content="Check for updates",
                            icon=ft.Icons.SYSTEM_UPDATE_ALT,
                            on_click=self._manual_update_check,
                        ),
                        ft.PopupMenuItem(
                            content="Export to CSV",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=self._export_csv,
                        ),
                        ft.PopupMenuItem(
                            content="Import from CSV",
                            icon=ft.Icons.DOWNLOAD,
                            on_click=self._import_csv,
                        ),
                        ft.PopupMenuItem(),
                        ft.PopupMenuItem(
                            content="About",
                            icon=ft.Icons.INFO_OUTLINE,
                            on_click=lambda _: self._about(),
                        ),
                    ]
                ),
            ],
        )

        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Add a memory",
            bgcolor=accent(),
            on_click=lambda _: self._open_memory(None),
        )

        page.add(
            ft.Row(
                [self.rail, ft.VerticalDivider(width=1), self.content],
                expand=True,
                spacing=0,
            )
        )
        self.refresh()
        maybe_show_dialog(page, self.state)
        if self.state.settings.get("update_check", "on") != "off":
            page.run_task(self._startup_update_check)

    # ------------------------------------------------------------ rendering

    def refresh(self) -> None:
        if self.tab_index == 0:
            banner = build_banner(self.state, self._open_memory)
            self.content.content = build_timeline(
                self.state,
                self._open_memory,
                self._confirm_delete_memory,
                header=banner,
            )
        elif self.tab_index == 1:
            self.content.content = build_gallery(
                self.page, self.state, self._open_memory
            )
        else:
            self.content.content = build_stats(self.state)
        self.page.update()

    def _on_nav(self, e: ft.ControlEvent) -> None:
        self.tab_index = e.control.selected_index
        self.refresh()

    def _on_search(self, e: ft.ControlEvent) -> None:
        self.state.search = e.control.value
        if self.tab_index != 0:
            self.tab_index = 0
            self.rail.selected_index = 0
        self.refresh()

    def _toggle_theme(self, _) -> None:
        mode = "light" if self.page.theme_mode == ft.ThemeMode.DARK else "dark"
        self.state.set_setting("theme_mode", mode)
        self.page.theme_mode = (
            ft.ThemeMode.LIGHT if mode == "light" else ft.ThemeMode.DARK
        )
        self.page.update()

    def _on_theme_change(self) -> None:
        """Re-tint accent-colored chrome after the user picks a new theme."""
        self.page.appbar.leading = ft.Icon(ft.Icons.HOURGLASS_TOP, color=accent())
        self.page.floating_action_button.bgcolor = accent()
        self.refresh()

    # -------------------------------------------------------------- dialogs

    def _open_memory(self, memory: Memory | None) -> None:
        MemoryDialog(self.page, self.state, memory, self.refresh).open()

    def _confirm_delete_memory(self, memory: Memory) -> None:
        confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete memory?"),
            content=ft.Text(f'"{memory.title}" and its photos will be removed.'),
            actions=[
                ft.TextButton("Keep it", on_click=lambda _: self.page.pop_dialog()),
                ft.FilledButton(
                    "Delete",
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ERROR, color=ft.Colors.ON_ERROR
                    ),
                    on_click=lambda _: self._delete_memory(memory),
                ),
            ],
        )
        self.page.show_dialog(confirm)

    def _delete_memory(self, memory: Memory) -> None:
        self.page.pop_dialog()
        self.state.remove(memory)
        self.refresh()
        self._snack("Memory deleted")

    def _about(self) -> None:
        dlg = ft.AlertDialog(
            title=ft.Text(f"{APP_NAME} v{VERSION}"),
            content=ft.Text(
                "A memory journal for the moments that matter.\n\n"
                "Made with love. Icon by Pixel Perfect from Flaticon."
            ),
            actions=[ft.TextButton("Close", on_click=lambda _: self.page.pop_dialog())],
        )
        self.page.show_dialog(dlg)

    def _snack(self, message: str) -> None:
        self.page.show_dialog(ft.SnackBar(ft.Text(message)))

    # -------------------------------------------------------------- updates

    async def _startup_update_check(self) -> None:
        latest = await asyncio.to_thread(updates.fetch_latest_version)
        if latest and updates.is_newer(latest):
            self._show_update_dialog(latest)

    async def _manual_update_check(self) -> None:
        self._snack("Checking for updates…")
        latest = await asyncio.to_thread(updates.fetch_latest_version)
        if latest is None:
            self._snack("Could not reach GitHub to check for updates")
        elif updates.is_newer(latest):
            self._show_update_dialog(latest)
        else:
            self._snack(f"You're up to date (v{VERSION})")

    def _show_update_dialog(self, latest: str) -> None:
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Update available"),
            content=ft.Text(
                f"Time Capsule {latest.lstrip('v')} is available — "
                f"you have v{VERSION}.\n\n"
                "Download the new installer from GitHub?"
            ),
            actions=[
                ft.TextButton("Later", on_click=lambda _: self.page.pop_dialog()),
                ft.FilledButton(
                    "Download",
                    on_click=lambda _: (
                        webbrowser.open(updates.RELEASES_PAGE),
                        self.page.pop_dialog(),
                    ),
                ),
            ],
        )
        self.page.show_dialog(dlg)

    # ------------------------------------------------------------------ CSV

    async def _export_csv(self) -> None:
        path = await self.file_picker.save_file(
            dialog_title="Export memories",
            file_name="memories_export.csv",
            allowed_extensions=["csv"],
        )
        if not path:
            return
        if not path.lower().endswith(".csv"):
            path += ".csv"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(CSV_FIELDS)
            for m in sorted(self.state.memories, key=lambda m: m.day):
                writer.writerow([m.title, m.day.isoformat(), m.notes, m.category])
        self._snack(f"Exported {len(self.state.memories)} memories")

    async def _import_csv(self) -> None:
        files = await self.file_picker.pick_files(
            dialog_title="Import memories",
            allowed_extensions=["csv"],
        )
        if not files or not files[0].path:
            return
        added = skipped = 0
        try:
            with open(files[0].path, "r", newline="", encoding="utf-8-sig") as fh:
                for row in csv.DictReader(fh):
                    title = (row.get("Title") or row.get("Event") or "").strip()
                    day = _parse_csv_date(row.get("Date", ""))
                    if not title or day is None:
                        skipped += 1
                        continue
                    self.state.add(
                        Memory.new(
                            title=title,
                            day=day,
                            notes=(row.get("Notes") or "").strip(),
                            category=(row.get("Category") or "").strip(),
                        )
                    )
                    added += 1
        except (OSError, csv.Error):
            self._snack("Could not read that CSV file")
            return
        if added:
            self.refresh()
        self._snack(
            f"Imported {added} memories" + (f", skipped {skipped}" if skipped else "")
        )


def _parse_csv_date(raw: str) -> date | None:
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def main(page: ft.Page) -> None:
    TimeCapsuleApp(page)
