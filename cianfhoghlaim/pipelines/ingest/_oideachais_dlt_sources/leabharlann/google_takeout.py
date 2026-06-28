"""
Google Takeout DLT source (Phase 1: filesystem only).

Indexes files in a per-account `Takeout/<account_label>/` directory.
Configuration is loaded from `author_archive_accounts.yaml` at the repo root
(or `AUTHOR_ARCHIVE_ACCOUNTS_PATH`).

Yields 4 resources per account:
1. `takeout_index` — one row per file with `account`, `mime_type`, `modified_at`.
2. `takeout_pdf_documents` — PDF with pymupdf extraction.
3. `takeout_word_documents` — DOCX with python-docx extraction.
4. `takeout_google_docs` — files with the `application/vnd.google-apps.document`
   MIME type (as exported to .docx/.pdf in the Takeout).

Phase 2 hooks (OAuth + Drive API + Gmail export) are stubbed in the
`_oauth.py` and `_download.py` modules. They raise `NotImplementedError`
in this change and are scheduled as a follow-up once the user provides
the Takeout zips and confirms the OAuth flow.

Reference: openspec/changes/author-archive-gemini-and-uos-ingestion/specs/google-takeout-ingestion/spec.md
"""

from __future__ import annotations

import os
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
import structlog

from ._scanner import (
    PathGrammar,
    extract_content,
    scan_directory,
)
from ._takeout_paths import (
    TakeoutAccountConfig,
    load_takeout_accounts,
)

logger = structlog.get_logger(__name__)

# Default path of the accounts YAML. Overridden by the AUTHOR_ARCHIVE_ACCOUNTS_PATH env var.
DEFAULT_ACCOUNTS_PATH = Path(
    os.environ.get(
        "AUTHOR_ARCHIVE_ACCOUNTS_PATH",
        str(Path.cwd() / "author_archive_accounts.yaml"),
    )
)


# Common MIME-type heuristic from file extension.
_EXT_TO_MIME: dict[str, str] = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
    ".html": "text/html",
    ".htm": "text/html",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".json": "application/json",
    ".csv": "text/csv",
    ".zip": "application/zip",
    ".eml": "message/rfc822",
    ".mbox": "application/mbox",
}


# ============================================================================
# DLT source (one per account — generator function)
# ============================================================================


def _takeout_grammar_for_account(account: TakeoutAccountConfig) -> PathGrammar:
    """Build a permissive PathGrammar for a Takeout directory."""
    return PathGrammar(
        subject_paths={},
        course_code_pattern=None,
        handwriting_extensions=set(),
        handwriting_subdirs=set(),
    )


def _detect_mime(path: Path) -> str:
    """Heuristic MIME-type from file extension. Falls back to `application/octet-stream`."""
    suffix = path.suffix.lower()
    if suffix in _EXT_TO_MIME:
        return _EXT_TO_MIME[suffix]
    if suffix in {".gdoc", ".gsheet", ".gslides", ".gdraw", ".gmap"}:
        # Google-native formats are exposed in the Takeout as their export mirror.
        return "application/vnd.google-apps.document"
    return "application/octet-stream"


def _gpg_recipients() -> list[str] | None:
    """
    Look up the workstation's GPG key fingerprint (if any).

    Returns None if GPG is unavailable or no key is present. The OCR/GPG
    encoder at `oideachais/dlt_sources/leabharlann/_gpg.py` (future work)
    will be the consumer.
    """
    try:
        import subprocess  # noqa: F401
    except ImportError:
        return None
    # Stub: GPG encryption is a Phase 2 concern. The spec notes that the
    # `gpg_encrypt_paths` knob defaults empty, so this is a no-op in Phase 1.
    return None


def _takeout_resource_for_account(
    account: TakeoutAccountConfig,
    grammar: PathGrammar,
    gpg_recipients: list[str] | None,
) -> Iterator[dict[str, Any]]:
    """Walk `account.takeout_path` and yield one index row per file."""
    if not account.takeout_path.exists():
        logger.warning(
            "takeout_path_not_found",
            account_label=account.account_label,
            path=str(account.takeout_path),
        )
        return

    for path in account.takeout_path.rglob("*"):
        if not path.is_file():
            continue

        try:
            rel = path.relative_to(account.takeout_path)
        except ValueError:
            rel = path

        rel_str = str(rel)
        is_gpg = account.is_gpg_path(rel_str)
        if is_gpg and not gpg_recipients:
            logger.debug(
                "gpg_path_skipped_no_recipients",
                account_label=account.account_label,
                path=rel_str,
            )
            is_gpg = False

        # Derive `domain` from the top-level Takeout folder (e.g. "Drive",
        # "Gmail", "Gemini Apps") — Takeout exports nest by product.
        domain = "other"
        if rel.parts:
            top = rel.parts[0]
            normalised = re.sub(r"[^a-z0-9]+", "_", top.lower()).strip("_")
            domain = normalised or "other"

        stat = path.stat()
        yield {
            "id": f"{account.account_label}:{rel_str}",
            "file_path": str(path),
            "relative_path": rel_str,
            "file_name": path.name,
            "file_size": stat.st_size,
            "mime_type": _detect_mime(path),
            "account": account.account_label,
            "domain": domain,
            "default_domain": account.default_domain,
            "modified_at": stat.st_mtime,
            "gpg_required": is_gpg,
            "gpg_fingerprint": gpg_recipients[0] if is_gpg and gpg_recipients else None,
            "discovered_at": _now_iso(),
        }


