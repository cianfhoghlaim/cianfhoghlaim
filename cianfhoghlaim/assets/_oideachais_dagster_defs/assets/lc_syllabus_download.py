"""
Dagster asset for downloading the curriculumonline.ie Leaving Certificate syllabi corpus.

Per the `ncca-leaving-cert-syllabi-corpus` openspec change (2026-06-30):
- 8 subjects * 2 languages = 16 base partitions
- (gaeilge, en) is a no-op partition (the subject is taught in Irish only)
- The asset downloads each PDF URL emitted by the `curriculumonline_syllabi` DLT
  source into `stedding/ingest_queue/curriculumonline.ie/{subject}/{lang}/{filename}.pdf`
- Idempotent: SHA-256 dedup means re-runs are no-ops
- MaterializeResult metadata includes `url`, `filename`, `size_bytes`, `sha256`,
  `skipped`, `http_status`

This asset is auto-discovered by the existing `_oideachais_dagster_defs` mount
point — drop a file in this directory and the new asset appears in the Dagster UI.
"""
from __future__ import annotations

import hashlib
import logging
import os
import warnings
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dagster as dg
import requests
import structlog
from dagster import (
    AssetExecutionContext,
    AssetKey,
    MaterializeResult,
    MetadataValue,
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
)

warnings.filterwarnings("ignore", category=DeprecationWarning)

from cianfhoghlaim.pipelines.ingest.ie.education.curriculumonline_syllabi import (  # noqa: E402
    SENIOR_CYCLE_SYLLABI_SUBJECTS,
    _extract_pdf_links_from_page,
    _filename_from_url,
    _scrape_subject_page,
)

logger = structlog.get_logger(__name__)
logging.basicConfig(level=logging.INFO)


# 8 priority subjects
SUBJECT_PARTITIONS = StaticPartitionsDefinition(SENIOR_CYCLE_SYLLABI_SUBJECTS)
# 2 languages
LANGUAGE_PARTITIONS = StaticPartitionsDefinition(["en", "ga"])

LC_SYLLABUS_PARTITIONS = MultiPartitionsDefinition({
    "subject": SUBJECT_PARTITIONS,
    "language": LANGUAGE_PARTITIONS,
})


# Stedding root — same convention as the rest of the pipeline.
STEDDING_ROOT = Path(os.environ.get("STEDDING_ROOT", "/stedding/ingest_queue"))
INGEST_TARGET = STEDDING_ROOT / "curriculumonline.ie"

# HTTP settings — match the Firecrawl 21-second throttle baseline but per-request
HTTP_TIMEOUT_SECONDS = 30
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def _download_pdf_bytes(url: str) -> tuple[bytes, int]:
    """Download a PDF and return (bytes, http_status).

    Raises requests.HTTPError on non-2xx.
    """
    resp = requests.get(
        url,
        timeout=HTTP_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
        allow_redirects=True,
    )
    resp.raise_for_status()
    return resp.content, resp.status_code


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ============================================================================
# Asset
# ============================================================================

