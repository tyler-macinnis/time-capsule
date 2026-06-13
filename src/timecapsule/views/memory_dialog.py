"""Add/edit memory dialog and category manager."""

from __future__ import annotations

import os
from datetime import date, datetime
from typing import Callable

import flet as ft

from .. import storage
from ..models import Memory
from ..state import AppState

SWATCHES = [
    "#E91E63",
    "#F06292",
    "#BA68C8",
    "#7E57C2",
    "#5C6BC0",
    "#42A5F5",
    "#26A69A",
    "#66BB6A",
    "#9CCC65",
    "#FFB300",
    "#FF7043",
    "#8D6E63",
]


class MemoryDialog:
    """Modal dialog for creating or editing a memory."""

    def __init__(
        self,
        page: ft.Page,
        state: AppState,
        memory: Memory | None,
        on_change: Callable[[], None],
    ) -> None:
        self.page = page
        self.state = state
        self.memory = memory
        self.on_change = on_change
        self.day: date = memory.day if memory else date.today()
        self.photos: list[str] = list(memory.photos) if memory else []
        self.added_photos: list[str] = []  # imported during this session
        self.removed_photos: list[str] = []  # pending deletion on save

        self.picker = ft.FilePicker()
        page.services.append(self.picker)

        self.title_field = ft.TextField(
            label="Title",
            value=memory.title if memory else "",
            autofocus=True,
        )
        self.notes_field = ft.TextField(
            label="Notes",
            value=memory.notes if memory else "",
            multiline=True,
            min_lines=3,
            max_lines=6,
        )
        self.category_dd = ft.Dropdown(
            label="Category",
            value=memory.category if memory and memory.category else None,
            options=self._category_options(),
            expand=True,
        )
        self.date_btn = ft.OutlinedButton(
            content=self.day.strftime("%B %d, %Y"),
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self._pick_date,
        )
        self.photo_row = ft.Row(wrap=True, spacing=8)
        self._rebuild_photo_row()

        actions = [
            ft.TextButton("Cancel", on_click=self._cancel),
            ft.FilledButton("Save", on_click=self._save),
        ]
        if memory:
            actions.insert(
                0,
                ft.TextButton(
                    "Delete",
                    style=ft.ButtonStyle(color=ft.Colors.ERROR),
                    on_click=self._confirm_delete,
                ),
            )

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Edit memory" if memory else "New memory"),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    [
                        self.title_field,
                        ft.Row([ft.Text("Date:"), self.date_btn]),
                        self.category_dd,
                        self.notes_field,
                        ft.Row(
                            [
                                ft.Text("Photos", weight=ft.FontWeight.BOLD),
                                ft.TextButton(
                                    "Add photos",
                                    icon=ft.Icons.ADD_PHOTO_ALTERNATE,
                                    on_click=self._add_photos,
                                ),
                            ]
                        ),
                        self.photo_row,
                    ],
                    tight=True,
                    spacing=14,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=actions,
        )

    # ----------------------------------------------------------------- UI

    def open(self) -> None:
        self.page.show_dialog(self.dialog)

    def _category_options(self) -> list[ft.dropdown.Option]:
        opts = [ft.dropdown.Option(key="", text="(none)")]
        for name in sorted(self.state.categories):
            opts.append(ft.dropdown.Option(key=name, text=name))
        return opts

    def _rebuild_photo_row(self) -> None:
        tiles = []
        for name in self.photos:
            path = storage.thumb_path(name)
            if not os.path.exists(path):
                continue
            tiles.append(
                ft.Stack(
                    [
                        ft.Image(
                            src=path,
                            width=90,
                            height=90,
                            fit=ft.BoxFit.COVER,
                            border_radius=8,
                        ),
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=14,
                                icon_color=ft.Colors.WHITE,
                                bgcolor=ft.Colors.BLACK54,
                                on_click=lambda _, n=name: self._remove_photo(n),
                            ),
                            alignment=ft.Alignment.TOP_RIGHT,
                        ),
                    ],
                    width=90,
                    height=90,
                )
            )
        self.photo_row.controls = tiles

    def _pick_date(self, _) -> None:
        dp = ft.DatePicker(
            value=self.day,
            first_date=date(date.min.year, 1, 1),
            last_date=date(date.max.year, 12, 31),
            help_text="Any date works — past or future",
            on_change=self._date_changed,
        )
        self.page.show_dialog(dp)

    def _date_changed(self, e: ft.ControlEvent) -> None:
        if e.control.value:
            value = e.control.value
            self.day = value.date() if isinstance(value, datetime) else value
            self.date_btn.content = self.day.strftime("%B %d, %Y")
            self.date_btn.update()

    async def _add_photos(self) -> None:
        files = await self.picker.pick_files(
            allow_multiple=True,
            file_type=ft.FilePickerFileType.IMAGE,
        )
        for f in files or []:
            if not f.path:
                continue
            name = storage.import_photo(f.path)
            if name:
                self.photos.append(name)
                self.added_photos.append(name)
        self._rebuild_photo_row()
        self.photo_row.update()

    def _remove_photo(self, name: str) -> None:
        self.photos.remove(name)
        if name in self.added_photos:
            self.added_photos.remove(name)
            storage.delete_photo(name)
        else:
            self.removed_photos.append(name)
        self._rebuild_photo_row()
        self.photo_row.update()

    # ------------------------------------------------------------- actions

    def _save(self, _) -> None:
        title = self.title_field.value.strip()
        if not title:
            self.title_field.error = "A title is required"
            self.title_field.update()
            return
        for name in self.removed_photos:
            storage.delete_photo(name)
        if self.memory:
            self.memory.title = title
            self.memory.day = self.day
            self.memory.notes = self.notes_field.value.strip()
            self.memory.category = self.category_dd.value or ""
            self.memory.photos = self.photos
            self.state.update(self.memory)
        else:
            self.state.add(
                Memory.new(
                    title=title,
                    day=self.day,
                    notes=self.notes_field.value.strip(),
                    category=self.category_dd.value or "",
                    photos=self.photos,
                )
            )
        self._close()
        self.on_change()

    def _cancel(self, _) -> None:
        for name in self.added_photos:
            storage.delete_photo(name)
        self._close()

    def _confirm_delete(self, _) -> None:
        confirm = ft.AlertDialog(
            modal=True,
            title=ft.Text("Delete memory?"),
            content=ft.Text(f'"{self.memory.title}" and its photos will be removed.'),
            actions=[
                ft.TextButton("Keep it", on_click=lambda _: self.page.pop_dialog()),
                ft.FilledButton(
                    "Delete",
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.ERROR, color=ft.Colors.ON_ERROR
                    ),
                    on_click=lambda _: self._delete(),
                ),
            ],
        )
        self.page.show_dialog(confirm)

    def _delete(self) -> None:
        self.page.pop_dialog()  # close the confirm dialog
        self.state.remove(self.memory)
        self._close()
        self.on_change()

    def _close(self) -> None:
        self.page.pop_dialog()
        if self.picker in self.page.services:
            self.page.services.remove(self.picker)
        self.page.update()


