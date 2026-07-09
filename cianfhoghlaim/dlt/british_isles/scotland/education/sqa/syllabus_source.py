"""
Scotland / SQA — scaffolded cross-nation DLT source.

Reads cached SQA mathematics syllabus snapshots from
``stedding/site_scrape_samples/sqa/en/mathematics/sample.json``
when the cache file exists. Returns 1 row per cache file; 0 rows
otherwise. Honours ``USE_LOCAL_SCRAPES=true`` to skip any future
live network calls.

This is the proof-of-concept scaffold for the cross-nation extension
documented in ``docs/agents/cross-nation-content-audit.md`` and the
ADDED Requirements in
``openspec/changes/2026-07-09-cross-nation-content-audit-v1/``.

Production v2 wiring will replace the cache-only read path with a
Firecrawl-crawl of the SQA National Qualifications finder
(``https://www.sqa.org.uk/sqa/56983.html``), the BAML
``ExtractCurriculumSpec`` function, and the partition pattern
``MultiPartitionsDefinition(cycle=["national_5", "higher", "advanced_higher"], subject, language)``.

Usage:
    from cianfhoghlaim.dlt.british_isles.scotland.education.sqa.syllabus_source import (
        sqa_syllabus_source,
    )
    pipeline = dlt.pipeline(
        pipeline_name="biep_sqa_smoke",
        destination=dlt.destinations.duckdb("data/sqa.duckdb"),
    )
    pipeline.run(sqa_syllabus_source())
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt

CACHE_DIR = Path("stedding/site_scrape_samples/sqa")


def _cache_path(language: str, subject: str) -> Path:
    """Return the canonical cache file path for a (language, subject) pair."""
    return CACHE_DIR / language / subject / "sample.json"


def _read_cache(cache_path: Path) -> dict[str, Any] | None:
    """Read a single cache file; return the parsed JSON or None if missing.

    The fixture shape matches the Firecrawl ``/scrape`` v2 response:
    a top-level ``markdown`` field plus a ``metadata`` sub-dict with
    ``sourceURL`` / ``statusCode`` / ``proxyUsed`` / ``cacheState`` /
    ``creditsUsed``. See
    ``stedding/site_scrape_samples/curriculumonline.ie/`` for the
    canonical shape.
    """
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
def sqa_mathematics_syllabus(
    language: str = "en",
    subject: str = "mathematics",
) -> Iterator[dict[str, Any]]:
    """Yield 1 row per cached SQA syllabus snapshot for ``subject`` in ``language``.

    Args:
        language: "en" (English) or "gd" (Scots Gaelic / Gàidhlig).
        subject: BIEP subject slug (default "mathematics" — the only
            subject common to all 5 nations at every level).

    Yields:
        DLT row dicts keyed by ``url`` (the cache file's ``sourceURL``).
    """
    cache = _read_cache(_cache_path(language, subject))
    if cache is None:
        # Honour USE_LOCAL_SCRAPES=true to skip live network calls.
        if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() in ("1", "true", "yes"):
            return
        # Live crawl path is intentionally NOT implemented in this
        # scaffold; the v2 change wires the Firecrawl crawl.
        return

    metadata = cache.get("metadata", {})
    url = metadata.get("sourceURL") or metadata.get("url") or ""
    title = cache.get("title") or cache.get("metadata", {}).get("title") or ""
    markdown = cache.get("markdown") or ""
    content_hash = f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}" if markdown else ""

    yield {
        "url": url,
        "nation": "scotland",
        "exam_board": "sqa",
        "qualification_level": "national_5",
        "language": language,
        "subject": subject,
        "filename": cache_path(language, subject).name,
        "document_type": "syllabus",
        "title": title,
        "content_hash": content_hash,
        "scraped_at": datetime.now(UTC).isoformat(),
    }


def cache_path(language: str, subject: str) -> Path:
    """Public alias for ``_cache_path`` — used by smoke tests."""
    return _cache_path(language, subject)


@dlt.source(name="sqa_syllabus")
def sqa_syllabus_source(
    language: str = "en",
    subject: str = "mathematics",
):
    """DLT source for the SQA scaffolded syllabus read."""
    return sqa_mathematics_syllabus(language=language, subject=subject)
