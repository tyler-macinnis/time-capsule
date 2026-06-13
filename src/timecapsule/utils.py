"""Date helpers: time since and anniversaries."""

from __future__ import annotations

from datetime import date, timedelta

from .models import Memory


def _ymd_between(start: date, end: date) -> tuple[int, int, int]:
    """Calendar years, months, and days from start to end (start <= end)."""
    years = end.year - start.year
    months = end.month - start.month
    days = end.day - start.day
    if days < 0:
        months -= 1
        last_of_prev_month = end.replace(day=1) - timedelta(days=1)
        days += last_of_prev_month.day
    if months < 0:
        years -= 1
        months += 12
    return years, months, days


def time_since(day: date, today: date | None = None) -> str:
    today = today or date.today()
    if day > today:
        years, months, days = _ymd_between(today, day)
        suffix = " from now"
    else:
        years, months, days = _ymd_between(day, today)
        suffix = " ago" if (years or months or days) else ""
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years > 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months > 1 else ''}")
    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    return (", ".join(parts) or "Today") + (suffix if parts else "")


def years_ago_text(day: date, today: date | None = None) -> str:
    today = today or date.today()
    years = today.year - day.year
    if years <= 0:
        return "Today"
    return f"{years} year{'s' if years > 1 else ''} ago today"


def on_this_day(memories: list[Memory], today: date | None = None) -> list[Memory]:
    """Memories from past years whose month/day match today (Feb 29 -> Mar 1)."""
    today = today or date.today()
    matches = []
    for m in memories:
        if m.day.year >= today.year:
            continue
        md = (m.day.month, m.day.day)
        if md == (today.month, today.day):
            matches.append(m)
        elif md == (2, 29) and (today.month, today.day) == (3, 1) and not _is_leap(today.year):
            matches.append(m)
    matches.sort(key=lambda m: m.day)
    return matches


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def next_occurrence(day: date, today: date | None = None) -> date:
    """Next anniversary of `day` (today counts if it matches)."""
    today = today or date.today()
    for year in (today.year, today.year + 1):
        try:
            candidate = day.replace(year=year)
        except ValueError:  # Feb 29 in a non-leap year
            candidate = date(year, 3, 1)
        if candidate >= today:
            return candidate
    return day.replace(year=today.year + 1)


def upcoming_anniversaries(
    memories: list[Memory], today: date | None = None, limit: int = 5
) -> list[tuple[Memory, date, int]]:
    """(memory, next date, days until) sorted soonest-first, past dates only."""
    today = today or date.today()
    rows = []
    for m in memories:
        if m.day >= today:
            continue
        nxt = next_occurrence(m.day, today)
        rows.append((m, nxt, (nxt - today).days))
    rows.sort(key=lambda r: r[2])
    return rows[:limit]
