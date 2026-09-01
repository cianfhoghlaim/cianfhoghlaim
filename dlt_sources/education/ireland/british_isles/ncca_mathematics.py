"""
DLT source for the Mathematics NCCA syllabus — BIEP v1 per-subject ingestion.

Per the british-isles-education-pipeline (BIEP) v1 spec, the 6
LC priority subjects (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) each have a per-subject
NCCA syllabus crawl source. This file is the Mathematics
variant. It is a focused single-subject crawler that yields
one `<subject>_syllabus` resource per page on ncca.ie, with
`USE_LOCAL_SCRAPES=true` honouring the
`stedding/ingest_queue/ncca/mathematics/` fallback cache.

The canonical BIEP v1 pattern (per `9e97ca0ca`):
- `@dlt.resource(name="mathematics_syllabus", write_disposition="merge", primary_key=["url"])`
- Uses the `named_destinations` factory (the `ducklake_cianfhoghlaim`
  named destination)
- Honours `USE_LOCAL_SCRAPES=true` to read from the local cache
- Uses the `default` BAML client (minimax-m3 per `667635dfd`)

Usage:

    from dlt_sources.education.ireland.british_isles.education.ncca_mathematics import (
        ncca_mathematics_source,
        ncca_mathematics_partitions,
    )

    # Local dev (reads from stedding/ingest_queue/ncca/mathematics/)
    os.environ["USE_LOCAL_SCRAPES"] = "true"
    pipeline.run(ncca_mathematics_source(language="en"))

    # Production (the warehouse named destination)
    pipeline.run(ncca_mathematics_source(language="en"))

Reference: openspec/changes/2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1/
"""
from __future__ import annotations
import dlt


import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dlt_sources.common.destinations import named_destinations

import dlt_sources

# Canonical BIEP v1 ingest queue (the curated local cache)
REPO_ROOT = Path(__file__).resolve().parents[5]
INGEST_QUEUE = REPO_ROOT / "stedding" / "ingest_queue" / "ncca" / "mathematics"

# The 6 BIEP v1 LC languages (English + Irish)
LC_LANGUAGES: list[str] = ["en", "ga"]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _iter_local_cache(language: str) -> Iterator[dict[str, Any]]:
    """Yield cached Mathematics pages from the local ingest queue.

    Honour `USE_LOCAL_SCRAPES=true` by reading from
    `stedding/ingest_queue/ncca/mathematics/<lang>/`.
    """
    cache_dir = INGEST_QUEUE / language
    if not cache_dir.exists():
        return
    for path in sorted(cache_dir.glob("*.json")):
        try:
            payload = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        yield {
            "url": payload.get("url", str(path)),
            "title": payload.get("title", ""),
            "description": payload.get("description", ""),
            "markdown": payload.get("markdown", ""),
            "language": language,
            "subject": "mathematics",
            "source": "ncca",
            "crawled_at": payload.get("crawled_at", _now_iso()),
            "status": "cached",
        }


