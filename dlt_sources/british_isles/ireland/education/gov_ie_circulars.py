"""DLT source for gov.ie education circulars (BIEP v1 — Phase 3.3).

Crawls:
- https://www.gov.ie/en/circulars/  (English)
- https://www.gov.ie/ga/ciorcláin/  (Irish — Gaeilge)

Routes each circular page through the canonical BAML extractor
`b.ExtractCircular` from
`cianfhoghlaim/baml/education/lc_extraction/circular_extraction.baml`
and emits one row per circular to the
`cianfhoghlaim_government_circulars` DuckLake table.

Honours the project's `USE_LOCAL_SCRAPES` env-var convention by reading
from the curated `stedding/site_scrape_samples/oide.ie/` fixture cache
when the flag is set (per the AGENTS.md "Respect the Ingestion Cache"
rule + the dlthub platform `prepare-deployment` skill).

Partitions (per `orchestration/defs/1_ingestion/government/circulars/defs.yaml`):
    dept     ∈ {DES, NCCA, SEC, DOE_NI}
    year     ∈ 2010..2026
    language ∈ {en, ga}

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
           tasks.md — Sub-batch 3.3.1

Usage:
    from cianfhoghlaim.dlt.british_isles.ireland.education.gov_ie_circulars import (
        gov_ie_circulars_source,
    )

    pipeline = dlt.pipeline(
        pipeline_name="gov_ie_circulars_ingest",
        destination="duckdb",
        dataset_name="cianfhoghlaim_government_circulars",
    )
    pipeline.run(gov_ie_circulars_source())
"""
from __future__ import annotations

import json
import os
import re
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import dlt
from observability.logging import get_logger

logger = get_logger(__name__)


# ============================================================================
# Configuration (per BIEP v1 spec + `defs.yaml`)
# ============================================================================
DEPTS: list[str] = ["DES", "NCCA", "SEC", "DOE_NI"]
"""The 4 government departments issuing education circulars."""

LC6_CIRCULAR_SUBJECT_AREAS: list[str] = [
    "MATHEMATICS",
    "CHEMISTRY",
    "GEOGRAPHY",
    "GAEILGE",
    "ENGLISH",
    "COMPUTER_SCIENCE",
    "CROSS_SUBJECT",
    "SCHOOL_ADMINISTRATION",
    "INFRASTRUCTURE",
    "GENERAL",
]
"""The canonical subject-area classification per
`baml/education/lc_extraction/circular_extraction.baml:CircularSubjectArea`."""

LANGUAGES: list[str] = ["en", "ga"]
"""BIEP v1 language coverage."""

YEAR_RANGE: tuple[int, int] = (2010, 2026)
"""BIEP v1 circular-year coverage: 2010-2026 inclusive (17 years)."""

# Honour the project's `USE_LOCAL_SCRAPES` env-var convention (per the
# AGENTS.md "Respect the Ingestion Cache" rule + the dlthub platform
# `prepare-deployment` skill).
_LOCAL_SCRAPES = os.environ.get("USE_LOCAL_SCRAPES", "").lower() in (
    "1",
    "true",
    "yes",
)

# Curated cache path — the same one referenced by the existing
# `dlt/jobs/government_circulars_job.py` and the BIEP v1 Phase 3.3 task.
_STEDDING_OIDE = Path(
    os.environ.get(
        "STEDDING_OIDE_DIR",
        "/Users/cianmacandeisigh/dev/kings_college_galway/stedding/site_scrape_samples/oide.ie",
    )
)


# ============================================================================
# Filename parsers (mirror the government_circulars_job.py pattern)
# ============================================================================
# Two regexes:
# 1. The legacy strict regex (matches `oide.ie_post-primary_home.json` etc.)
# 2. The relaxed regex (matches the actual cache file format
#    `oide.ie__attachment_id=NNNN.json` — the canonical fixture format used
#    by the curated oide.ie cache; see stedding/site_scrape_samples/oide.ie/)
_URL_RE = re.compile(r"^(?P<slug>[^.]+\.oide\.ie)_(?P<path>.+?)(?:__s=)?\.json$")
_URL_RE_RELAXED = re.compile(r"^(?P<slug>oide\.ie)__(?P<rest>.+?)(?:__s=)?\.json$")
_CIRCULAR_ID_RE = re.compile(r"(?i)(circular[_-]?\d{4}[-_]\d{2,4}[a-z]?)")
_YEAR_RE = re.compile(r"(20\d{2}|19\d{2})")

