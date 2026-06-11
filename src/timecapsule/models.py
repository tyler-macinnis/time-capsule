"""Data models for Time Capsule."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Memory:
    id: str
    title: str
    day: date
    notes: str = ""
    category: str = ""
    photos: list[str] = field(default_factory=list)  # file names under photos/
    created_at: str = ""

    @staticmethod
    def new(
        title: str,
        day: date,
        notes: str = "",
        category: str = "",
        photos: list[str] | None = None,
    ) -> "Memory":
        return Memory(
            id=uuid.uuid4().hex,
            title=title,
            day=day,
            notes=notes,
            category=category,
            photos=list(photos or []),
            created_at=datetime.now().isoformat(timespec="seconds"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "date": self.day.isoformat(),
            "notes": self.notes,
            "category": self.category,
            "photos": self.photos,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Memory":
        return Memory(
            id=data.get("id") or uuid.uuid4().hex,
            title=data.get("title", ""),
            day=date.fromisoformat(data["date"]),
            notes=data.get("notes", ""),
            category=data.get("category", ""),
            photos=list(data.get("photos", [])),
            created_at=data.get("created_at", ""),
        )