def _now_iso() -> str:
    from datetime import UTC, datetime

    return datetime.now(UTC).isoformat()


# ============================================================================
# DLT source definition
# ============================================================================


@dlt.source(name="author_archive_takeout")
def google_takeout_source(
    config_path: str | Path | None = None,
    account_label: str | None = None,
):
    """
    DLT source for Google Takeout directories (Phase 1: filesystem only).

    Args:
        config_path: Path to the `author_archive_accounts.yaml` file. Defaults
            to the env var `AUTHOR_ARCHIVE_ACCOUNTS_PATH` or
            `./author_archive_accounts.yaml` at CWD.
        account_label: If set, only the named account is processed (Dagster
            partition key). If None, all configured accounts are processed.
    """
    accounts = load_takeout_accounts(config_path=config_path)
    gpg_recipients = _gpg_recipients()

    selected: list[TakeoutAccountConfig] = []
    if account_label is not None:
        for a in accounts:
            if a.account_label == account_label:
                selected = [a]
                break
    else:
        selected = list(accounts)

    @dlt.resource(
        name="takeout_index",
        write_disposition="merge",
        primary_key=["account", "relative_path"],
        columns={
            "account": {"partition": True},
            "domain": {"partition": True},
        },
    )
    def takeout_index() -> Iterator[dict[str, Any]]:
        """One row per file in the Takeout (across all configured accounts)."""
        for account in selected:
            grammar = _takeout_grammar_for_account(account)
            yield from _takeout_resource_for_account(account, grammar, gpg_recipients)

    @dlt.resource(
        name="takeout_pdf_documents",
        write_disposition="merge",
        primary_key=["account", "relative_path"],
    )
    def takeout_pdf_documents() -> Iterator[dict[str, Any]]:
        """PDF files in the Takeout, with pymupdf extraction."""
        for account in selected:
            grammar = _takeout_grammar_for_account(account)
            for row in scan_directory(
                base_path=account.takeout_path,
                grammar=grammar,
                account=account.account_label,
                file_types=["pdf"],
            ):
                row = extract_content(row, account.takeout_path, grammar)
                yield row

    @dlt.resource(
        name="takeout_word_documents",
        write_disposition="merge",
        primary_key=["account", "relative_path"],
    )
    def takeout_word_documents() -> Iterator[dict[str, Any]]:
        """DOCX files in the Takeout, with python-docx extraction."""
        for account in selected:
            grammar = _takeout_grammar_for_account(account)
            for row in scan_directory(
                base_path=account.takeout_path,
                grammar=grammar,
                account=account.account_label,
                file_types=["word"],
            ):
                row = extract_content(row, account.takeout_path, grammar)
                yield row

    @dlt.resource(
        name="takeout_google_docs",
        write_disposition="merge",
        primary_key=["account", "relative_path"],
    )
    def takeout_google_docs() -> Iterator[dict[str, Any]]:
        """Google-Docs-native files (`.gdoc`/`.gsheet`/`.gslides`/etc.) — emitted as index rows."""
        for account in selected:
            grammar = _takeout_grammar_for_account(account)
            for row in _takeout_resource_for_account(
                account, grammar, gpg_recipients
            ):
                if row["mime_type"] == "application/vnd.google-apps.document":
                    yield row

    return takeout_index, takeout_pdf_documents, takeout_word_documents, takeout_google_docs


def create_takeout_pipeline(
    destination: str = "duckdb",
    dataset_name: str = "author_archive_takeout",
) -> dlt.Pipeline:
    """Create a DLT pipeline for the Takeout source (convenience helper)."""
    return dlt.pipeline(
        pipeline_name="author_archive_takeout_pipeline",
        destination=destination,
        dataset_name=dataset_name,
    )


# ============================================================================
# Phase 2 stubs (NOT IMPLEMENTED in this change)
# ============================================================================


def phase2_oauth_drive_export(*args: Any, **kwargs: Any) -> Iterator[dict[str, Any]]:
    """
    Phase 2: OAuth-driven Google Drive export.

    Raises `NotImplementedError` in this change. Deferred to a follow-up
    once the user provides the Takeout zips and confirms the OAuth flow.
    See `oideachais/dlt_sources/leabharlann/_oauth.py` for the entry point.
    """
    raise NotImplementedError(
        "phase2_oauth_drive_export: deferred until Takeout zips are available. "
        "See openspec/changes/author-archive-gemini-and-uos-ingestion/specs/google-takeout-ingestion/spec.md"
    )


def phase2_gmail_export(*args: Any, **kwargs: Any) -> Iterator[dict[str, Any]]:
    """Phase 2: Gmail export of `from:gemini.google.com` threads. Stub."""
    raise NotImplementedError(
        "phase2_gmail_export: deferred until Takeout zips are available."
    )


__all__ = [
    "DEFAULT_ACCOUNTS_PATH",
    "google_takeout_source",
    "create_takeout_pipeline",
    "phase2_oauth_drive_export",
    "phase2_gmail_export",
]
