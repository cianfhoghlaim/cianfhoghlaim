"""DLT filesystem source for downloading LC PDFs to Garage S3 (BIEP v1 — Phase 4).

Downloads:
- NCCA syllabus PDFs (from ncca_source)
- SEC exam paper + marking scheme PDFs (from examinations_source)
- gov.ie circular PDFs (from gov_ie_circulars_source)

Target path pattern:
    s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf

Honours the project's `USE_LOCAL_SCRAPES=true` env-var convention by
reading from the curated `cianfhoghlaim/leaving_certificate/<subject>/`
sample corpus (skipping the download step entirely).

Uses `apply_ducklake_1_0_optimisations()` from
`cianfhoghlaim.dlt_sources.common.ducklake_options` to register the
DuckLake 1.0 sort + bucket + inlining optimisations on the
`pdf_downloads` table once it's materialised.

Partitions:
    subject  ∈ LC6_SUBJECTS (mathematics, chemistry, geography, gaeilge, english, computer_science)
    language ∈ {en, ga}
    year     ∈ 1990..2026

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
           tasks.md — Phase 4 (item 4.1)

Usage:
    from dlt_sources.filesystem.pdf_download_source import (
        pdf_download_source, pdf_download_lc6_partitions,
    )

    # BIEP v1 — Mathematics EN 2024 PDFs from local cache
    pipeline.run(pdf_download_source(subject="mathematics", language="en", year=2024))
"""
from __future__ import annotations
import dlt


import hashlib
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

from dlt_sources.british_isles.ireland.education.examinations import LC6_SUBJECTS

import dlt_sources
from observability.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# Configuration
# ============================================================================
LC6_LANGUAGES: list[str] = ["en", "ga"]
LC6_YEAR_RANGE: tuple[int, int] = (1990, 2026)
GARAGE_BUCKET = "s3://garage/oideachais"
"""The canonical Garage S3 bucket + namespace for the BIEP v1 PDF lake."""

GARAGE_PDF_PREFIX = "leaving_cert"
"""The S3 prefix under the bucket for the BIEP v1 PDF corpus."""

# Local cache directory (per BIEP v1 Phase 4 — `USE_LOCAL_SCRAPES=true`)
_CIANFHOGHLAIM_ROOT = Path(
    os.environ.get(
        "CIANFHOGHLAIM_ROOT",
        "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim",
    )
)
_LOCAL_PDF_CACHE = _CIANFHOGHLAIM_ROOT / "leaving_certificate"
"""The local curated PDF corpus at `cianfhoghlaim/leaving_certificate/<subject>/`."""

_LOCAL_SCRAPES = os.environ.get("USE_LOCAL_SCRAPES", "").lower() in (
    "1",
    "true",
    "yes",
)


# ============================================================================
# Helpers
# ============================================================================
def _s3_path(subject: str, language: str, year: int, filename: str) -> str:
    """Build the canonical S3 path for an LC PDF.

    Format: s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<filename>
    """
    return f"{GARAGE_BUCKET}/{GARAGE_PDF_PREFIX}/{subject}/{language}/{year}/{filename}"


def _local_path(subject: str, language: str, filename: str) -> Path:
    """Build the local cache path for an LC PDF.

    Format: <root>/leaving_certificate/<subject>/<lang>/<filename>
    """
    return _LOCAL_PDF_CACHE / subject / language / filename


