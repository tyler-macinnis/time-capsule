"""Application state: in-memory cache backed by the SQLite database."""

from __future__ import annotations

from . import storage
from .models import Memory
from .storage import Database


class AppState:
    def __init__(self, db: Database | None = None) -> None:
        self.db = db or Database()
        self.memories = self.db.list_memories()
        self.categories = self.db.categories()
        self.settings = self.db.get_settings()
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
            if q in m.title.lower() or q in m.notes.lower() or q in m.category.lower()
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

    def add(self, memory: Memory) -> None:
        self.memories.append(memory)
        self.db.upsert_memory(memory)

    def update(self, memory: Memory) -> None:
        self.db.upsert_memory(memory)

    def remove(self, memory: Memory) -> None:
        for photo in memory.photos:
            storage.delete_photo(photo)
        self.memories = [m for m in self.memories if m.id != memory.id]
        self.db.delete_memory(memory.id)

    def set_category(self, name: str, color: str) -> None:
        self.categories[name] = color
        self.db.set_category(name, color)

    def remove_category(self, name: str) -> None:
        self.categories.pop(name, None)
        for m in self.memories:
            if m.category == name:
                m.category = ""
        self.db.delete_category(name)

    # ------------------------------------------------------------ settings

    def set_setting(self, key: str, value: str) -> None:
        self.settings[key] = value
        self.db.set_setting(key, value)
