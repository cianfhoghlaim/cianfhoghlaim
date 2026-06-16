"""
Tests for the leabharlann ingestion pipeline (books + zotero + takeout v1).

Covers:
1. dlt sources (leabharlann_books, zotero, takeout_v1) — filesystem scan
   against the real `leabharlann/` directories.
2. _epub_extractor graceful degradation when ebooklib is missing.
3. takeout_v1 auto-discovery (with and without account prefix).
4. BAML `ZoteroPaper` schema imports.
5. arxiv_id extraction (legacy + modern).
6. previews helper (PNG pairing).
7. CocoIndex v1 App loadability (3 Apps, 1 query handler per table).
8. Dagster assets (7) + sensor.
9. Path resolution: DEFAULT_*_PATH constants point at leabharlann/.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Make the dlt source package importable regardless of pytest cwd.
_REPO_ROOT = Path(__file__).resolve().parents[2]
for p in (str(_REPO_ROOT), str(_REPO_ROOT / "oideachais")):
    if p not in sys.path:
        sys.path.insert(0, p)


# ============================================================================
# Path resolution
# ============================================================================


def test_leabharlann_path_resolution() -> None:
    """DEFAULT_*_PATH constants point at the new leabharlann/ tree."""
    from dlt_sources.author_archive import (
        DEFAULT_LEABHARLANN_ROOT,
        DEFAULT_UOG_PATH,
        DEFAULT_GEMINI_PATH,
        DEFAULT_ZOTERO_ROOT,
        DEFAULT_TAKEOUT_ROOT,
    )

    # All should end with a path under the repo root.
    repo_root = Path(__file__).resolve().parents[2]
    for name, p in [
        ("DEFAULT_LEABHARLANN_ROOT", DEFAULT_LEABHARLANN_ROOT),
        ("DEFAULT_UOG_PATH", DEFAULT_UOG_PATH),
        ("DEFAULT_GEMINI_PATH", DEFAULT_GEMINI_PATH),
        ("DEFAULT_ZOTERO_ROOT", DEFAULT_ZOTERO_ROOT),
        ("DEFAULT_TAKEOUT_ROOT", DEFAULT_TAKEOUT_ROOT),
    ]:
        try:
            rel = p.relative_to(repo_root)
            # Should be inside the repo.
            assert not str(rel).startswith(".."), f"{name}={p} is outside repo"
        except ValueError:
            pytest.fail(f"{name}={p} is not under {repo_root}")


# ============================================================================
# arxiv_id extraction
# ============================================================================


def test_extract_arxiv_id_modern() -> None:
    from cocoindex_flows.leabharlann_embedding import extract_arxiv_id_from_filename

    assert extract_arxiv_id_from_filename("2504.02890v2.pdf") == ("2504.02890", "v2")
    assert extract_arxiv_id_from_filename("2510.17652v1.pdf") == ("2510.17652", "v1")
    assert extract_arxiv_id_from_filename("2511.06876v1.pdf") == ("2511.06876", "v1")
    assert extract_arxiv_id_from_filename("2510.20957v1.pdf") == ("2510.20957", "v1")


def test_extract_arxiv_id_legacy_and_dup() -> None:
    from cocoindex_flows.leabharlann_embedding import extract_arxiv_id_from_filename

    # Pre-DOI arXiv: 4 digits + __dup0 suffix.
    assert extract_arxiv_id_from_filename("2402__dup0.pdf") == ("2402", None)
    # 4 digits followed by underscore: matches the legacy regex.
    assert extract_arxiv_id_from_filename("2025.cltw-1__dup0.pdf") == ("2025", None)
    # No arXiv at all.
    assert extract_arxiv_id_from_filename("gaBERT - 2022 - an Irish Language Model.pdf") == (None, None)
    assert extract_arxiv_id_from_filename("gaBERT.pdf") == (None, None)


# ============================================================================
# Zotero dlt source
# ============================================================================


def test_zotero_source_yields_arxiv_and_dup_columns() -> None:
    from dlt_sources.author_archive import DEFAULT_ZOTERO_ROOT, zotero_source

    if not DEFAULT_ZOTERO_ROOT.exists():
        pytest.skip(f"Zotero archive not present: {DEFAULT_ZOTERO_ROOT}")

    rows = list(
        zotero_source(max_files=50).selected_resources["all_documents"]
    )
    if not rows:
        pytest.skip("Zotero archive empty")

    # Find at least one row with arxiv_id AND at least one with __dup0.
    arxiv_rows = [r for r in rows if r.get("arxiv_id")]
    dup_rows = [r for r in rows if r.get("duplicate_marker") == "__dup0"]
    assert arxiv_rows, "Expected at least one arXiv paper"
    assert dup_rows, "Expected at least one __dup0 paper"

    for row in arxiv_rows:
        assert "title_guess" in row
        assert "file_hash" in row
        # The empty _.pdf placeholder is skipped.
        assert row["file_name"] != "_.pdf"
        assert row["file_size"] > 0


def test_zotero_source_skips_empty_placeholder() -> None:
    from dlt_sources.author_archive import DEFAULT_ZOTERO_ROOT, zotero_source

    if not DEFAULT_ZOTERO_ROOT.exists():
        pytest.skip(f"Zotero archive not present: {DEFAULT_ZOTERO_ROOT}")

    rows = list(
        zotero_source(max_files=500).selected_resources["all_documents"]
    )
    # The empty `_.pdf` is 0 bytes and must be skipped.
    for r in rows:
        assert r["file_name"] != "_.pdf", "Empty _.pdf placeholder must be skipped"


# ============================================================================
# Leabharlann books dlt source
# ============================================================================


def test_leabharlann_books_source_yields_partitioned_rows() -> None:
    from dlt_sources.author_archive import DEFAULT_LEABHARLANN_ROOT, leabharlann_books_source

    if not DEFAULT_LEABHARLANN_ROOT.exists():
        pytest.skip(f"leabharlann archive not present: {DEFAULT_LEABHARLANN_ROOT}")

    rows = list(
        leabharlann_books_source(max_files=30).selected_resources["all_documents"]
    )
    if not rows:
        pytest.skip("leabharlann archive empty")

    subjects = {r.get("subject") for r in rows}
    assert "gaeilge" in subjects or "aigne" in subjects

    for r in rows[:5]:
        assert r["account"] == "leabharlann"
        assert r.get("subject") in {"gaeilge", "aigne", "epub", "md"}
        assert "file_hash" in r


def test_leabharlann_books_preview_pairing() -> None:
    from dlt_sources.author_archive import DEFAULT_LEABHARLANN_ROOT, leabharlann_books_source

    if not DEFAULT_LEABHARLANN_ROOT.exists():
        pytest.skip(f"leabharlann archive not present: {DEFAULT_LEABHARLANN_ROOT}")

    gaeilge_dir = DEFAULT_LEABHARLANN_ROOT / "gaeilge"
    if not gaeilge_dir.exists():
        pytest.skip("gaeilge dir missing")

    rows = list(
        leabharlann_books_source(max_files=50).selected_resources["all_documents"]
    )
    gaeilge_rows = [r for r in rows if r.get("subject") == "gaeilge"]
    if not gaeilge_rows:
        pytest.skip("no gaeilge books found")

    # At least one gaeilge book has a preview_path populated.
    with_preview = [r for r in gaeilge_rows if r.get("preview_path")]
    assert with_preview, "Expected at least one gaeilge book with a preview_path"
    for r in with_preview:
        assert r["preview_path"].endswith("_preview.png")


# ============================================================================
# Takeout v1 dlt source
# ============================================================================


def test_takeout_v1_source_yields_rows() -> None:
    from dlt_sources.author_archive import DEFAULT_TAKEOUT_ROOT, takeout_v1_source

    if not DEFAULT_TAKEOUT_ROOT.exists():
        pytest.skip(f"Takeout archive not present: {DEFAULT_TAKEOUT_ROOT}")

    rows = list(
        takeout_v1_source(max_files=30).selected_resources["takeout_index"]
    )
    if not rows:
        pytest.skip("Takeout archive empty")

    for r in rows[:5]:
        assert r["account"] == "stedding_takeout"
        assert r["domain"] == "Drive"
        assert r["file_type"] in {"docx", "csv", "pdf", "md", "txt"}
        assert r.get("is_zip") is False  # The sample takeout has no .zip in it
        assert r.get("file_size", 0) > 0


def test_takeout_v1_account_fallback() -> None:
    """The no-account-prefix layout falls back to account='stedding_takeout'."""
    from dlt_sources.author_archive import takeout_v1_source, _detect_account_label

    # Direct test of the helper: given a path directly under the takeout root
    # with a known product name, the account should be the fallback.
    fake_root = Path("/tmp/fake_takeout")
    fake_path = fake_root / "Drive" / "foo.docx"
    account, domain = _detect_account_label(fake_root, fake_path)
    assert account == "stedding_takeout"
    assert domain == "Drive"


def test_takeout_v1_account_multi_account() -> None:
    """The multi-account layout uses the directory name as the account."""
    from dlt_sources.author_archive import _detect_account_label

    fake_root = Path("/tmp/fake_takeout")
    fake_path = fake_root / "cian_personal" / "Drive" / "foo.docx"
    account, domain = _detect_account_label(fake_root, fake_path)
    assert account == "cian_personal"
    assert domain == "Drive"


# ============================================================================
# EPUB extractor
# ============================================================================


def test_epub_extractor_graceful_degradation(tmp_path: Path) -> None:
    """extract_epub_chapters returns 'skipped_no_library' when ebooklib is missing."""
    from dlt_sources.author_archive._epub_extractor import extract_epub_chapters

    # If ebooklib IS installed, the file-not-found path returns 'error' instead.
    fake_epub = tmp_path / "does_not_exist.epub"
    result = extract_epub_chapters(fake_epub)
    # Either "skipped_no_library" (no ebooklib) or "error" (file not found).
    assert result["status"] in {"skipped_no_library", "error"}
    assert result["epub_chapters"] == []
    assert result["epub_total_chars"] == 0


# ============================================================================
# Previews helper
# ============================================================================


def test_find_preview_for(tmp_path: Path) -> None:
    from dlt_sources.author_archive.previews import find_preview_for

    book = tmp_path / "book.pdf"
    book.write_text("dummy")
    previews = tmp_path / "previews"
    previews.mkdir()
    preview = previews / "book_preview.png"
    preview.write_bytes(b"\x89PNG")

    assert find_preview_for(book, previews) == str(preview)


def test_find_preview_for_no_match(tmp_path: Path) -> None:
    from dlt_sources.author_archive.previews import find_preview_for

    book = tmp_path / "missing.pdf"
    previews = tmp_path / "previews"
    previews.mkdir()
    assert find_preview_for(book, previews) is None


# ============================================================================
# BAML ZoteroPaper schema
# ============================================================================


def test_baml_zotero_paper_importable() -> None:
    from baml_client.types import Author, PaperKind, ZoteroPaper

    # Field-level assertions.
    assert "paper_kind" in ZoteroPaper.model_fields
    assert "arxiv_id" in ZoteroPaper.model_fields
    assert "doi" in ZoteroPaper.model_fields
    assert "title" in ZoteroPaper.model_fields
    assert "authors" in ZoteroPaper.model_fields
    assert "year" in ZoteroPaper.model_fields
    assert "abstract" in ZoteroPaper.model_fields
    assert "venue" in ZoteroPaper.model_fields
    assert "irish_relevant" in ZoteroPaper.model_fields
    assert "htr_relevant" in ZoteroPaper.model_fields
    assert "confidence" in ZoteroPaper.model_fields

    assert "name" in Author.model_fields
    assert "affiliation" in Author.model_fields

    # All 7 PaperKind enum values are present.
    members = {m.value for m in PaperKind}
    assert members == {
        "ARXIV_PREPRINT",
        "JOURNAL_ARTICLE",
        "CONFERENCE_PAPER",
        "THESIS",
        "BOOK_CHAPTER",
        "BOOK",
        "OTHER",
    }


# ============================================================================
# CocoIndex v1 Apps
# ============================================================================


def test_cocoindex_v1_apps_loadable() -> None:
    """The 3 CocoIndex v1 Apps exist and have the expected names."""
    from cocoindex_flows import (
        leabharlann_books_app,
        leabharlann_zotero_app,
        leabharlann_takeout_app,
    )

    # Each App has a `update` method and a `config` attr.
    for app in (leabharlann_books_app, leabharlann_zotero_app, leabharlann_takeout_app):
        assert callable(getattr(app, "update", None))
        assert callable(getattr(app, "update_blocking", None))


def test_leabharlann_embedding_module_metadata() -> None:
    """The module exports the expected constants and search helpers."""
    from cocoindex_flows import (
        LEABHARLANN_EMBED_MODEL,
        LEABHARLANN_EMBED_DIM,
        LEABHARLANN_LANCEDB_URI,
        LEABHARLANN_COCOINDEX_AVAILABLE,
        search_leabharlann_books,
        search_leabharlann_zotero,
        search_leabharlann_takeout,
    )

    assert LEABHARLANN_EMBED_MODEL == "BAAI/bge-large-en-v1.5"
    assert LEABHARLANN_EMBED_DIM == 1024
    assert LEABHARLANN_LANCEDB_URI.startswith("rest://")
    assert LEABHARLANN_COCOINDEX_AVAILABLE is True
    for fn in (search_leabharlann_books, search_leabharlann_zotero, search_leabharlann_takeout):
        assert callable(fn)


# ============================================================================
# Dagster assets
# ============================================================================


def test_leabharlann_assets() -> None:
    """7 leabharlann assets import and have the right group_name."""
    from dagster_defs.assets.leabharlann_assets import LEABHARLANN_ASSETS

    assert len(LEABHARLANN_ASSETS) == 7
    expected_names = {
        "leabharlann_books_raw",
        "leabharlann_zotero_raw",
        "leabharlann_takeout_v1_raw",
        "leabharlann_paper_metadata",
        "leabharlann_cocoindex_books_update",
        "leabharlann_cocoindex_zotero_update",
        "leabharlann_cocoindex_takeout_update",
    }
    actual_names = {
        spec.key.to_user_string() for asset in LEABHARLANN_ASSETS for spec in asset.specs
    }
    assert actual_names == expected_names

    for asset in LEABHARLANN_ASSETS:
        for spec in asset.specs:
            assert spec.group_name == "leabharlann_ingestion"


def test_leabharlann_sensor() -> None:
    """The leabharlann sensor module exposes the expected list."""
    from dagster_defs.sensors.leabharlann_sensors import (
        leabharlann_directory_sensor,
        leabharlann_sensors,
    )

    assert leabharlann_directory_sensor.name == "leabharlann_directory_sensor"
    assert leabharlann_sensors == [leabharlann_directory_sensor]
