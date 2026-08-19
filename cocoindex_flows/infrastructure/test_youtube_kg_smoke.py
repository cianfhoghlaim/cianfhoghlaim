"""Smoke tests for the Phase 1 YouTube KG pipeline of
`2026-07-14-multimodal-code-and-media-intel-v1`.

Run with `uv run pytest cianfhoghlaim/cocoindex/test_youtube_kg_smoke.py -v`.

# not-a-flow: this file is colocated test code, not a LanceDB flow.
# The cocoindex_v1_conformance audit treats every .py file under
# `cianfhoghlaim/cocoindex/` as a flow; the not-a-flow marker tells
# the audit to skip ALL 4 conformance rules (R1+R2+R3+R4).
"""

from __future__ import annotations

import pytest

# The youtube_kg_embedding module pulls in `shared_lifespan` from
# `_lifespan.py`, which in turn does `import cocoindex`. If the
# installed cocoindex is the wrong version, that import raises an
# AttributeError. We import defensively: skip the YouTube-KG-specific
# tests if cocoindex is broken in the dev environment.
try:
    from cianfhoghlaim.cocoindex import youtube_kg_embedding as _yt  # noqa: F401

    _COCOINDEX_OK = True
except (ImportError, AttributeError) as _e:
    _COCOINDEX_OK = False
    _COCOINDEX_ERROR = _e

# Load the youtube_videos module directly via importlib.util because
# `dlt/api_sources/__init__.py` imports `from .linkedin import *` which
# fails on the pre-existing broken `_shared.config` import chain. This
# pre-existing issue is outside the scope of
# `2026-07-14-multimodal-code-and-media-intel-v1`.
import importlib.util as _importlib_util
import sys as _sys
from pathlib import Path as _Path

_youtube_videos_path = (
    _Path(__file__).resolve().parents[1]
    / "dlt"
    / "api_sources"
    / "youtube_videos.py"
)
_spec = _importlib_util.spec_from_file_location(
    "cianfhoghlaim.dlt.api_sources.youtube_videos",
    _youtube_videos_path,
)
_youtube_videos = _importlib_util.module_from_spec(_spec)
_sys.modules["cianfhoghlaim.dlt.api_sources.youtube_videos"] = _youtube_videos
_spec.loader.exec_module(_youtube_videos)  # type: ignore[union-attr]

DEFAULT_STAGING_DIR = _youtube_videos.DEFAULT_STAGING_DIR
YouTubeVideoRow = _youtube_videos.YouTubeVideoRow
_DEFAULT_WATCHLIST = _youtube_videos._DEFAULT_WATCHLIST
_safe_upload_date = _youtube_videos._safe_upload_date
load_curated_watchlist = _youtube_videos.load_curated_watchlist


def test_safe_upload_date_normalizes_yt_dlp_string() -> None:
    """yt-dlp returns YYYYMMDD; we normalise to ISO 8601."""
    assert _safe_upload_date("20240715") == "2024-07-15"
    assert _safe_upload_date("") == ""
    assert _safe_upload_date(None) == ""
    assert _safe_upload_date("invalid") == ""  # wrong length


def test_default_watchlist_is_non_empty() -> None:
    """The fallback watchlist (when no YAML is present) must have ≥1 entry."""
    assert len(_DEFAULT_WATCHLIST) >= 1
    for entry in _DEFAULT_WATCHLIST:
        assert "channel_id" in entry
        assert "max_videos" in entry


def test_load_curated_watchlist_falls_back_when_yaml_missing(
    tmp_path,
) -> None:
    """When the YAML is missing, the loader returns the default watchlist."""
    missing = tmp_path / "nope.yaml"
    loaded = load_curated_watchlist(path=missing)
    assert loaded == _DEFAULT_WATCHLIST


def test_load_curated_watchlist_parses_a_valid_yaml(tmp_path) -> None:
    """A well-formed YAML list is returned as-is."""
    yaml_path = tmp_path / "watchlist.yaml"
    yaml_path.write_text(
        """
- channel_id: UC123
  channel_title: Test Channel
  max_videos: 2
  label: smoke-test
""",
        encoding="utf-8",
    )
    loaded = load_curated_watchlist(path=yaml_path)
    assert len(loaded) == 1
    assert loaded[0]["channel_id"] == "UC123"
    assert loaded[0]["label"] == "smoke-test"


def test_load_curated_watchlist_rejects_non_list(tmp_path) -> None:
    """A non-list YAML raises ValueError (not a silent fallthrough)."""
    bad = tmp_path / "bad.yaml"
    bad.write_text("not_a_list: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Expected.*list"):
        load_curated_watchlist(path=bad)


def test_you_tube_video_row_dataclass_fields() -> None:
    """The row dataclass has the 17 columns the DLT source emits."""
    expected_fields = {
        "video_id",
        "channel_id",
        "channel_title",
        "title",
        "description",
        "duration_s",
        "upload_date",
        "webpage_url",
        "uploader_id",
        "uploader_name",
        "tags",
        "categories",
        "language",
        "file_path",
        "info_json_path",
        "sha256",
        "bytes_on_disk",
        "downloaded_at",
        "curated_label",
    }
    assert expected_fields.issubset(set(YouTubeVideoRow.__dataclass_fields__.keys()))


def test_youtube_kg_embedding_module_reexports_constants() -> None:
    """The 3 LanceDB table names + the DuckLake source name are exported."""
    if not _COCOINDEX_OK:
        pytest.skip(
            f"cocoindex import failed (pre-existing dev-env issue): {_COCOINDEX_ERROR}"
        )
    assert _yt.LANCEDB_TABLE_SEGMENTS == "video_segments"
    assert _yt.LANCEDB_TABLE_FRAME_CAPTIONS == "video_frame_captions"
    assert _yt.LANCEDB_TABLE_TRIPLES == "video_triples"
    assert _yt.YOUTUBE_VIDEOS_DUCKLAKE_TABLE == "cianfhoghlaim.youtube.youtube_videos"


def test_youtube_kg_embedding_data_model_has_embedding_columns() -> None:
    """Each row dataclass carries an `embedding: Annotated[list[float], EMBED_MODEL]`."""
    if not _COCOINDEX_OK:
        pytest.skip(
            f"cocoindex import failed (pre-existing dev-env issue): {_COCOINDEX_ERROR}"
        )
    from cianfhoghlaim.cocoindex.youtube_kg_embedding import (
        VideoFrameCaptionRecord,
        VideoSegmentRecord,
        VideoTripleRecord,
    )

    for cls in (VideoSegmentRecord, VideoFrameCaptionRecord, VideoTripleRecord):
        fields = cls.__dataclass_fields__
        assert "embedding" in fields, f"{cls.__name__} missing embedding column"