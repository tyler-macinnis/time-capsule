"""Headless construction tests for every Flet view.

These build the control trees without a real ``ft.Page`` and assert their
structure, which catches layout/API regressions (e.g. the STRETCH-inside-
ListView bug that blanked the timeline) before the app is ever launched.
"""

from __future__ import annotations

from datetime import date, timedelta

import flet as ft
import pytest

from timecapsule import storage
from timecapsule.views.gallery import build_gallery
from timecapsule.views.on_this_day import build_banner
from timecapsule.views.stats import build_stats
from timecapsule.views.timeline import build_timeline, memory_card

# ------------------------------------------------------------------ helpers

_CHILD_ATTRS = ("content", "controls", "title", "leading", "actions")


def walk(control):
    """Yield a control and all of its descendants."""
    yield control
    for attr in _CHILD_ATTRS:
        child = getattr(control, attr, None)
        if isinstance(child, (list, tuple)):
            for c in child:
                if isinstance(c, ft.BaseControl):
                    yield from walk(c)
        elif isinstance(child, ft.BaseControl):
            yield from walk(child)


def texts(control) -> list[str]:
    return [str(c.value) for c in walk(control) if isinstance(c, ft.Text)]


def _noop(_memory):
    pass


@pytest.fixture
def populated_state(state, make_memory):
    state.add(
        make_memory(
            title="Hike",
            day=date(2026, 3, 10),
            notes="Mountain trail",
            category="Adventures",
        )
    )
    state.add(make_memory(title="Dinner", day=date(2026, 3, 2)))
    state.add(make_memory(title="Concert", day=date(2025, 11, 20)))
    state.add(make_memory(title="First date", day=date(2022, 2, 14), category="Us"))
    return state


# ----------------------------------------------------------------- timeline


def test_timeline_renders_a_card_per_memory(populated_state):
    tl = build_timeline(populated_state, _noop, _noop)
    assert isinstance(tl, ft.ListView)
    all_text = texts(tl)
    for title in ("Hike", "Dinner", "Concert", "First date"):
        assert title in all_text


def test_timeline_year_and_month_headers(populated_state):
    tl = build_timeline(populated_state, _noop, _noop)
    all_text = texts(tl)
    assert "2026" in all_text
    assert "2025" in all_text
    assert "2022" in all_text
    # Month labels are uppercased; March appears once even with two entries
    assert all_text.count("MARCH") == 1
    assert "NOVEMBER" in all_text
    assert "FEBRUARY" in all_text


def test_timeline_no_stretch_rows_regression(populated_state):
    """STRETCH rows inside ListView items have unbounded height and blank
    the whole list -- the original 'only years show' bug."""
    tl = build_timeline(populated_state, _noop, _noop)
    for c in walk(tl):
        if isinstance(c, ft.Row):
            assert c.vertical_alignment != ft.CrossAxisAlignment.STRETCH


def test_timeline_empty_state(state):
    tl = build_timeline(state, _noop, _noop)
    assert any("No memories yet" in t for t in texts(tl))


def test_timeline_search_count_and_no_match_states(populated_state):
    populated_state.search = "hike"
    tl = build_timeline(populated_state, _noop, _noop)
    all_text = texts(tl)
    assert any("1 memory match" in t for t in all_text)
    assert "Dinner" not in all_text

    populated_state.search = "zzz"
    tl = build_timeline(populated_state, _noop, _noop)
    assert any("No memories match" in t for t in texts(tl))


def test_timeline_header_is_prepended(populated_state):
    header = ft.Text("BANNER")
    tl = build_timeline(populated_state, _noop, _noop, header=header)
    assert texts(tl)[0] == "BANNER"


def test_timeline_card_click_and_buttons_wired(populated_state):
    opened, deleted = [], []
    tl = build_timeline(populated_state, opened.append, deleted.append)
    buttons = [c for c in walk(tl) if isinstance(c, ft.IconButton)]
    # one edit + one delete button per memory
    assert len(buttons) == 2 * len(populated_state.memories)
    edit, delete = buttons[0], buttons[1]
    edit.on_click(None)
    delete.on_click(None)
    assert opened == [populated_state.filtered_memories()[0]]
    assert deleted == [populated_state.filtered_memories()[0]]


def test_memory_card_shows_photo_strip_and_overflow(state, make_memory, sample_png):
    names = [storage.import_photo(sample_png) for _ in range(5)]
    m = make_memory(title="Trip", photos=names)
    state.add(m)
    card = memory_card(m, state, _noop, _noop)
    images = [c for c in walk(card) if isinstance(c, ft.Image)]
    assert len(images) == 4  # capped at 4 thumbnails
    assert "+1" in texts(card)  # overflow badge


def test_memory_card_skips_missing_thumbnails(state, make_memory):
    m = make_memory(title="Ghost", photos=["missing.jpg"])
    state.add(m)
    card = memory_card(m, state, _noop, _noop)
    assert [c for c in walk(card) if isinstance(c, ft.Image)] == []


def test_memory_card_category_chip_uses_category_color(state, make_memory):
    m = make_memory(title="Tagged", category="Us")
    state.add(m)
    card = memory_card(m, state, _noop, _noop)
    chips = [
        c
        for c in walk(card)
        if isinstance(c, ft.Container) and c.bgcolor == state.categories["Us"]
    ]
    assert chips, "expected a chip tinted with the category color"
    assert "Us" in texts(card)


# ------------------------------------------------------------------ gallery


def test_gallery_empty_state(state):
    g = build_gallery(None, state, _noop)
    assert any("No photos yet" in t for t in texts(g))


def test_gallery_grid_has_tile_per_photo(state, make_memory, sample_png):
    names = [storage.import_photo(sample_png) for _ in range(3)]
    state.add(make_memory(title="Album", photos=names))
    g = build_gallery(None, state, _noop)
    assert isinstance(g, ft.GridView)
    assert len(g.controls) == 3


def test_gallery_skips_photos_without_thumbnails(state, make_memory, sample_png):
    name = storage.import_photo(sample_png)
    state.add(make_memory(title="Mixed", photos=[name, "missing.jpg"]))
    g = build_gallery(None, state, _noop)
    assert len(g.controls) == 1


# -------------------------------------------------------------------- stats


def test_stats_empty_state_builds(state):
    s = build_stats(state)
    all_text = texts(s)
    assert "Memories" in all_text
    assert "0" in all_text


def test_stats_counts_and_sections(populated_state):
    s = build_stats(populated_state)
    all_text = texts(s)
    assert "4" in all_text  # memory count
    assert "Memories by category" in all_text
    assert "Adventures" in all_text
    assert "Upcoming anniversaries" in all_text


# ------------------------------------------------------------------- banner


def test_banner_none_when_no_matches(state, make_memory):
    state.add(make_memory(day=date.today() - timedelta(days=1)))
    assert build_banner(state, _noop) is None


def test_banner_lists_on_this_day_matches(state, make_memory):
    today = date.today()
    anniversary = today.replace(year=today.year - 2)
    state.add(make_memory(title="Two years ago", day=anniversary))
    banner = build_banner(state, _noop)
    assert banner is not None
    all_text = texts(banner)
    assert "On this day" in all_text
    assert "Two years ago" in all_text