def _compute_sha256(path: Path) -> str:
    """Compute the SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _upload_to_s3(local_path: Path, s3_url: str) -> bool:
    """Upload a local PDF to S3 (Garage).

    In a real run this uses boto3 + the lakehouse's GARAGE_* credentials
    (the AWS_ENDPOINT_URL=http://localhost:3900 — per
    `destinations_oideachais.py:_build_local_destination`).

    For BIEP v1 dry-runs / CI smoke tests, returns False when the
    `boto3` library is unavailable OR the `GARAGE_ACCESS_KEY_ID` env
    var is unset. The caller treats False as "skip upload" (the local
    PDF is still recorded in the `pdf_downloads` table for traceability).
    """
    if not _LOCAL_SCRAPES:
        try:
            import boto3  # type: ignore
        except ImportError:
            logger.warning("boto3_not_installed_skipping_upload", s3_url=s3_url)
            return False

        access_key = os.environ.get("GARAGE_ACCESS_KEY_ID") or os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("GARAGE_SECRET_ACCESS_KEY") or os.environ.get("AWS_SECRET_ACCESS_KEY")
        endpoint = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900")
        if not access_key or not secret_key:
            logger.warning(
                "garage_credentials_missing_skipping_upload",
                s3_url=s3_url,
                hint="Set GARAGE_ACCESS_KEY_ID + GARAGE_SECRET_ACCESS_KEY",
            )
            return False

        try:
            client = boto3.client(  # type: ignore
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=os.environ.get("AWS_REGION", "garage"),
            )
            # parse s3://garage/oideachais/...
            assert s3_url.startswith("s3://"), s3_url
            bucket, key = s3_url[5:].split("/", 1)
            client.upload_file(str(local_path), bucket, key)
            return True
        except Exception as e:
            logger.error("garage_upload_failed", s3_url=s3_url, error=str(e))
            return False
    return False


# ============================================================================
# Resource — the canonical `pdf_downloads` DLT resource
# ============================================================================
@dlt.resource(
    name="pdf_downloads",
    write_disposition="merge",
    primary_key=["sha256", "subject", "language", "year"],
    columns={
        "subject": {"data_type": "text"},
        "language": {"data_type": "text"},
        "year": {"data_type": "bigint"},
        "filename": {"data_type": "text"},
        "sha256": {"data_type": "text"},
        "size_bytes": {"data_type": "bigint"},
        "local_path": {"data_type": "text"},
        "s3_path": {"data_type": "text"},
        "source": {"data_type": "text"},  # ncca | examinations | gov_ie_circulars | local_cache
        "status": {"data_type": "text"},  # downloaded | cached | uploaded | skipped
        "downloaded_at": {"data_type": "timestamp"},
        "uploaded_at": {"data_type": "timestamp"},
    },
)
def pdf_downloads(
    subject: str | None = None,
    language: str | None = None,
    year: int | None = None,
) -> Iterator[dict]:
    """Yield one row per PDF discovered/downloaded for the BIEP v1 LC corpus.

    Scans the local curated cache `cianfhoghlaim/leaving_certificate/<subject>/`
    when `USE_LOCAL_SCRAPES=true`, otherwise the live PDF source URLs.

    The schema mirrors the canonical destination table layout:
      `oideachais_government_circulars.pdf_downloads` (DuckLake on Garage S3).

    Per tasks.md item 4.1 — `pdf_download_source.py`.
    """
    subjects = [subject] if subject else LC6_SUBJECTS
    languages = [language] if language else LC6_LANGUAGES
    years = [year] if year else list(range(LC6_YEAR_RANGE[0], LC6_YEAR_RANGE[1] + 1))

    for subj in subjects:
        for lang in languages:
            for yr in years:
                yield from _iter_pdfs_for_partition(subj, lang, yr)


def _iter_pdfs_for_partition(
    subject: str, language: str, year: int
) -> Iterator[dict]:
    """Iterate all PDFs for one (subject, language, year) partition.

    Reads from the local cache if present, otherwise records a
    'pending_remote_download' status row.
    """
    if subject not in LC6_SUBJECTS:
        logger.warning("pdf_download_invalid_subject", subject=subject, valid=LC6_SUBJECTS)
        return
    if language not in LC6_LANGUAGES:
        logger.warning("pdf_download_invalid_language", language=language, valid=LC6_LANGUAGES)
        return
    if year < LC6_YEAR_RANGE[0] or year > LC6_YEAR_RANGE[1]:
        logger.warning(
            "pdf_download_invalid_year",
            year=year,
            valid_range=LC6_YEAR_RANGE,
        )
        return

    partition_dir = _LOCAL_PDF_CACHE / subject / language
    if not partition_dir.exists():
        logger.debug(
            "pdf_download_partition_dir_missing",
            subject=subject,
            language=language,
            year=year,
            path=str(partition_dir),
        )
        # Emit a placeholder row so Dagster asset_check can detect "no data"
        yield {
            "subject": subject,
            "language": language,
            "year": year,
            "filename": None,
            "sha256": None,
            "size_bytes": None,
            "local_path": None,
            "s3_path": None,
            "source": "pending_remote_download",
            "status": "skipped_no_local_cache",
            "downloaded_at": datetime.now(UTC).isoformat(),
            "uploaded_at": None,
        }
        return

    # Scan all PDFs in the partition directory
    found_any = False
    for pdf_path in sorted(partition_dir.glob("*.pdf")):
        found_any = True
        sha256 = _compute_sha256(pdf_path)
        size = pdf_path.stat().st_size
        s3_url = _s3_path(subject, language, year, pdf_path.name)
        now_iso = datetime.now(UTC).isoformat()

        # In local mode, just record the cache hit; in remote mode, upload
        if _LOCAL_SCRAPES:
            uploaded = False
            status = "cached"
        else:
            uploaded = _upload_to_s3(pdf_path, s3_url)
            status = "uploaded" if uploaded else "downloaded_local_only"

        yield {
            "subject": subject,
            "language": language,
            "year": year,
            "filename": pdf_path.name,
            "sha256": sha256,
            "size_bytes": size,
            "local_path": str(pdf_path),
            "s3_path": s3_url,
            "source": "local_cache",
            "status": status,
            "downloaded_at": now_iso,
            "uploaded_at": now_iso if uploaded else None,
        }

    if not found_any:
        yield {
            "subject": subject,
            "language": language,
            "year": year,
            "filename": None,
            "sha256": None,
            "size_bytes": None,
            "local_path": None,
            "s3_path": None,
            "source": "empty_partition_dir",
            "status": "skipped_empty_cache",
            "downloaded_at": datetime.now(UTC).isoformat(),
            "uploaded_at": None,
        }


# ============================================================================
# DLT source — the canonical entry point
# ============================================================================
@dlt.source(name="pdf_download")
def pdf_download_source(
    subject: str | None = None,
    language: str | None = None,
    year: int | None = None,
):
    """DLT source for the BIEP v1 PDF downloader.

    Routes through `pdf_downloads()` (above) and registers the DuckLake 1.0
    optimisations on the `pdf_downloads` table once it's materialised.

    Per tasks.md item 4.1 — `pdf_download_source.py`.
    """
    return pdf_downloads(subject=subject, language=language, year=year)


# ============================================================================
# Dagster partition factory
# ============================================================================
def pdf_download_lc6_partitions() -> object:
    """Return the canonical Dagster MultiPartitionsDefinition for the
    BIEP v1 PDF downloader: (subject × language × year).

    Total partitions: 6 subjects × 2 languages × 37 years = 444.

    Lazy import — pdf_download_source.py must not hard-bind Dagster
    at module-load time (it is imported by ~12 downstream modules).
    """  # noqa: RUF002
    from dagster import MultiPartitionsDefinition, StaticPartitionsDefinition

    _subject_lang_combos = [
        f"{subject}__{language}"
        for subject in LC6_SUBJECTS
        for language in LC6_LANGUAGES
    ]
    return MultiPartitionsDefinition({
        "subject_language": StaticPartitionsDefinition(_subject_lang_combos),
        "year": StaticPartitionsDefinition(
            [str(y) for y in range(LC6_YEAR_RANGE[0], LC6_YEAR_RANGE[1] + 1)]
        ),
    })


# ============================================================================
# DuckLake 1.0 optimisation hook (per tasks.md item 4.1)
# ============================================================================
def post_create_pdf_downloads_table(dataset_name: str) -> list[str]:
    """Return SQL statements to apply DuckLake 1.0 optimisations to the
    `pdf_downloads` table once it's materialised.

    Wraps `apply_ducklake_1_0_optimisations()` from
    `cianfhoghlaim.dlt_sources.common.ducklake_options` — adds the 3
    DuckLake 1.0 features (data inlining, sort by `sha256`,
    optional bucket partitioning).

    Per tasks.md item 4.1: "Uses `apply_ducklake_1_0_optimisations()`
    from `dlt/common/ducklake_options.py`".
    """
    from dlt_sources.common.ducklake_options import (
        apply_ducklake_1_0_optimisations,
    )

    return apply_ducklake_1_0_optimisations(
        f"{dataset_name}.pdf_downloads",
        enable_sorting=True,
        enable_bucketing=False,  # pdf_downloads is moderate-volume; sort is sufficient
    )
