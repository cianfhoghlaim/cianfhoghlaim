"""oideachais.cianfhoghlaim.dlt.official_media.instagram_export — DLT source over the JSON bundle Instagram ships.

Reference: Meta's "Download Your Information" export. As of 2026-05
the relevant subdirectory is ``connections/followers_and_following/``
and contains 7 JSON files (``followers_1.json`` is paginated;
``following.json`` is the single full list). Each file is a list
(or object containing a list) of objects with the shape::

    {
        "title": "<username>",
        "media_list_data": [],
        "string_list_data": [
            {
                "href": "https://www.instagram.com/<username>",
                "value": "<username>",
                "timestamp": <unix epoch seconds>
            }
        ]
    }

``followers_1.json`` and ``removed_suggestions.json`` are flat
arrays. ``following.json`` wraps the array in
``{"relationships_following": [...]}``. The other 5 files
(``close_friends``, ``blocked_profiles``, ``pending_follow_requests``,
``restricted_profiles``) wrap the array in
``{"relationships_<kind>": [...]}``.

The DLT resource ``profiles`` yields one row per profile (regardless
of which list it was on), with columns:

    ig_username    str
    ig_href        str
    list_kind      "following" | "follower" | "close_friend" | ...
    followed_at    datetime | None
    ig_export_id   str   # the export directory name
"""
from __future__ import annotations

import json
import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# The 7 files inside connections/followers_and_following/ that
# Instagram ships in the standard export.
FOLLOWER_LIST_KINDS: dict[str, str] = {
    "followers_1.json": "follower",
    "following.json": "following",
    "close_friends.json": "close_friend",
    "blocked_profiles.json": "blocked",
    "pending_follow_requests.json": "pending_follow_request",
    "removed_suggestions.json": "removed_suggestion",
    "restricted_profiles.json": "restricted",
}

# The wrapper key inside each JSON object (None for flat arrays).
_WRAPPER_KEY: dict[str, str | None] = {
    "followers_1.json": None,
    "following.json": "relationships_following",
    "close_friends.json": "relationships_close_friends",
    "blocked_profiles.json": "relationships_blocked_users",
    "pending_follow_requests.json": "relationships_follow_requests_sent",
    "removed_suggestions.json": "relationships_removed_suggestions",
    "restricted_profiles.json": "relationships_restricted_users",
}


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


@dataclass
class ParsedProfile:
    """One row of the ``profiles`` resource."""

    ig_username: str
    ig_href: str
    list_kind: str
    followed_at: datetime | None
    ig_export_id: str

    def to_dlt_row(self) -> dict[str, Any]:
        return {
            "ig_username": self.ig_username,
            "ig_href": self.ig_href,
            "list_kind": self.list_kind,
            "followed_at": self.followed_at,
            "ig_export_id": self.ig_export_id,
        }


