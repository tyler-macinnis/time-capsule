"""Application shell: navigation, search, backup, updates, and wiring."""

from __future__ import annotations

import asyncio
import os
import sqlite3
import webbrowser
from datetime import date

import flet as ft

from . import APP_NAME, VERSION, storage, updates
from .models import Memory
from .state import AppState
from .storage import res_path
from .theme import accent, apply_theme, set_accent, set_highlight, theme_mode
from .views.gallery import build_gallery
from .views.memory_dialog import CategoryManager, MemoryDialog
from .views.on_this_day import build_banner, maybe_show_dialog
from .views.stats import build_stats
from .views.theme_dialog import ThemeDialog
from .views.timeline import build_timeline


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
        self._apply_settings()

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
                            content="Back up everything",
                            icon=ft.Icons.BACKUP_OUTLINED,
                            on_click=self._backup,
                        ),
                        ft.PopupMenuItem(
                            content="Restore from backup",
                            icon=ft.Icons.RESTORE,
                            on_click=self._restore,
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

    def _apply_settings(self) -> None:
        """Apply the stored accent and light/dark mode to the page."""
        set_accent(self.state.settings.get("accent", ""))  # invalid -> default
        set_highlight(self.state.settings.get("highlight", ""))
        apply_theme(self.page)
        self.page.theme_mode = theme_mode(self.state.settings.get("theme_mode"))

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
        self.page.theme_mode = theme_mode(mode)
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
            content=ft.Column(
                [
                    ft.Image(src=res_path("time.png"), width=96, height=96),
                    ft.Text(
                        "A memory journal for the moments that matter.\n\n"
                        "Made with love.",
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                tight=True,
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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

    # --------------------------------------------------------------- backup

    async def _backup(self) -> None:
        path = await self.file_picker.save_file(
            dialog_title="Back up everything",
            file_name=f"time-capsule-backup-{date.today().isoformat()}.zip",
            allowed_extensions=["zip"],
        )
        if not path:
            return
        if not path.lower().endswith(".zip"):
            path += ".zip"
        self._snack("Backing up…")
        try:
            await asyncio.to_thread(storage.create_backup, path)
        except (OSError, sqlite3.Error):
            self._snack("Could not write the backup file")
            return
        self._snack("Backup saved, including photos")

    async def _restore(self) -> None:
        files = await self.file_picker.pick_files(
            dialog_title="Restore from backup",
            allowed_extensions=["zip"],
        )
        if not files or not files[0].path:
            return
        path = files[0].path
        confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("Restore this backup?"),
            content=ft.Text(
                "Everything currently in Time Capsule (memories, photos, "
                "categories, and settings) will be replaced by the backup. "
                "This cannot be undone."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.page.pop_dialog()),
                ft.FilledButton(
                    "Replace everything",
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ERROR, color=ft.Colors.ON_ERROR
                    ),
                    on_click=lambda _: self._do_restore(path),
                ),
            ],
        )
        self.page.show_dialog(confirm)

    def _do_restore(self, path: str) -> None:
        self.page.pop_dialog()
        # Deliberately synchronous: no other handler can touch the closed DB.
        self.state.db.close()
        try:
            storage.restore_backup(path)
            message = "Backup restored"
        except storage.BackupError:
            message = "That file is not a Time Capsule backup; nothing was changed"
        except OSError:
            message = "Restore failed partway; try restoring the backup again"
        self.state = AppState()
        self.state.search = self.search_field.value or ""
        self._apply_settings()
        self._on_theme_change()
        self._snack(message)


def main(page: ft.Page) -> None:
    TimeCapsuleApp(page)
