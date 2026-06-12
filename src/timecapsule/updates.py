"""Update check against GitHub Releases (no auto-download, prompt only)."""

from __future__ import annotations

import json
import re
import urllib.request

from . import VERSION

OWNER_REPO = "tyler-macinnis/time-capsule"
RELEASES_API = f"https://api.github.com/repos/{OWNER_REPO}/releases/latest"
RELEASES_PAGE = f"https://github.com/{OWNER_REPO}/releases/latest"

_VERSION_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def parse_version(raw: str) -> tuple[int, int, int] | None:
    """'v3.0.0' or '3.0.0' -> (3, 0, 0); None if not a plain semver."""
    match = _VERSION_RE.match((raw or "").strip())
    if not match:
        return None
    return tuple(int(g) for g in match.groups())  # type: ignore[return-value]


def is_newer(latest: str, current: str = VERSION) -> bool:
    latest_v = parse_version(latest)
    current_v = parse_version(current)
    if latest_v is None or current_v is None:
        return False
    return latest_v > current_v


def fetch_latest_version(timeout: float = 5.0) -> str | None:
    """Latest release tag (e.g. 'v3.0.0'), or None if the check fails."""
    request = urllib.request.Request(
        RELEASES_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"time-capsule/{VERSION}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except (OSError, ValueError):
        return None
    tag = data.get("tag_name", "")
    return tag if parse_version(tag) else None