class InstagramExportParser:
    """Parse the standard Instagram export directory layout.

    The parser is deterministic and offline — no network calls. It is
    reusable in tests with ``InstagramExportParser(export_dir)`` against
    a synthetic fixture.
    """

    def __init__(self, export_dir: str | Path) -> None:
        self.export_dir = Path(export_dir)
        if not self.export_dir.exists():
            raise FileNotFoundError(
                f"Instagram export directory not found: {self.export_dir}"
            )
        self.export_id = self.export_dir.name

    def _read_file(self, filename: str) -> list[dict[str, Any]]:
        """Read a single followers/following JSON file. Returns a flat
        list of relationship entries."""
        path = self.export_dir / "connections" / "followers_and_following" / filename
        if not path.exists():
            logger.warning(
                "instagram_export_missing",
                file=str(path),
                export_id=self.export_id,
            )
            return []
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        wrapper = _WRAPPER_KEY[filename]
        if wrapper is None:
            if not isinstance(data, list):
                logger.warning(
                    "instagram_export_unexpected_shape",
                    file=filename,
                    type=type(data).__name__,
                )
                return []
            return data
        if not isinstance(data, dict):
            logger.warning(
                "instagram_export_unexpected_shape",
                file=filename,
                type=type(data).__name__,
            )
            return []
        entries = data.get(wrapper, [])
        if not isinstance(entries, list):
            logger.warning(
                "instagram_export_unexpected_shape",
                file=filename,
                wrapper=wrapper,
                type=type(entries).__name__,
            )
            return []
        return entries

    @staticmethod
    def _entry_to_profile(
        entry: dict[str, Any],
        list_kind: str,
        export_id: str,
    ) -> ParsedProfile | None:
        """Convert one relationship entry into a ``ParsedProfile``.

        Returns ``None`` if the entry has no ``string_list_data`` or no
        usable username."""
        string_data = entry.get("string_list_data") or []
        if not string_data:
            return None
        first = string_data[0]
        if not isinstance(first, dict):
            return None
        username = first.get("value") or entry.get("title")
        if not isinstance(username, str) or not username:
            return None
        href = first.get("href") or f"https://www.instagram.com/{username}"
        timestamp = first.get("timestamp")
        followed_at: datetime | None = None
        if isinstance(timestamp, (int, float)):
            try:
                followed_at = datetime.fromtimestamp(int(timestamp), tz=UTC)
            except (OverflowError, OSError, ValueError):
                followed_at = None
        return ParsedProfile(
            ig_username=username,
            ig_href=href,
            list_kind=list_kind,
            followed_at=followed_at,
            ig_export_id=export_id,
        )

    def parse(self) -> Iterator[ParsedProfile]:
        """Yield one ``ParsedProfile`` per (profile × list_kind) entry."""
        seen: set[tuple[str, str]] = set()
        for filename, list_kind in FOLLOWER_LIST_KINDS.items():
            entries = self._read_file(filename)
            for entry in entries:
                profile = self._entry_to_profile(entry, list_kind, self.export_id)
                if profile is None:
                    continue
                key = (profile.ig_username, profile.list_kind)
                if key in seen:
                    continue
                seen.add(key)
                yield profile

    def parse_all(self) -> list[ParsedProfile]:
        """Materialise the full parse as a list. Useful for tests."""
        return list(self.parse())


# ---------------------------------------------------------------------------
# DLT source
# ---------------------------------------------------------------------------


def _resolve_export_dir() -> Path:
    """Resolve the export directory from the standard env var.

    ``OIDEACHAIS_IG_EXPORT_DIR`` is the canonical name; the older
    ``INSTAGRAM_EXPORT_DIR`` is honoured for backward compatibility.
    """
    path = os.environ.get("OIDEACHAIS_IG_EXPORT_DIR") or os.environ.get(
        "INSTAGRAM_EXPORT_DIR"
    )
    if not path:
        raise FileNotFoundError(
            "Set OIDEACHAIS_IG_EXPORT_DIR to the path of your Instagram "
            "export directory (e.g. the unzipped folder that contains "
            "connections/, media/, ads_information/, ...)."
        )
    return Path(path)


@dlt.source(name="instagram_export")
def instagram_export_source(export_dir: str | Path | None = None):
    """DLT source over the standard Instagram export bundle.

    Args:
        export_dir: Path to the unzipped Instagram export directory.
            Defaults to the ``OIDEACHAIS_IG_EXPORT_DIR`` env var.

    Returns:
        A DLT source with one resource, ``profiles``.
    """
    resolved = Path(export_dir) if export_dir is not None else _resolve_export_dir()
    parser = InstagramExportParser(resolved)

    @dlt.resource(
        name="profiles",
        write_disposition="merge",
        primary_key=["ig_export_id", "ig_username", "list_kind"],
    )
    def profiles() -> Iterator[dict[str, Any]]:
        """One row per (profile × list_kind) combination."""
        for profile in parser.parse():
            yield profile.to_dlt_row()

    return profiles