def _iter_live_crawl(language: str, max_pages: int) -> Iterator[dict[str, Any]]:
    """Crawl ncca.ie/en/senior-cycle/mathematics live via Firecrawl.

    Only invoked when `USE_LOCAL_SCRAPES` is not set; gracefully
    degrades to a single placeholder row when Firecrawl is not
    installed / not configured.
    """
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        yield {
            "url": "https://ncca.ie",
            "title": "Mathematics (NCCA — Firecrawl not installed)",
            "language": language,
            "subject": "mathematics",
            "source": "ncca",
            "crawled_at": _now_iso(),
            "status": "firecrawl_not_installed",
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        yield {
            "url": "https://ncca.ie",
            "title": "Mathematics (NCCA — FIRECRAWL_API_KEY missing)",
            "language": language,
            "subject": "mathematics",
            "source": "ncca",
            "crawled_at": _now_iso(),
            "status": "no_api_key",
        }
        return

    app = FirecrawlApp(api_key=api_key)
    base = "https://ncca.ie/ga" if language == "ga" else "https://ncca.ie/en"
    include_paths = [
        f"{base}/senior-cycle/mathematics/*",
        f"{base}/senior-cycle/matamaitic/*" if language == "ga" else f"{base}/senior-cycle/mathematics/*",
    ]
    try:
        result = app.crawl(
            url=base,
            limit=max_pages,
            include_paths=include_paths,
            scrape_options={"formats": ["markdown", "links"]},
            poll_interval=5,
        )
    except Exception as exc:
        yield {
            "url": base,
            "title": f"Mathematics crawl failed: {exc}",
            "language": language,
            "subject": "mathematics",
            "source": "ncca",
            "crawled_at": _now_iso(),
            "status": "crawl_error",
            "error": str(exc),
        }
        return

    for page in getattr(result, "data", []) or []:
        metadata = getattr(page, "metadata", None) or {}
        if hasattr(metadata, "sourceURL"):
            url = getattr(metadata, "sourceURL", "") or ""
            title = getattr(metadata, "title", "") or ""
            description = getattr(metadata, "description", "") or ""
        else:
            url = metadata.get("sourceURL", "") or ""
            title = metadata.get("title", "") or ""
            description = metadata.get("description", "") or ""
        yield {
            "url": url,
            "title": title,
            "description": description,
            "markdown": getattr(page, "markdown", "") or page.get("markdown", ""),
            "language": language,
            "subject": "mathematics",
            "source": "ncca",
            "crawled_at": _now_iso(),
            "status": "success",
        }


@dlt.resource(
    name="mathematics_syllabus",
    write_disposition="merge",
    primary_key=["url"],
    columns={
        "url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "description": {"data_type": "text"},
        "markdown": {"data_type": "text"},
        "language": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "source": {"data_type": "text"},
        "crawled_at": {"data_type": "timestamp"},
        "status": {"data_type": "text"},
    },
)
def mathematics_syllabus_resource(language: str = "en") -> Iterator[dict[str, Any]]:
    """Yield one row per Mathematics NCCA page (EN or GA)."""
    if language not in LC_LANGUAGES:
        raise ValueError(f"language must be one of {LC_LANGUAGES}, got {language!r}")
    use_local = os.getenv("USE_LOCAL_SCRAPES", "false").lower() in {"1", "true", "yes"}
    if use_local:
        yield from _iter_local_cache(language)
    else:
        yield from _iter_live_crawl(language, max_pages=100)


@dlt.source(name="ncca_mathematics_lc6")
def ncca_mathematics_source(language: str = "en") -> Any:
    """The canonical BIEP v1 Mathematics NCCA source."""
    return mathematics_syllabus_resource(language=language)


def ncca_mathematics_partitions() -> Any:
    """Return the canonical Dagster MultiPartitionsDefinition for the
    Mathematics NCCA crawl: (mathematics) x (en + ga) = 2 partitions.

    Lazy import to avoid hard-binding DLT to Dagster at module-load time.
    """
    from dagster import MultiPartitionsDefinition, StaticPartitionsDefinition

    return MultiPartitionsDefinition({
        "subject": StaticPartitionsDefinition(["mathematics"]),
        "language": StaticPartitionsDefinition(LC_LANGUAGES),
    })


__all__ = [
    "INGEST_QUEUE",
    "LC_LANGUAGES",
    "mathematics_syllabus_resource",
    "ncca_mathematics_partitions",
    "ncca_mathematics_source",
]


def create_ncca_mathematics_pipeline(
    pipeline_name: str = "ncca_mathematics_lc6",
    dataset_name: str = "cianfhoghlaim.leaving_cert.mathematics",
) -> Any:
    """Return a configured dlt pipeline for the BIEP v1 mathematics NCCA crawl.

    Honours `USE_LOCAL_SCRAPES=true` and the canonical
    `ducklake_cianfhoghlaim` named destination via the named_destinations factory.
    """
    import dlt_sources as _dlt

    return _dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=named_destinations("ducklake_cianfhoghlaim"),
        dataset_name=dataset_name,
    )


__all__ = [
    "INGEST_QUEUE",
    "LC_LANGUAGES",
    "create_ncca_mathematics_pipeline",
    "mathematics_syllabus_resource",
    "ncca_mathematics_partitions",
    "ncca_mathematics_source",
]
