"""DLT source for Leaving Certificate 2026 (7 priority subjects).

Reads cached PDF metadata from the local scrape cache
(`stedding/ingest_queue/{examinations,ncca,curriculumonline}.ie/`) and yields
structured records per asset:

  leaving_cert.{subject}_syllabus
  leaving_cert.{subject}_past_papers
  leaving_cert.{subject}_marking_schemes
  leaving_cert.{subject}_examiner_reports
  leaving_cert.{subject}_topic_frequency
  leaving_cert.{subject}_syllabus_extracted
  leaving_cert.{subject}_past_papers_extracted
  leaving_cert.{subject}_marking_schemes_extracted
  leaving_cert.{subject}_topic_frequency_computed

Each subject's partition is processed in isolation; the topic_frequency
asset cross-references syllabus topics with past exam question frequency
to drive the portal-page layout (MaterializeResult / Metadata).

This source respects USE_LOCAL_SCRAPES=true (the default in compose.yaml).
When the env var is "false", it would fall back to Firecrawl — but the
local cache is the canonical source for the 7 priority subjects.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


# ── Subject taxonomy ─────────────────────────────────────────────────────────

SUBJECTS: list[str] = [
    "mathematics",
    "irish",
    "biology",
    "french",
    "history",
    "business",
    "construction-studies",
]

# Substring patterns for matching cached files to a subject.
# Each entry is a list of substring tokens (case-insensitive) that
# any one of which must appear in the filename for the file to
# belong to the subject (OR within entry).
#
# Cached filenames use two patterns:
#   1. ..._lc_<subject>_<year>_<paper>_er[_ir].pdf
#      e.g. ..._lc_maths_00_er.pdf, ..._lc_biology_01_er.pdf
#   2. cer_<year>_irish_lc_<actual_subject>_<year>_er_ir.pdf
#      e.g. cer_2001_irish_lc_agri_science_01_er_ir.pdf
#      The "irish_lc_" prefix is a language marker (Irish-language
#      examiner report), not the subject.
#
# We handle both via:
#   - PRIMARY pattern: `_lc_<subject>_<year>` or
#                     `irish_lc_<subject>_<year>`
#   - FALLBACK pattern: bare subject tokens in the filename
SUBJECT_TOKENS: dict[str, list[str]] = {
    "mathematics": ["maths", "mathematics", "math_", "applied_math"],
    "irish": ["gaeilge"],
    "biology": ["biology", "biolog_"],
    "french": ["french"],
    "history": ["history"],
    "business": ["business", "bus_"],
    "construction-studies": ["construct", "construction"],
}

# Map DLT-level table suffix to the asset family in dagster.
TABLE_TO_ASSET: dict[str, str] = {
    "syllabus": "syllabus_pdf",
    "syllabus_extracted": "syllabus_extracted",
    "past_papers": "past_papers",
    "past_papers_extracted": "past_papers_extracted",
    "marking_schemes": "marking_schemes",
    "marking_schemes_extracted": "marking_schemes_extracted",
    "examiner_reports": "examiner_reports",
    "topic_frequency": "topic_frequency",
}

# Cached content types per table suffix (we only ship cache hits for
# syllabus + past_papers + marking_schemes + examiner_reports — the
# other tables are computed from these).
CACHE_SUFFIX_TO_CONTENT_TYPE: dict[str, str] = {
    "syllabus": "syllabus",
    "past_papers": "exam_materials",
    "marking_schemes": "exam_materials",
    "examiner_reports": "examiner_reports",
}


# ── Helpers ────────────────────────────────────────────────────────────────

def _cache_root() -> Path:
    """Local scrape cache root. Override with STEDDING_INGEST_QUEUE."""
    return Path(os.environ.get("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue"))


def _ingest_queue_dir_for(content_type: str) -> Path:
    """Map a content_type to its cache subdir."""
    mapping = {
        "syllabus": "curriculumonline.ie",
        "exam_materials": "examinations.ie",
        "examiner_reports": "examinations.ie",
    }
    return _cache_root() / mapping.get(content_type, "examinations.ie")


def _extract_year(filename: str) -> int | None:
    """Best-effort year extraction from a cached filename."""
    m = re.search(r"(?:cer[_-]?|academic[_-]?)(\d{4})", filename, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return None


def _extract_level(filename: str) -> str:
    """Best-effort level extraction (H/O/F)."""
    fn = filename.lower()
    if "applied_maths" in fn or "foundation" in fn or "ol_" in fn:
        return "F"
    if "_ol_" in fn or "ordinary" in fn:
        return "O"
    if "_hl_" in fn or "higher" in fn:
        return "H"
    return "H&O"


def _normalize_subject_from_filename(filename: str) -> str | None:
    """Return the subject slug if `filename` is about a known subject.

    Handles two patterns:
      1. ..._lc_<subject>_<year>_<paper>...
         e.g. ..._lc_maths_00_er.pdf → subject="mathematics"
      2. ..._irish_lc_<subject>_<year>_<paper>_ir...
         e.g. ..._irish_lc_agri_science_01_er_ir.pdf → subject="agricultural-science"
         (the irish_lc_ prefix is the LANGUAGE marker, not the subject)

    Returns None if the file can't be classified into one of the 7
    priority subjects.
    """
    fn = filename.lower()

    # Pattern 1: ..._irish_lc_<subject>_<year>... → extract the part
    # AFTER "irish_lc_". The actual subject is the next token.
    m = re.search(r"irish_lc_([a-z]+)", fn)
    if m:
        # Map the after-prefix token to one of our 7 subjects
        token = m.group(1)
        token_to_subject = {
            "maths": "mathematics",
            "mathematics": "mathematics",
            "applied_math": "mathematics",
            "biology": "biology",
            "french": "french",
            "history": "history",
            "business": "business",
            "construct": "construction-studies",
            "construction": "construction-studies",
        }
        if token in token_to_subject:
            return token_to_subject[token]

    # Pattern 2: ..._lc_<subject>_<year>... → find the subject
    # after `_lc_` (but not `_irish_lc_` which is handled above)
    m = re.search(r"(?<!irish_)_lc_([a-z_]+?)(?:_\d{2,4}|_er|_exam|_\.pdf)", fn)
    if m:
        token = m.group(1)
        token_to_subject = {
            "maths": "mathematics",
            "mathematics": "mathematics",
            "applied_math": "mathematics",
            "biology": "biology",
            "french": "french",
            "history": "history",
            "business": "business",
            "construct": "construction-studies",
            "construction": "construction-studies",
        }
        if token in token_to_subject:
            return token_to_subject[token]

    # Pattern 3: _ol_<subject> (ordinary level) — alternate
    m = re.search(r"_ol_([a-z_]+)", fn)
    if m:
        token = m.group(1)
        token_to_subject = {
            "maths": "mathematics",
            "mathematics": "mathematics",
            "applied_math": "mathematics",
            "biology": "biology",
            "french": "french",
            "history": "history",
            "business": "business",
            "construct": "construction-studies",
            "construction": "construction-studies",
        }
        if token in token_to_subject:
            return token_to_subject[token]

    # Fallback: SUBJECT_TOKENS OR matching (rare; covers edge cases)
    for subject, tokens in SUBJECT_TOKENS.items():
        if any(token in fn for token in tokens):
            return subject

    return None


def _stable_hash(record: dict[str, Any]) -> str:
    """Content-addressable hash for change detection."""
    return hashlib.sha256(
        json.dumps(record, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()[:16]


def _iter_cached_files(content_type: str) -> Iterator[Path]:
    """Yield cached .pdf.json files for a content_type, descending into nested dirs."""
    root = _ingest_queue_dir_for(content_type)
    if not root.exists():
        return
    for path in root.rglob("*.pdf.json"):
        yield path


# ── Cached-PDF readers ─────────────────────────────────────────────────────

def _read_cached_pdf_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("lc_cache_read_failed", path=str(path), error=str(exc))
        return None


def _yield_syllabus_records() -> Iterator[dict[str, Any]]:
    """Yield syllabus_records from cached curriculumonline.ie PDFs."""
    for path in _iter_cached_files("syllabus"):
        data = _read_cached_pdf_json(path)
        if data is None:
            continue
        subject = _normalize_subject_from_filename(path.name)
        if subject is None:
            continue
        year = _extract_year(path.name) or datetime.now(UTC).year
        level = _extract_level(path.name)
        record = {
            "subject": subject,
            "year": year,
            "level": level,
            "title": data.get("title", path.stem),
            "url": data.get("url", f"file://{path}"),
            "language": "en" if "irish" not in path.name.lower() else "ga",
            "content_hash": _stable_hash(data),
            "source": "curriculumonline.ie",
            "crawled_at": data.get("crawledAt", datetime.now(UTC).isoformat()),
        }
        yield record


def _yield_exam_materials_records() -> Iterator[dict[str, Any]]:
    """Yield past_papers, marking_schemes, and examiner_reports records
    from cached examinations.ie PDFs.

    The cache contains both exam paper PDFs and chief examiner reports.
    We classify each file by its filename tokens:
      - "marking" → marking_schemes
      - "examiner" or "chief_examiner" → examiner_reports
      - default → past_papers
    """
    for path in _iter_cached_files("exam_materials"):
        data = _read_cached_pdf_json(path)
        if data is None:
            continue
        subject = _normalize_subject_from_filename(path.name)
        if subject is None:
            continue
        year = _extract_year(path.name) or datetime.now(UTC).year
        level = _extract_level(path.name)
        fn = path.name.lower()
        if "marking" in fn or "mark" in fn and "scheme" in fn:
            kind = "marking_schemes"
        elif "examiner" in fn or "chief_examiner" in fn or "chief_examines" in fn:
            kind = "examiner_reports"
        elif "irish" in fn or "gaeilge" in fn:
            # Cached Irish-language chief examiner reports have distinct
            # filename markers; treat as examiner_reports too.
            kind = "examiner_reports"
        else:
            kind = "past_papers"
        record = {
            "subject": subject,
            "year": year,
            "level": level,
            "kind": kind,
            "title": data.get("title", path.stem),
            "url": data.get("url", f"file://{path}"),
            "language": "ga" if ("irish" in fn or "gaeilge" in fn) else "en",
            "content_hash": _stable_hash(data),
            "source": "examinations.ie",
            "crawled_at": data.get("crawledAt", datetime.now(UTC).isoformat()),
        }
        yield record


# ── DLT source ──────────────────────────────────────────────────────────────

@dlt.source(name="leaving_cert")
def leaving_cert_source(
    use_local_scrapes: bool | None = None,
    cache_only: bool = True,
):
    """DLT source for the 7 priority Leaving Cert subjects.

    Yields 4 resource groups per subject:
      - syllabus (cached curriculumonline.ie PDFs)
      - past_papers (cached examinations.ie exam papers)
      - marking_schemes (cached examinations.ie marking schemes)
      - examiner_reports (cached examinations.ie chief examiner reports)

    Args:
        use_local_scrapes: when None, reads the env var USE_LOCAL_SCRAPES
            (default true). When false, would fall back to Firecrawl — but
            the local cache is the canonical source for the 7 priority subjects
            so we default to true and don't go to the network.
        cache_only: if true, emit only records that hit the cache. If false,
            emit an empty seed (per-subject existence row) so every subject
            appears in DuckLake even without cached data.
    """
    if use_local_scrapes is None:
        use_local_scrapes = os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"

    if not use_local_scrapes:
        logger.warning(
            "lc_live_firecrawl_disabled",
            reason="live scrape path not implemented; falling back to local cache",
        )

    # Group 1: syllabus
    @dlt.resource(
        name="syllabus",
        write_disposition="merge",
        primary_key=["subject", "year", "level", "language", "content_hash"],
    )
    def syllabus_resource() -> Iterator[dict[str, Any]]:
        rows = list(_yield_syllabus_records())
        logger.info("lc_syllabus_rows", count=len(rows))
        yield from rows
        if cache_only and not rows:
            # Always seed at least one row per subject so the table exists
            for subject in SUBJECTS:
                yield {
                    "subject": subject,
                    "year": datetime.now(UTC).year,
                    "level": "H&O",
                    "title": f"{subject} syllabus (no cache yet)",
                    "url": "",
                    "language": "en",
                    "content_hash": f"empty-{subject}",
                    "source": "seed",
                    "crawled_at": datetime.now(UTC).isoformat(),
                }

    # Group 2: past_papers
    @dlt.resource(
        name="past_papers",
        write_disposition="merge",
        primary_key=["subject", "year", "level", "content_hash"],
    )
    def past_papers_resource() -> Iterator[dict[str, Any]]:
        rows = [r for r in _yield_exam_materials_records() if r["kind"] == "past_papers"]
        logger.info("lc_past_papers_rows", count=len(rows))
        yield from rows

    # Group 3: marking_schemes
    @dlt.resource(
        name="marking_schemes",
        write_disposition="merge",
        primary_key=["subject", "year", "level", "content_hash"],
    )
    def marking_schemes_resource() -> Iterator[dict[str, Any]]:
        rows = [r for r in _yield_exam_materials_records() if r["kind"] == "marking_schemes"]
        logger.info("lc_marking_schemes_rows", count=len(rows))
        yield from rows

    # Group 4: examiner_reports
    @dlt.resource(
        name="examiner_reports",
        write_disposition="merge",
        primary_key=["subject", "year", "level", "content_hash"],
    )
    def examiner_reports_resource() -> Iterator[dict[str, Any]]:
        rows = [r for r in _yield_exam_materials_records() if r["kind"] == "examiner_reports"]
        logger.info("lc_examiner_reports_rows", count=len(rows))
        yield from rows

    return (
        syllabus_resource(),
        past_papers_resource(),
        marking_schemes_resource(),
        examiner_reports_resource(),
    )


# ── Convenience for tests / single-subject runs ───────────────────────────

def iter_subject_records(subject: str) -> Iterator[dict[str, Any]]:
    """Yield all records for one subject across all 4 resources."""
    for path in _iter_cached_files("syllabus"):
        data = _read_cached_pdf_json(path)
        if data is None:
            continue
        if _normalize_subject_from_filename(path.name) != subject:
            continue
        yield {
            "kind": "syllabus",
            "year": _extract_year(path.name),
            "level": _extract_level(path.name),
            "title": data.get("title", path.stem),
        }
    for path in _iter_cached_files("exam_materials"):
        data = _read_cached_pdf_json(path)
        if data is None:
            continue
        if _normalize_subject_from_filename(path.name) != subject:
            continue
        fn = path.name.lower()
        kind = (
            "marking_schemes" if "mark" in fn and "scheme" in fn
            else "examiner_reports" if "examiner" in fn or "chief" in fn
            else "past_papers"
        )
        yield {
            "kind": kind,
            "year": _extract_year(path.name),
            "level": _extract_level(path.name),
            "title": data.get("title", path.stem),
        }