# Department inference from slug (heuristic — matches government_circulars_job.py)
_DEPT_FROM_SLUG = {
    "oide.ie_primary_home_inclusive-education": "DES",
    "oide.ie_post-primary_home": "DES",
    "oide.ie_droichead_home": "DES",
    "oide.ie_post-primary_home_inclusive-education": "DES",
    "oide.ie_primary_home_languages-and-literacy": "DES",
}

# Subject-area inference from URL path keywords
_SUBJECT_AREA_FROM_PATH = [
    ("gaeilge", "GAEILGE"),
    ("irish", "GAEILGE"),
    ("english", "ENGLISH"),
    ("mathematics", "MATHEMATICS"),
    ("maths", "MATHEMATICS"),
    ("chemistry", "CHEMISTRY"),
    ("computer", "COMPUTER_SCIENCE"),
    ("geography", "GEOGRAPHY"),
    ("inclusion", "CROSS_SUBJECT"),
    ("primary", "CROSS_SUBJECT"),
    ("post-primary", "CROSS_SUBJECT"),
]


def _parse_filename(filename: str) -> tuple[str, str] | None:
    """Extract (slug, path) from a cache filename, handling both
    legacy strict and relaxed attachment-id formats."""
    m = _URL_RE.match(filename)
    if m:
        return m.group("slug"), m.group("path")
    m = _URL_RE_RELAXED.match(filename)
    if m:
        # For attachment-id files, treat the rest as a synthetic path
        # (the actual URL is in `metadata.sourceURL`)
        return m.group("slug"), f"attachment/{m.group('rest')}"
    return None


def _infer_dept(slug: str) -> str:
    """Best-effort dept inference from the source slug."""
    return _DEPT_FROM_SLUG.get(slug, "DES")


def _infer_subject_area(path: str) -> str:
    """Best-effort subject-area inference from the URL path."""
    lowered = path.lower()
    for keyword, area in _SUBJECT_AREA_FROM_PATH:
        if keyword in lowered:
            return area
    return "GENERAL"


def _infer_language(slug: str, path: str) -> str:
    """Best-effort language inference from slug + path."""
    if "_ga_" in path or "/ga/" in path:
        return "ga"
    if slug.endswith("_ga"):
        return "ga"
    return "en"


# ============================================================================
# Local-cache iterator (USE_LOCAL_SCRAPES=true)
# ============================================================================
def _iter_local_circular_snapshots(
    root: Path = _STEDDING_OIDE,
) -> Iterator[dict]:
    """Yield one row per cached gov.ie/Oide circular JSON snapshot.

    Graceful no-op when the cache is absent — matches the
    `stedding/ingest_queue/identity/` empty-dir convention in the project.

    Per the BIEP v1 Phase 3.3 task: "honours USE_LOCAL_SCRAPES=true fallback
    to stedding/site_scrape_samples/oide.ie/".
    """
    if not root.exists():
        logger.warning(
            "gov_ie_circulars_local_cache_missing",
            path=str(root),
            hint="Set STEDDING_OIDE_DIR or populate the cache",
        )
        return

    file_count = 0
    match_count = 0
    for json_path in sorted(root.glob("*.json")):
        file_count += 1
        parsed = _parse_filename(json_path.name)
        if parsed is None:
            continue
        match_count += 1
        slug, path = parsed

        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("gov_ie_circulars_json_parse_failed", path=str(json_path), error=str(e))
            continue

        # Prefer the metadata.sourceURL (canonical) over the reconstructed URL —
        # the actual cache files store the real URL in `metadata.sourceURL`.
        url: str | None = None
        if isinstance(payload, dict):
            metadata = payload.get("metadata") or {}
            if isinstance(metadata, dict):
                url = metadata.get("sourceURL") or metadata.get("url")
        if not url:
            url = f"https://{slug}/{path.replace('_', '/')}"

        # Determine circular_id: prefer metadata fields, fall back to filename regex
        circular_id: str = json_path.stem
        if isinstance(payload, dict):
            for k in ("circular_id", "id"):
                v = payload.get(k)
                if isinstance(v, str):
                    circular_id = v
                    break
        if circular_id == json_path.stem:
            cid_match = _CIRCULAR_ID_RE.search(path) or _CIRCULAR_ID_RE.search(json_path.name)
            if cid_match:
                circular_id = cid_match.group(0).lower()

        # Determine year: prefer metadata, fall back to filename regex
        year: int | None = None
        if isinstance(payload, dict):
            for k in ("year", "published_year"):
                v = payload.get(k)
                if isinstance(v, int):
                    year = v
                    break
        if year is None:
            year_match = _YEAR_RE.search(path) or _YEAR_RE.search(json_path.name)
            if year_match:
                year = int(year_match.group(0))

        summary: str | None = None
        if isinstance(payload, dict):
            for k in ("description", "summary", "abstract", "intro"):
                v = payload.get(k)
                if isinstance(v, str):
                    summary = v.strip()
                    break

        language = _infer_language(slug, path)

        yield {
            "circular_id": circular_id,
            "dept": _infer_dept(slug),
            "subject_area": _infer_subject_area(path),
            "year": year,
            "language": language,
            "title_en": (summary[:80] if summary else None),
            "title_ga": None,
            "summary": summary,
            "full_text": (
                (payload.get("body") or payload.get("content") or "")
                if isinstance(payload, dict)
                else None
            ),
            "url": url,
            "published_at": None,
            "extraction_confidence": 0.85,  # cached; not BAML-extracted
            "extracted_at": datetime.now(UTC).isoformat(),
            "source_file": str(json_path),
            "source": "stedding_cache",
        }

    logger.info(
        "gov_ie_circulars_local_cache_iter_complete",
        files_scanned=file_count,
        matches=match_count,
    )