class CategoryManager:
    """Dialog to add/remove categories with a color swatch palette."""

    def __init__(self, page: ft.Page, state: AppState, on_change: Callable[[], None]):
        self.page = page
        self.state = state
        self.on_change = on_change
        self.selected_color = SWATCHES[0]
        self.name_field = ft.TextField(label="New category", expand=True)
        self.swatch_row = ft.Row(wrap=True, spacing=6)
        self.list_col = ft.Column(spacing=6, tight=True)
        self._rebuild()

        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Categories"),
            content=ft.Container(
                width=440,
                content=ft.Column(
                    [
                        self.list_col,
                        ft.Divider(),
                        self.name_field,
                        self.swatch_row,
                        ft.FilledTonalButton(
                            "Add category", icon=ft.Icons.ADD, on_click=self._add
                        ),
                    ],
                    tight=True,
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[ft.TextButton("Done", on_click=self._close)],
        )

    def open(self) -> None:
        self.page.show_dialog(self.dialog)

    def _rebuild(self) -> None:
        rows = []
        for name, color in sorted(self.state.categories.items()):
            rows.append(
                ft.Row(
                    [
                        ft.Container(
                            width=18, height=18, bgcolor=color, border_radius=9
                        ),
                        ft.Text(name, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_size=18,
                            tooltip="Delete category",
                            on_click=lambda _, n=name: self._delete(n),
                        ),
                    ]
                )
            )
        self.list_col.controls = rows or [ft.Text("No categories yet", italic=True)]

        self.swatch_row.controls = [
            ft.Container(
                width=30,
                height=30,
                bgcolor=c,
                border_radius=15,
                border=ft.Border.all(3, ft.Colors.ON_SURFACE)
                if c == self.selected_color
                else None,
                on_click=lambda _, c=c: self._pick_color(c),
            )
            for c in SWATCHES
        ]

    def _pick_color(self, color: str) -> None:
        self.selected_color = color
        self._rebuild()
        self.dialog.update()

    def _add(self, _) -> None:
        name = self.name_field.value.strip()
        if not name:
            return
        self.state.set_category(name, self.selected_color)
        self.name_field.value = ""
        self._rebuild()
        self.dialog.update()

    def _delete(self, name: str) -> None:
        self.state.remove_category(name)
        self._rebuild()
        self.dialog.update()

    def _close(self, _) -> None:
        self.page.pop_dialog()
        self.on_change()
