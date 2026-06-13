"""Tests for update-check version parsing and comparison."""

from __future__ import annotations

import pytest

from timecapsule.updates import is_newer, parse_version


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("v3.0.0", (3, 0, 0)),
        ("3.0.0", (3, 0, 0)),
        ("  v1.22.333  ", (1, 22, 333)),
        ("not-a-version", None),
        ("v3.0", None),
        ("3.0.0.1", None),
        ("v3.0.0-beta", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_version(raw, expected):
    assert parse_version(raw) == expected


@pytest.mark.parametrize(
    ("latest", "current", "expected"),
    [
        ("v3.2.0", "3.1.0", True),
        ("v3.1.1", "3.1.0", True),
        ("v4.0.0", "3.9.9", True),
        ("v3.1.0", "3.1.0", False),
        ("v3.0.9", "3.1.0", False),
        ("v2.9.9", "3.0.0", False),
        ("garbage", "3.1.0", False),
        ("v3.2.0", "garbage", False),
    ],
)
def test_is_newer(latest, current, expected):
    assert is_newer(latest, current) is expected


def test_is_newer_defaults_to_app_version():
    from timecapsule import VERSION

    assert is_newer(f"v{VERSION}") is False
