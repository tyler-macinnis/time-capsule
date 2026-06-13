"""Tests for date helpers: time since, anniversaries, on-this-day."""

from __future__ import annotations

from datetime import date

import pytest

from timecapsule.models import Memory
from timecapsule.utils import (
    next_occurrence,
    on_this_day,
    time_since,
    upcoming_anniversaries,
    years_ago_text,
)

TODAY = date(2026, 6, 12)


# -------------------------------------------------------------- time_since


@pytest.mark.parametrize(
    ("day", "expected"),
    [
        (date(2026, 6, 12), "Today"),
        (date(2026, 6, 11), "1 day ago"),
        (date(2026, 6, 5), "7 days ago"),
        (date(2026, 5, 12), "1 month ago"),
        (date(2025, 6, 12), "1 year ago"),
        (date(2023, 4, 10), "3 years, 2 months, 2 days ago"),
        (date(2026, 6, 13), "1 day from now"),
        (date(2027, 8, 14), "1 year, 2 months, 2 days from now"),
    ],
)
def test_time_since(day, expected):
    assert time_since(day, TODAY) == expected


def test_time_since_month_boundary():
    # Jan 31 -> Mar 1: 1 month (Feb) + 1 day
    assert time_since(date(2026, 1, 31), date(2026, 3, 1)) == "1 month, 1 day ago"


def test_time_since_defaults_to_today():
    assert time_since(date.today()) == "Today"


# ---------------------------------------------------------- years_ago_text


def test_years_ago_text():
    assert years_ago_text(date(2024, 6, 12), TODAY) == "2 years ago today"
    assert years_ago_text(date(2025, 6, 12), TODAY) == "1 year ago today"
    assert years_ago_text(date(2026, 1, 1), TODAY) == "Today"


# ------------------------------------------------------------- on_this_day


def _mem(title: str, day: date) -> Memory:
    return Memory.new(title, day)


def test_on_this_day_matches_month_and_day_from_past_years():
    memories = [
        _mem("match", date(2024, 6, 12)),
        _mem("other day", date(2024, 6, 11)),
        _mem("this year", date(2026, 6, 12)),  # same year -> excluded
        _mem("older match", date(2020, 6, 12)),
    ]
    titles = [m.title for m in on_this_day(memories, TODAY)]
    assert titles == ["older match", "match"]  # sorted oldest first


def test_on_this_day_feb29_maps_to_mar1_in_non_leap_years():
    memories = [_mem("leap", date(2024, 2, 29))]
    assert on_this_day(memories, date(2026, 3, 1)) == memories
    assert on_this_day(memories, date(2026, 2, 28)) == []
    # In a leap year, Mar 1 does NOT pick up Feb 29
    assert on_this_day(memories, date(2028, 3, 1)) == []
    assert on_this_day(memories, date(2028, 2, 29)) == memories


def test_on_this_day_empty():
    assert on_this_day([], TODAY) == []


# --------------------------------------------------------- next_occurrence


def test_next_occurrence_later_this_year():
    assert next_occurrence(date(2020, 12, 25), TODAY) == date(2026, 12, 25)


def test_next_occurrence_already_passed_rolls_to_next_year():
    assert next_occurrence(date(2020, 1, 5), TODAY) == date(2027, 1, 5)


def test_next_occurrence_today_counts():
    assert next_occurrence(date(2020, 6, 12), TODAY) == TODAY


def test_next_occurrence_feb29_in_non_leap_year():
    assert next_occurrence(date(2024, 2, 29), date(2026, 1, 1)) == date(2026, 3, 1)
    assert next_occurrence(date(2024, 2, 29), date(2027, 6, 1)) == date(2028, 2, 29)


# ------------------------------------------------- upcoming_anniversaries


def test_upcoming_anniversaries_sorted_and_limited():
    memories = [
        _mem("in 3 days", date(2024, 6, 15)),
        _mem("in 1 day", date(2024, 6, 13)),
        _mem("in 200 days", date(2024, 12, 29)),
        _mem("future memory", date(2027, 1, 1)),  # not in the past -> excluded
    ]
    rows = upcoming_anniversaries(memories, TODAY, limit=2)
    assert [(m.title, days) for m, _, days in rows] == [
        ("in 1 day", 1),
        ("in 3 days", 3),
    ]


def test_upcoming_anniversaries_today_is_zero_days():
    rows = upcoming_anniversaries([_mem("anniv", date(2020, 6, 12))], TODAY)
    assert rows[0][1] == TODAY
    assert rows[0][2] == 0


def test_upcoming_anniversaries_empty():
    assert upcoming_anniversaries([], TODAY) == []
