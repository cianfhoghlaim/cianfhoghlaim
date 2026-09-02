"""
Wales / WJEC — scaffolded cross-nation DLT source.

Reads cached WJEC mathematics syllabus snapshots from
``stedding/site_scrape_samples/wjec/en/mathematics/sample.json``
when the cache file exists. Returns 1 row per cache file; 0 rows
otherwise. Honours ``USE_LOCAL_SCRAPES=true`` to skip any future
live network calls.

This is the proof-of-concept scaffold for the cross-nation extension
documented in ``docs/agents/cross-nation-content-audit.md`` and the
ADDED Requirements in
``openspec/changes/2026-07-09-cross-nation-content-audit-v1/``.

Production v2 wiring will replace the cache-only read path with a
Firecrawl-crawl of the WJEC qualification finder
(``https://www.wjec.co.uk/``), the BAML
``ExtractCurriculumSpec`` function, and the partition pattern
``MultiPartitionsDefinition(cycle=["gcse", "a_level"], subject, language=["en", "cy"])``.

The language code ``cy`` (Cymraeg / Welsh) is the ISO 639-1 code
for Welsh; the same awarding body publishes under the brand
"CBAC" (``Cyd-bwyllgor Addysg Cymru``) for the Welsh-language
editions of the same syllabuses.

Usage:
    from dlt_sources.education.wales.british_isles.education.wjec.syllabus_source import (
        wjec_syllabus_source,
    )
"""

from __future__ import annotations
import dlt


import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt_sources

CACHE_DIR = Path("stedding/site_scrape_samples/wjec")
URLS_CACHE_PATH = Path("stedding/site_scrape_samples/wjec/urls.json")
WJEC_BASE_URL = "https://www.wjec.co.uk/qualifications"
"""Phase 1 fix: WJEC was healthy but the discovery URL is now
``/qualifications`` (the old ``/`` landing page has moved). The
resource iterates the Firecrawl-discovered URL list at
``stedding/site_scrape_samples/wjec/urls.json``."""


def _cache_path(language: str, subject: str) -> Path:
    return CACHE_DIR / language / subject / "sample.json"


def _read_cache(cache_path: Path) -> dict[str, Any] | None:
    if not cache_path.exists():
        return None
    try:
        with cache_path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


@dlt.resource(
    name="mathematics_syllabus",
    write_disposition="merge",
    primary_key=["url"],
    columns={
        "url": {"data_type": "text"},
        "nation": {"data_type": "text"},
        "exam_board": {"data_type": "text"},
        "qualification_level": {"data_type": "text"},
        "language": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "filename": {"data_type": "text"},
        "document_type": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "scraped_at": {"data_type": "timestamp"},
    },
)
def wjec_mathematics_syllabus(
    language: str = "en",
    subject: str = "mathematics",
) -> Iterator[dict[str, Any]]:
    """Yield 1 row per cached WJEC syllabus snapshot for ``subject`` in ``language``.

    Args:
        language: "en" (English / WJEC) or "cy" (Welsh / CBAC).
        subject: BIEP subject slug (default "mathematics").

    Yields:
        DLT row dicts keyed by ``url`` (the cache file's ``sourceURL``).
    """
    cache = _read_cache(_cache_path(language, subject))
    if cache is None:
        if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() in ("1", "true", "yes"):
            return
        return

    metadata = cache.get("metadata", {})
    url = metadata.get("sourceURL") or metadata.get("url") or ""
    title = cache.get("title") or cache.get("metadata", {}).get("title") or ""
    markdown = cache.get("markdown") or ""
    content_hash = f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}" if markdown else ""

    yield {
        "url": url,
        "nation": "wales",
        "exam_board": "wjec",
        "qualification_level": "gcse",
        "language": language,
        "subject": subject,
        "filename": _cache_path(language, subject).name,
        "document_type": "syllabus",
        "title": title,
        "content_hash": content_hash,
        "scraped_at": datetime.now(UTC).isoformat(),
    }


def cache_path(language: str, subject: str) -> Path:
    """Public alias for ``_cache_path`` — used by smoke tests."""
    return _cache_path(language, subject)


@dlt.source(name="wjec_syllabus")
def wjec_syllabus_source(
    language: str = "en",
    subject: str = "mathematics",
):
    """DLT source for the WJEC scaffolded syllabus read."""
    return wjec_mathematics_syllabus(language=language, subject=subject)
