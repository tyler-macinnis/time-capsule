"""Application state: in-memory store with persistence."""

from __future__ import annotations

from datetime import date

from . import storage
from .models import Memory


class AppState:
    def __init__(self) -> None:
        self.memories, self.categories = storage.load_store()
        self.settings = storage.load_settings()
        self.search = ""

    # ------------------------------------------------------------- queries

    def filtered_memories(self) -> list[Memory]:
        items = sorted(self.memories, key=lambda m: m.day, reverse=True)
        q = self.search.strip().lower()
        if not q:
            return items
        return [
            m
            for m in items
            if q in m.title.lower()
            or q in m.notes.lower()
            or q in m.category.lower()
        ]

    def get(self, memory_id: str) -> Memory | None:
        return next((m for m in self.memories if m.id == memory_id), None)

    def all_photos(self) -> list[tuple[str, Memory]]:
        """(photo file name, owning memory) newest memories first."""
        out = []
        for m in sorted(self.memories, key=lambda m: m.day, reverse=True):
            for p in m.photos:
                out.append((p, m))
        return out

    # ----------------------------------------------------------- mutations

    def save(self) -> None:
        storage.save_store(self.memories, self.categories)

    def add(self, memory: Memory) -> None:
        self.memories.append(memory)
        self.save()

    def remove(self, memory: Memory) -> None:
        for photo in memory.photos:
            storage.delete_photo(photo)
        self.memories = [m for m in self.memories if m.id != memory.id]
        self.save()

    def set_category(self, name: str, color: str) -> None:
        self.categories[name] = color
        self.save()

    def remove_category(self, name: str) -> None:
        self.categories.pop(name, None)
        for m in self.memories:
            if m.category == name:
                m.category = ""
        self.save()

    # ------------------------------------------------------------ settings

    def save_settings(self) -> None:
        storage.save_settings(self.settings)

    @property
    def anchor_date(self) -> date | None:
        raw = self.settings.get("relationship_start")
        if not raw:
            return None
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None

    @anchor_date.setter
    def anchor_date(self, value: date) -> None:
        self.settings["relationship_start"] = value.isoformat()
        self.save_settings()
