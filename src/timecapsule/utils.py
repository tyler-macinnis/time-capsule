"""Date helpers: time since, anniversaries, milestones."""

from __future__ import annotations

from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from .models import Memory


def time_since(day: date, today: date | None = None) -> str:
    today = today or date.today()
    if day > today:
        delta = relativedelta(day, today)
        suffix = " from now"
    else:
        delta = relativedelta(today, day)
        suffix = " ago" if (delta.years or delta.months or delta.days) else ""
    parts = []
    if delta.years:
        parts.append(f"{delta.years} year{'s' if delta.years > 1 else ''}")
    if delta.months:
        parts.append(f"{delta.months} month{'s' if delta.months > 1 else ''}")
    if delta.days:
        parts.append(f"{delta.days} day{'s' if delta.days > 1 else ''}")
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


MILESTONE_DAYS = [100, 365, 500, 1000, 2000, 3650, 5000, 7300, 10000]


def milestones(start: date, today: date | None = None) -> tuple[list[str], str | None]:
    """(reached milestone labels, next milestone label with countdown)."""
    today = today or date.today()
    days = (today - start).days
    reached = [f"{d:,} days together" for d in MILESTONE_DAYS if days >= d]
    nxt = None
    for d in MILESTONE_DAYS:
        if days < d:
            nxt = f"{d:,} days on {(start + timedelta(days=d)).strftime('%B %d, %Y')} — {d - days:,} to go"
            break
    return reached, nxt
