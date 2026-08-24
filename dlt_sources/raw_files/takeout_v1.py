"""
Leabharlann Takeout dlt source (Phase 1 filesystem).

Auto-discovers three layouts:
1. `<account>/<product>/<file>`  — multi-account (e.g. `stedding/Takeout/personal/Drive/foo.docx`)
2. `<product>/<file>`             — single-account fallback (e.g. `stedding/Takeout/Drive/foo.docx`)
3. `~/Downloads/takeout-*.zip`    — new zips (Phase 2: extract+ingest)

Phase 1 ingests DOCX/PDF/TXT/MD/CSV (CSV is treated as a single-row document
and indexed via python-docx-style fallback). Phase 2 will add OAuth + Drive API.

Reference: openspec/changes/leabharlann-cocoindex-v1/specs/leabharlann-ingestion/spec.md
"""

from __future__ import annotations
import dlt


import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

from ._scanner import (
    PathGrammar,
    extract_content,
    scan_directory,
)

logger = structlog.get_logger(__name__)


DEFAULT_TAKEOUT_ROOT = Path(
    os.environ.get(
        "LEABHARLANN_TAKEOUT_ROOT",
        str(
            Path(__file__).resolve().parents[3]
            / "stedding"
            / "Takeout"
        ),
    )
)

# A small set of "product" labels that we expect to find as the top-level
# subdir under a takeout. Used to decide whether to treat the immediate
# subdir as a "domain" or as an "account" wrapper.
_KNOWN_PRODUCTS = {"Drive", "Gmail", "Gemini Apps", "Photos", "Keep", "Calendar", "Contacts", "other"}


def _detect_account_label(
    takeout_root: Path,
    file_path: Path,
) -> tuple[str, str]:
    """
    Decide whether the file is under a multi-account layout or single-account
    fallback. Returns (account_label, product_domain).

    Heuristic: if the top-level subdir under `takeout_root` is in
    `_KNOWN_PRODUCTS`, the entire takeout is single-account and the
    subdir name is the product domain. Otherwise, the top-level subdir
    is the account label and the next subdir is the product domain.
    """
    try:
        rel = file_path.relative_to(takeout_root)
    except ValueError:
        return "unknown", "unknown"
    parts = rel.parts
    if not parts:
        return "unknown", "unknown"
    if parts[0] in _KNOWN_PRODUCTS:
        return "stedding_takeout", parts[0]
    if len(parts) >= 2:
        return parts[0], parts[1]
    return parts[0], "other"


def _is_zip(path: Path) -> bool:
    return path.suffix.lower() == ".zip" and path.name.lower().startswith("takeout-")


def _takeout_grammar(base_path: Path) -> PathGrammar:
    return PathGrammar(
        subject_paths={},
        course_code_pattern=None,
        handwriting_extensions=set(),
        handwriting_subdirs=set(),
    )


# ============================================================================
# DLT source
# ============================================================================


@dlt.source(name="leabharlann_takeout")
def takeout_v1_source(
    base_path: str | Path = DEFAULT_TAKEOUT_ROOT,
    max_files: int | None = None,
    include_extraction: bool = True,
):
    """
    DLT source for `stedding/Takeout/`.

    Handles both the multi-account and single-account layouts. Phase 1 is
    filesystem only; Phase 2 will add OAuth + Drive API + Gmail export.
    """
    base_path = Path(base_path)
    grammar = _takeout_grammar(base_path)

    @dlt.resource(
        name="takeout_index",
        write_disposition="merge",
        primary_key=["file_path"],
        columns={
            "account": {"partition": True},
            "domain": {"partition": True},
        },
    )
    def takeout_index() -> Iterator[dict[str, Any]]:
        """One row per file in the takeout directory (across all accounts)."""
        if not base_path.exists():
            return
        for path in base_path.rglob("*"):
            if not path.is_file():
                continue
            if _is_zip(path):
                # Mark zips for Phase 2 (extract+ingest follow-up).
                account = "zip_pending_extract"
                domain = "zip"
            else:
                account, domain = _detect_account_label(base_path, path)
            try:
                rel = path.relative_to(base_path)
            except ValueError:
                rel = path
            try:
                stat = path.stat()
            except (OSError, PermissionError) as e:
                logger.warning("takeout_stat_failed", path=str(path), error=str(e))
                continue
            yield {
                "file_path": str(path),
                "relative_path": str(rel),
                "file_name": path.name,
                "file_size": stat.st_size,
                "file_type": path.suffix.lower().lstrip("."),
                "account": account,
                "domain": domain,
                "modified_at": stat.st_mtime,
                "discovered_at": _now_iso(),
                "is_zip": _is_zip(path),
            }

    @dlt.resource(
        name="takeout_documents",
        write_disposition="merge",
        primary_key=["file_path"],
    )
    def takeout_documents() -> Iterator[dict[str, Any]]:
        """Takeout documents (DOCX/PDF/TXT/MD) with text extraction."""
        if not base_path.exists():
            return
        for path in base_path.rglob("*"):
            if not path.is_file() or _is_zip(path):
                continue
            if path.suffix.lower() not in {".docx", ".pdf", ".md", ".txt", ".csv"}:
                continue
            account, domain = _detect_account_label(base_path, path)
            try:
                rel = path.relative_to(base_path)
            except ValueError:
                rel = path
            row: dict[str, Any] = {
                "file_path": str(path),
                "relative_path": str(rel),
                "file_name": path.name,
                "file_type": path.suffix.lower().lstrip("."),
                "account": account,
                "domain": domain,
            }
            if include_extraction:
                row = extract_content(row, base_path, grammar)
            yield row

    @dlt.resource(
        name="takeout_zip_manifest",
        write_disposition="merge",
        primary_key=["file_path"],
    )
    def takeout_zip_manifest() -> Iterator[dict[str, Any]]:
        """Manifest rows for any `takeout-*.zip` files (Phase 2: extract+ingest)."""
        if not base_path.exists():
            return
        # Look for zips in the takeout dir + the conventional Downloads dir.
        search_paths = [base_path]
        downloads = Path.home() / "Downloads"
        if downloads.exists():
            search_paths.append(downloads)
        for search_root in search_paths:
            for path in search_root.glob("takeout-*.zip"):
                try:
                    stat = path.stat()
                except (OSError, PermissionError):
                    continue
                yield {
                    "file_path": str(path),
                    "file_name": path.name,
                    "file_size": stat.st_size,
                    "modified_at": stat.st_mtime,
                    "account": "pending_extract",
                    "domain": "zip",
                    "discovered_at": _now_iso(),
                }

    return takeout_index, takeout_documents, takeout_zip_manifest


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


def create_takeout_v1_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "leabharlann_takeout",
) -> dlt.Pipeline:
    return dlt.pipeline(
        pipeline_name="leabharlann_takeout_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


__all__ = [
    "DEFAULT_TAKEOUT_ROOT",
    "_KNOWN_PRODUCTS",
    "takeout_v1_source",
    "create_takeout_v1_pipeline",
]
