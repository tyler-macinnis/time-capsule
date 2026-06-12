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