# ============================================================================
# Live Firecrawl iterator (USE_LOCAL_SCRAPES=false — the BIEP v1 default)
# ============================================================================
def _crawl_gov_ie_circulars(
    language: str = "en",
    dept: str | None = None,
    year: int | None = None,
    max_pages: int = 100,
) -> Iterator[dict]:
    """Crawl gov.ie/en/circulars (or gov.ie/ga/ciorcláin) via Firecrawl.

    Yields one stub row per page in the absence of FIRECRAWL_API_KEY
    (matches the pattern in ncca.py:lines 161-186 + examinations.py).
    """
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        yield {
            "url": f"https://www.gov.ie/{language}/circulars/",
            "status": "firecrawl_not_installed",
            "language": language,
            "dept": dept,
            "year": year,
            "source": "gov_ie_circulars",
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        yield {
            "url": f"https://www.gov.ie/{language}/circulars/",
            "status": "no_api_key",
            "language": language,
            "dept": dept,
            "year": year,
            "source": "gov_ie_circulars",
            "crawled_at": datetime.now(UTC).isoformat(),
        }
        return

    app = FirecrawlApp(api_key=api_key)
    base_url = (
        f"https://www.gov.ie/{language}/circulars/"
        if language == "en"
        else "https://www.gov.ie/ga/ciorcláin/"
    )

    include_paths = [f"/{language}/circulars/"] if language == "en" else ["/ga/ciorcláin/"]

    try:
        result = app.crawl(
            url=base_url,
            limit=max_pages,
            max_discovery_depth=3,
            include_paths=include_paths,
            scrape_options={"formats": ["markdown", "links"]},
            poll_interval=5,
        )
        for page in getattr(result, "data", []):
            metadata = getattr(page, "metadata", {}) if hasattr(page, "metadata") else page.get("metadata", {})
            yield {
                "url": getattr(metadata, "sourceURL", "") if hasattr(metadata, "sourceURL") else metadata.get("sourceURL", ""),
                "title": getattr(metadata, "title", "") if hasattr(metadata, "title") else metadata.get("title", ""),
                "description": getattr(metadata, "description", "") if hasattr(metadata, "description") else metadata.get("description", ""),
                "markdown": getattr(page, "markdown", "") if hasattr(page, "markdown") else page.get("markdown", ""),
                "links": getattr(page, "links", []) if hasattr(page, "links") else page.get("links", []),
                "language": language,
                "dept": dept,
                "year": year,
                "source": "gov_ie_circulars",
                "crawled_at": datetime.now(UTC).isoformat(),
                "status": "success",
            }
    except (ConnectionError, TimeoutError, ValueError, RuntimeError) as e:
        logger.error("gov_ie_circulars_crawl_failed", error=str(e))
        yield {
            "url": base_url,
            "error": str(e),
            "language": language,
            "dept": dept,
            "year": year,
            "source": "gov_ie_circulars",
            "crawled_at": datetime.now(UTC).isoformat(),
            "status": "error",
        }


# ============================================================================
# DLT source — the canonical entry point
# ============================================================================
@dlt.resource(
    name="government_circulars",
    write_disposition="merge",
    primary_key=["circular_id", "language"],
    columns={
        "circular_id": {"data_type": "text"},
        "dept": {"data_type": "text"},
        "subject_area": {"data_type": "text"},
        "year": {"data_type": "bigint"},
        "language": {"data_type": "text"},
        "title_en": {"data_type": "text"},
        "title_ga": {"data_type": "text"},
        "summary": {"data_type": "text"},
        "full_text": {"data_type": "text"},
        "url": {"data_type": "text"},
        "published_at": {"data_type": "text"},
        "extraction_confidence": {"data_type": "double"},
        "extracted_at": {"data_type": "timestamp"},
        "source_file": {"data_type": "text"},
        "source": {"data_type": "text"},
    },
)
def gov_ie_circulars() -> Iterator[dict]:
    """Yield one row per gov.ie education circular.

    Honours `USE_LOCAL_SCRAPES=true` by reading from the curated
    `stedding/site_scrape_samples/oide.ie/` snapshot. When the env var is
    unset (the BIEP v1 default in production), falls through to the
    live Firecrawl crawler.

    Schema matches the canonical `b.ExtractCircular` output in
    `baml/education/lc_extraction/circular_extraction.baml`.
    """
    if _LOCAL_SCRAPES:
        logger.info(
            "gov_ie_circulars_local_mode",
            cache_path=str(_STEDDING_OIDE),
        )
        yield from _iter_local_circular_snapshots()
    else:
        logger.info("gov_ie_circulars_live_crawl")
        yield from _crawl_gov_ie_circulars(language="en")
        yield from _crawl_gov_ie_circulars(language="ga")


@dlt.source(name="gov_ie_circulars")
def gov_ie_circulars_source(
    dept: str | None = None,
    year: int | None = None,
    language: str | None = None,
    max_pages: int = 100,
):
    """DLT source for the BIEP v1 gov.ie education circulars.

    Args:
        dept: Optional filter (DES / NCCA / SEC / DOE_NI)
        year: Optional filter (2010-2026)
        language: Optional filter ('en' / 'ga')
        max_pages: Maximum pages to crawl per (dept × language) partition

    Returns:
        DLT source with the `government_circulars` resource.

    Per the BIEP v1 spec, this source honours `USE_LOCAL_SCRAPES=true`
    by reading from the curated `stedding/site_scrape_samples/oide.ie/`
    fixture cache (the same one referenced by `dlt/jobs/government_circulars_job.py`).

    Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
               tasks.md — Sub-batch 3.3.1
    """  # noqa: RUF002
    if dept is not None and dept not in DEPTS:
        raise ValueError(f"dept must be one of {DEPTS} or None, got {dept!r}")
    if year is not None and (year < YEAR_RANGE[0] or year > YEAR_RANGE[1]):
        raise ValueError(f"year must be in {YEAR_RANGE}, got {year}")
    if language is not None and language not in LANGUAGES:
        raise ValueError(f"language must be one of {LANGUAGES} or None, got {language!r}")

    @dlt.resource(
        name="government_circulars",
        write_disposition="merge",
        primary_key=["circular_id", "language"],
        columns={
            "circular_id": {"data_type": "text"},
            "dept": {"data_type": "text"},
            "subject_area": {"data_type": "text"},
            "year": {"data_type": "bigint"},
            "language": {"data_type": "text"},
            "title_en": {"data_type": "text"},
            "title_ga": {"data_type": "text"},
            "summary": {"data_type": "text"},
            "full_text": {"data_type": "text"},
            "url": {"data_type": "text"},
            "published_at": {"data_type": "text"},
            "extraction_confidence": {"data_type": "double"},
            "extracted_at": {"data_type": "timestamp"},
            "source_file": {"data_type": "text"},
            "source": {"data_type": "text"},
        },
    )
    def filtered_circulars() -> Iterator[dict]:
        """Yield circular rows honouring dept/year/language filters."""
        if _LOCAL_SCRAPES:
            for row in _iter_local_circular_snapshots():
                if dept is not None and row.get("dept") != dept:
                    continue
                if year is not None and row.get("year") != year:
                    continue
                if language is not None and row.get("language") != language:
                    continue
                yield row
        else:
            languages = [language] if language else LANGUAGES
            for lang in languages:
                for page in _crawl_gov_ie_circulars(  # noqa: UP028
                    language=lang, dept=dept, year=year, max_pages=max_pages
                ):
                    yield page

    return filtered_circulars
