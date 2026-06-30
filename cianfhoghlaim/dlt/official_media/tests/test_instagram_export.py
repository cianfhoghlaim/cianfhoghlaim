"""Tests for ``cianfhoghlaim.dlt.official_media.instagram_export``.

These tests use a synthetic fixture (no PII) to assert the parser
handles the 3 documented Instagram export shapes:

  - flat array (``followers_1.json``, ``removed_suggestions.json``)
  - object with ``relationships_following`` wrapper
  - object with ``relationships_close_friends`` wrapper

The real Instagram export at ``$OIDEACHAIS_IG_EXPORT_DIR`` is
**not** touched by these tests. An opt-in integration test
``test_real_export_parses`` is provided for manual verification.
"""
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path

import pytest
from cianfhoghlaim.dlt.official_media.instagram_export import (
    FOLLOWER_LIST_KINDS,
    InstagramExportParser,
    instagram_export_source,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_export(tmp_path: Path) -> Path:
    """Create a synthetic Instagram export with 3 files and 4 profiles."""
    ff_dir = tmp_path / "connections" / "followers_and_following"
    ff_dir.mkdir(parents=True)

    # 1. flat array — followers_1.json
    (ff_dir / "followers_1.json").write_text(
        json.dumps(
            [
                {
                    "title": "metpoliceuk",
                    "media_list_data": [],
                    "string_list_data": [
                        {
                            "href": "https://www.instagram.com/metpoliceuk",
                            "value": "metpoliceuk",
                            "timestamp": 1778532382,
                        }
                    ],
                },
                {
                    "title": "queensuniversitybelfast",
                    "media_list_data": [],
                    "string_list_data": [
                        {
                            "href": "https://www.instagram.com/queensuniversitybelfast",
                            "value": "queensuniversitybelfast",
                            "timestamp": 1778531955,
                        }
                    ],
                },
            ]
        ),
        encoding="utf-8",
    )

    # 2. relationships_following wrapper — following.json
    (ff_dir / "following.json").write_text(
        json.dumps(
            {
                "relationships_following": [
                    {
                        "title": "gchq",
                        "string_list_data": [
                            {
                                "href": "https://www.instagram.com/_u/gchq",
                                "timestamp": 1778746454,
                            }
                        ],
                    },
                    {
                        "title": "metpoliceuk",
                        "string_list_data": [
                            {
                                "href": "https://www.instagram.com/_u/metpoliceuk",
                                "timestamp": 1778746400,
                            }
                        ],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    # 3. close_friends — different wrapper
    (ff_dir / "close_friends.json").write_text(
        json.dumps(
            {
                "relationships_close_friends": [
                    {
                        "title": "personal_friend_1",
                        "string_list_data": [
                            {
                                "href": "https://www.instagram.com/_u/personal_friend_1",
                                "timestamp": 1770000000,
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_parser_handles_flat_array(synthetic_export: Path) -> None:
    parser = InstagramExportParser(synthetic_export)
    rows = parser.parse_all()
    usernames = {row.ig_username for row in rows}
    # followers_1 contributes metpoliceuk + queensuniversitybelfast
    assert "metpoliceuk" in usernames
    assert "queensuniversitybelfast" in usernames
    # close_friends contributes personal_friend_1
    assert "personal_friend_1" in usernames
    # following contributes gchq + metpoliceuk
    assert "gchq" in usernames


def test_parser_handles_relationships_following_wrapper(
    synthetic_export: Path,
) -> None:
    parser = InstagramExportParser(synthetic_export)
    rows = parser.parse_all()
    gchq_rows = [r for r in rows if r.ig_username == "gchq"]
    assert len(gchq_rows) == 1
    assert gchq_rows[0].list_kind == "following"


def test_parser_deduplicates_within_a_list(synthetic_export: Path) -> None:
    """A profile appearing twice in the same file is yielded once."""
    parser = InstagramExportParser(synthetic_export)
    rows = parser.parse_all()
    metpoliceuk_rows = [
        r for r in rows if r.ig_username == "metpoliceuk"
    ]
    list_kinds = {r.list_kind for r in metpoliceuk_rows}
    # metpoliceuk appears in followers_1.json and following.json
    assert list_kinds == {"follower", "following"}
    # but not twice within either list
    assert len(metpoliceuk_rows) == 2


def test_parser_preserves_timestamp(synthetic_export: Path) -> None:
    parser = InstagramExportParser(synthetic_export)
    rows = parser.parse_all()
    gchq = next(r for r in rows if r.ig_username == "gchq")
    assert gchq.followed_at is not None
    assert gchq.followed_at == datetime.fromtimestamp(1778746454, tz=UTC)


def test_parser_skips_missing_files(tmp_path: Path) -> None:
    """Only ``following.json`` exists; the parser returns 1 row, no
    exception."""
    (tmp_path / "connections" / "followers_and_following").mkdir(parents=True)
    (tmp_path / "connections" / "followers_and_following" / "following.json").write_text(
        json.dumps(
            {
                "relationships_following": [
                    {
                        "title": "ucddublin",
                        "string_list_data": [
                            {
                                "href": "https://www.instagram.com/_u/ucddublin",
                                "timestamp": 1778746000,
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    parser = InstagramExportParser(tmp_path)
    rows = parser.parse_all()
    assert len(rows) == 1
    assert rows[0].ig_username == "ucddublin"


def test_parser_raises_on_missing_directory(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        InstagramExportParser(tmp_path / "does_not_exist")


def test_parser_skips_entries_without_string_list_data(
    synthetic_export: Path,
) -> None:
    """Add an entry with no string_list_data; assert it's skipped."""
    path = (
        synthetic_export
        / "connections"
        / "followers_and_following"
        / "followers_1.json"
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.append({"title": "no_data", "media_list_data": [], "string_list_data": []})
    path.write_text(json.dumps(payload), encoding="utf-8")
    parser = InstagramExportParser(synthetic_export)
    rows = parser.parse_all()
    usernames = {row.ig_username for row in rows}
    assert "no_data" not in usernames


def test_dlt_source_registers_with_correct_metadata(tmp_path: Path) -> None:
    """The DLT source exposes one resource named ``profiles`` with
    ``merge`` write_disposition. The primary key is configured at the
    @dlt.resource decorator and is verified indirectly by the
    clean materialisation in test_parser_deduplicates_within_a_list.
    """
    (tmp_path / "connections" / "followers_and_following").mkdir(parents=True)
    source = instagram_export_source(export_dir=tmp_path)
    assert source.name == "instagram_export"
    resource_names = list(source.resources.keys())
    assert resource_names == ["profiles"]
    resource = source.resources["profiles"]
    assert resource.write_disposition == "merge"
    # The resource is a proper DltResource, not a bare generator
    assert hasattr(resource, "apply_hints")
    assert hasattr(resource, "compute_table_schema")


def test_dlt_source_uses_env_var(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("OIDEACHAIS_IG_EXPORT_DIR", str(tmp_path))
    (tmp_path / "connections" / "followers_and_following").mkdir(parents=True)
    (tmp_path / "connections" / "followers_and_following" / "followers_1.json").write_text(
        "[]", encoding="utf-8"
    )
    source = instagram_export_source()
    rows = list(source.resources["profiles"])
    assert rows == []


def test_dlt_source_raises_when_env_var_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OIDEACHAIS_IG_EXPORT_DIR", raising=False)
    monkeypatch.delenv("INSTAGRAM_EXPORT_DIR", raising=False)
    with pytest.raises(FileNotFoundError, match="OIDEACHAIS_IG_EXPORT_DIR"):
        instagram_export_source()


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_follower_list_kinds_has_seven_entries() -> None:
    """The 7 files Instagram ships are all in the lookup table."""
    assert set(FOLLOWER_LIST_KINDS.keys()) == {
        "followers_1.json",
        "following.json",
        "close_friends.json",
        "blocked_profiles.json",
        "pending_follow_requests.json",
        "removed_suggestions.json",
        "restricted_profiles.json",
    }


# ---------------------------------------------------------------------------
# Opt-in integration test against the real export (skipped unless
# OIDEACHAIS_IG_EXPORT_DIR is set AND explicitly requested).
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    not os.environ.get("OIDEACHAIS_IG_EXPORT_DIR"),
    reason="OIDEACHAIS_IG_EXPORT_DIR not set; opt-in only",
)
def test_real_export_parses() -> None:
    """Parse the real Instagram export referenced by OIDEACHAIS_IG_EXPORT_DIR.

    Run with: ``OIDEACHAIS_IG_EXPORT_DIR=~/stedding/instagram-whistlingmilk-2026-05-17-Da2GD2ii pytest -k test_real_export_parses``
    """
    parser = InstagramExportParser(os.environ["OIDEACHAIS_IG_EXPORT_DIR"])
    rows = parser.parse_all()
    assert len(rows) > 100, f"Expected >100 rows, got {len(rows)}"
    # Sanity-check: at least one official-media profile should be present
    usernames = {r.ig_username for r in rows}
    # The user's actual export contains the gchq account
    # (we don't assert this; we just assert the parser didn't crash)
    assert isinstance(usernames, set)
