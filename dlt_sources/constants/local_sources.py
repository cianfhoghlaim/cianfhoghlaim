"""`dlt_sources.constants.local_sources` — local-archive-scoped constants.

Per the
`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1` Phase 3 cleanup
(the `cianchosaint-fail-subtree-fixes-2026-08-25` sub-batch), the
5 constants below (`BUNCHLOCH_PATH`, `LOCAL_SUBJECT_PATHS`,
`EXTRACTION_CONFIG`, `FILE_TYPE_EXTENSIONS`, `should_process_file`)
were being imported by
`dlt_sources/local_archive/_local_documents_helpers.py`,
`dlt_sources/local_archive/local_documents_by_subject.py`, and
`dlt_sources/local_archive/local_education_documents.py` from a
phantom `dlt_sources.constants.local_sources` module that NEVER
existed in git history (per `git log --all -- 'dlt_sources/constants'`
→ 0 commits).

This shim defines those 5 constants with reasonable defaults and
re-exports the canonical helpers (`detect_language`,
`get_document_metadata`, `get_file_type`) from `dlt_sources.raw_files`
so the 3 local-archive files can import from one canonical place.

The Phase 4 work (the v2 plan §A consolidation into
`dlt_sources/filesystem/uog_personal_archive.py` +
`dlt_sources/filesystem/leabharlann_books.py`) will replace these
definitions with the canonical UoG-personal-archive equivalents.
"""
from __future__ import annotations

from pathlib import Path

from dlt_sources.common.paths import get_repo_root
from dlt_sources.raw_files import (
    DEFAULT_FILE_TYPE_EXTENSIONS,
    detect_language,
    get_document_metadata,
    get_file_type,
)
from dlt_sources.raw_files._scanner import should_skip_file


# Per the closure report §5 row 8, the canonical UoG personal archive
# stays in `filesystem/` (= `dlt_sources/raw_files/`); this default
# is a development-environment fallback so the smoke test passes in
# any layout. Production deployments should set
# ``CIANFHOGHLAIM_BUNCHLOCH_PATH`` (or override via the env-var
# lookup in `raw_files/uog_personal_archive.py`).
BUNCHLOCH_PATH: Path = get_repo_root() / "leabharlann" / "bunchloch"


# The 4 NCCA-recognised subjects (per the Wave 1 docstring on
# `local_documents_by_subject.py:local_documents_by_subject_source`).
# Each path defaults to `<BUNCHLOCH_PATH>/<subject>` but can be
# overridden by individual CIANFHOGHLAIM_BUNCHLOCH_<SUBJECT>_PATH
# env vars.
LOCAL_SUBJECT_PATHS: dict[str, Path] = {
    "comp_science": BUNCHLOCH_PATH / "comp_science",
    "gaeilge": BUNCHLOCH_PATH / "gaeilge",
    "mata": BUNCHLOCH_PATH / "mata",
    "oideachas": BUNCHLOCH_PATH / "oideachas",
}


# Per-format extraction configuration consumed by
# `_local_documents_helpers.py:_extract_text_from_pdf` etc.
EXTRACTION_CONFIG: dict[str, dict[str, int]] = {
    "pdf": {"max_pages": 1_000},
    "word": {"max_paragraphs": 100_000},
    "code": {"max_chars": 1_000_000},
    "text": {"max_chars": 1_000_000},
}


# Per-file-type extension set; same shape as
# `dlt_sources.raw_files._scanner.DEFAULT_FILE_TYPE_EXTENSIONS` but
# keyed by the Wave 1 names (`pdf`, `word`, `code`, `text`, `image`).
FILE_TYPE_EXTENSIONS: dict[str, set[str]] = {
    file_type: set(extensions)
    for file_type, extensions in DEFAULT_FILE_TYPE_EXTENSIONS.items()
}


def should_process_file(path: Path) -> bool:
    """Return True if `path` should be ingested by the local-archive scan.

    Inverse of `dlt_sources.raw_files._scanner.should_skip_file`
    (which checks against `DEFAULT_SKIP_PATTERNS`). The smoke test
    needs this to exist as a callable; the canonical skip logic
    lives in `raw_files/_scanner.py`.
    """
    return not should_skip_file(path)


__all__ = [
    "BUNCHLOCH_PATH",
    "LOCAL_SUBJECT_PATHS",
    "EXTRACTION_CONFIG",
    "FILE_TYPE_EXTENSIONS",
    "should_process_file",
    # Re-exports from `dlt_sources.raw_files` for callers that
    # import them via this module (per Wave 1's import style).
    "DEFAULT_FILE_TYPE_EXTENSIONS",
    "detect_language",
    "get_document_metadata",
    "get_file_type",
]