@dg.asset(
    key=AssetKey(["lc_syllabus", "download"]),
    group_name="lc_syllabus",
    compute_kind="python",
    partitions_def=LC_SYLLABUS_PARTITIONS,
    description=(
        "Download the currently-taught Leaving Certificate syllabi PDFs from "
        "curriculumonline.ie for one (subject, language) partition. Writes "
        "PDF bytes to stedding/ingest_queue/curriculumonline.ie/{subject}/{lang}/ "
        "and emits MaterializeResult metadata (url, filename, size_bytes, "
        "sha256, skipped, http_status). Idempotent: SHA-256 dedup. The "
        "(gaeilge, en) partition is a no-op (no English syllabus exists for "
        "the Gaeilge subject, which is taught through Irish only)."
    ),
    metadata={
        "spec": "ncca-leaving-cert-syllabi-corpus",
        "source_domain": "curriculumonline.ie",
    },
)
def lc_syllabus_download(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Download the curriculumonline.ie syllabi for one (subject, language) pair."""
    parts = context.partition_key.keys() if hasattr(context.partition_key, "keys") else context.partition_key
    if isinstance(parts, dict):
        subject = parts["subject"]
        language = parts["language"]
    else:
        # Fallback: parse "subject|language" string format
        subject, language = str(context.partition_key).split("|")

    context.log.info(f"lc_syllabus_download started subject={subject} language={language}")

    # No-op partition: Gaeilge has no English syllabus
    if subject == "gaeilge" and language == "en":
        context.log.info("Skipping (gaeilge, en) — no English syllabus exists for Gaeilge subject")
        return MaterializeResult(
            metadata={
                "subject": subject,
                "language": language,
                "status": "no_op_gaeilge_no_en_syllabus",
                "documents_processed": 0,
            }
        )

    # Discover PDFs by scraping the subject page
    pages = _scrape_subject_page(subject, language)
    if not pages:
        context.log.warning(f"No pages scraped for {subject}/{language}")
        return MaterializeResult(
            metadata={
                "subject": subject,
                "language": language,
                "status": "scrape_failed",
                "documents_processed": 0,
            }
        )

    # Flatten all discovered PDFs across pages
    discovered: list[dict[str, Any]] = []
    for page in pages:
        for pdf in _extract_pdf_links_from_page(page, subject, language):
            discovered.append(pdf.to_row())

    # Also do a second pass on the OTHER language to detect "GA uses EN" cases
    # (e.g., English subject: GA page links to the same EN PDF — verified 2026-06-30)
    if not discovered:
        other_lang = "ga" if language == "en" else "en"
        context.log.info(
            f"No PDFs found for {subject}/{language}; checking {other_lang} page "
            "in case it cross-links"
        )
        other_pages = _scrape_subject_page(subject, other_lang)
        for page in other_pages:
            for pdf in _extract_pdf_links_from_page(page, subject, other_lang):
                # Re-label to the requested language so it lands in the right partition
                row = pdf.to_row()
                row["language"] = language
                row["filename"] = f"{row['filename']}.{language}"
                discovered.append(row)

    if not discovered:
        context.log.info(
            f"No PDFs discovered for {subject}/{language}; emitting empty result"
        )
        return MaterializeResult(
            metadata={
                "subject": subject,
                "language": language,
                "status": "no_pdfs_discovered",
                "documents_processed": 0,
            }
        )

    # Download each PDF
    target_dir = INGEST_TARGET / subject / language
    target_dir.mkdir(parents=True, exist_ok=True)

    documents_processed = 0
    documents_skipped = 0
    documents_errored = 0
    aggregate_size = 0
    download_log: list[dict[str, Any]] = []

    # Get today's date for the date-suffixed copy that pdf_processing_syllabus
    # picks up via `**/*-{today_str}*.pdf` glob (per the established pipeline
    # convention). We write BOTH a canonical-name file and a date-suffixed
    # file so the corpus is browsable by name AND picked up by the daily asset.
    today_str = datetime.now(UTC).strftime("%Y-%m-%d")

    for row in discovered:
        url = row["url"]
        filename = row["filename"]
        if not filename or filename == "unknown.pdf":
            # Derive filename from URL if missing
            filename = _filename_from_url(url)
        target_path = target_dir / filename
        # Date-suffixed companion file (e.g. SCSEC25_..._English_2026-06-30.pdf)
        stem = target_path.stem
        dated_path = target_dir / f"{stem}_{today_str}.pdf"

        # SHA-256 dedup
        if target_path.exists():
            try:
                existing_hash = _sha256_bytes(target_path.read_bytes())
            except OSError:
                existing_hash = None
            # Re-download to compare if we have no hash; otherwise trust it
            if existing_hash is not None:
                # Mark as skipped — file already exists. To strictly check
                # upstream changes we'd need a manifest; for now assume idempotent
                # writes are good (the user can force-re-run by deleting the file).
                context.log.info(
                    f"Skipped (file exists): {target_path.name} "
                    f"sha256={existing_hash[:12]}"
                )
                documents_skipped += 1
                download_log.append({
                    "url": url,
                    "filename": filename,
                    "sha256": existing_hash,
                    "skipped": True,
                    "status": "exists_locally",
                })
                continue

        # Download
        try:
            pdf_bytes, http_status = _download_pdf_bytes(url)
        except Exception as exc:  # pragma: no cover - network-dependent
            context.log.error(f"Download failed for {url}: {exc}")
            documents_errored += 1
            download_log.append({
                "url": url,
                "filename": filename,
                "skipped": False,
                "status": f"download_failed: {exc}",
            })
            continue

        sha = _sha256_bytes(pdf_bytes)
        target_path.write_bytes(pdf_bytes)
        # Also write a date-suffixed companion file so the daily
        # pdf_processing_syllabus asset picks it up via `**/*-{today_str}*.pdf`
        if not dated_path.exists() or _sha256_bytes(dated_path.read_bytes()) != sha:
            dated_path.write_bytes(pdf_bytes)
        documents_processed += 1
        aggregate_size += len(pdf_bytes)
        download_log.append({
            "url": url,
            "filename": filename,
            "size_bytes": len(pdf_bytes),
            "sha256": sha,
            "skipped": False,
            "http_status": http_status,
        })
        context.log.info(
            f"Downloaded {filename} size={len(pdf_bytes)} sha256={sha[:12]} http={http_status}"
        )

    context.log.info(
        f"lc_syllabus_download complete subject={subject} language={language} "
        f"processed={documents_processed} skipped={documents_skipped} "
        f"errored={documents_errored} total_bytes={aggregate_size}"
    )

    return MaterializeResult(
        metadata={
            "subject": subject,
            "language": language,
            "documents_processed": documents_processed,
            "documents_skipped": documents_skipped,
            "documents_errored": documents_errored,
            "total_bytes": aggregate_size,
            "download_log": MetadataValue.json(download_log),
        }
    )
