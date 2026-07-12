"""
DLT source for the Computer Science NCCA syllabus — BIEP v1 per-subject ingestion.

Per the british-isles-education-pipeline (BIEP) v1 spec, the 6
LC priority subjects (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) each have a per-subject
NCCA syllabus crawl source. This file is the Computer Science
variant.

Computer Science is a relatively new LC subject (introduced
2020), so the NCCA syllabus corpus is smaller than the other 5
LC subjects.

The canonical BIEP v1 pattern (per `9e97ca0ca`):
- `@dlt.resource(name="computer_science_syllabus", write_disposition="merge", primary_key=["url"])`
- Uses the `named_destinations` factory (the `warehouse` named
  destination)
- Honours `USE_LOCAL_SCRAPES=true` to read from
  `stedding/ingest_queue/ncca/computer_science/`
- Uses the `default` BAML client (minimax-m3 per `667635dfd`)

Usage:

    from cianfhoghlaim.dlt.british_isles.ireland.education.ncca_computer_science import (
        ncca_computer_science_source,
    )

    os.environ["USE_LOCAL_SCRAPES"] = "true"
    pipeline.run(ncca_computer_science_source(language="en"))

Reference: openspec/changes/2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1/
"""
from __future__ import annotations

import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cianfhoghlaim.dlt.common.named_destinations import named_destination

import dlt

REPO_ROOT = Path(__file__).resolve().parents[5]
INGEST_QUEUE = REPO_ROOT / "stedding" / "ingest_queue" / "ncca" / "computer_science"
LC_LANGUAGES: list[str] = ["en", "ga"]


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _iter_local_cache(language: str) -> Iterator[dict[str, Any]]:
    """Yield cached Computer Science pages from the local ingest queue."""
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
            "subject": "computer_science",
            "source": "ncca",
            "crawled_at": payload.get("crawled_at", _now_iso()),
            "status": "cached",
        }


def _iter_live_crawl(language: str, max_pages: int) -> Iterator[dict[str, Any]]:
    """Crawl ncca.ie for the Computer Science LC syllabus."""
    try:
        from firecrawl import FirecrawlApp
    except ImportError:
        yield {
            "url": "https://ncca.ie",
            "title": "Computer Science (NCCA — Firecrawl not installed)",
            "language": language,
            "subject": "computer_science",
            "source": "ncca",
            "crawled_at": _now_iso(),
            "status": "firecrawl_not_installed",
        }
        return

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        yield {
            "url": "https://ncca.ie",
            "title": "Computer Science (NCCA — FIRECRAWL_API_KEY missing)",
            "language": language,
            "subject": "computer_science",
            "source": "ncca",
            "crawled_at": _now_iso(),
            "status": "no_api_key",
        }
        return

    app = FirecrawlApp(api_key=api_key)
    base = "https://ncca.ie/ga" if language == "ga" else "https://ncca.ie/en"
    keyword = "ríomheolaíocht" if language == "ga" else "computer-science"
    include_paths = [f"{base}/senior-cycle/{keyword}/*"]
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
            "title": f"Computer Science crawl failed: {exc}",
            "language": language,
            "subject": "computer_science",
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
            "subject": "computer_science",
            "source": "ncca",
            "crawled_at": _now_iso(),
            "status": "success",
        }


@dlt.resource(
    name="computer_science_syllabus",
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
def computer_science_syllabus_resource(language: str = "en") -> Iterator[dict[str, Any]]:
    """Yield one row per Computer Science NCCA page (EN or GA)."""
    if language not in LC_LANGUAGES:
        raise ValueError(f"language must be one of {LC_LANGUAGES}, got {language!r}")
    use_local = os.getenv("USE_LOCAL_SCRAPES", "false").lower() in {"1", "true", "yes"}
    if use_local:
        yield from _iter_local_cache(language)
    else:
        yield from _iter_live_crawl(language, max_pages=100)


@dlt.source(name="ncca_computer_science_lc6")
def ncca_computer_science_source(language: str = "en") -> Any:
    """The canonical BIEP v1 Computer Science NCCA source."""
    return computer_science_syllabus_resource(language=language)


def ncca_computer_science_partitions() -> Any:
    """Return the canonical Dagster MultiPartitionsDefinition for the
    Computer Science NCCA crawl: (computer_science) x (en + ga) = 2 partitions.

    Lazy import to avoid hard-binding DLT to Dagster at module-load time.
    """
    from dagster import MultiPartitionsDefinition, StaticPartitionsDefinition

    return MultiPartitionsDefinition({
        "subject": StaticPartitionsDefinition(["computer_science"]),
        "language": StaticPartitionsDefinition(LC_LANGUAGES),
    })


__all__ = [
    "INGEST_QUEUE",
    "LC_LANGUAGES",
    "computer_science_syllabus_resource",
    "ncca_computer_science_partitions",
    "ncca_computer_science_source",
]


def create_ncca_computer_science_pipeline(
    pipeline_name: str = "ncca_computer_science_lc6",
    dataset_name: str = "oideachais.leaving_cert.computer_science",
) -> Any:
    """Return a configured dlt pipeline for the BIEP v1 computer_science NCCA crawl.

    Honours `USE_LOCAL_SCRAPES=true` and the canonical
    `warehouse` named destination via the named_destinations factory.
    """
    import dlt as _dlt

    return _dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=named_destination("warehouse"),
        dataset_name=dataset_name,
    )


__all__ = [
    "INGEST_QUEUE",
    "LC_LANGUAGES",
    "computer_science_syllabus_resource",
    "create_ncca_computer_science_pipeline",
    "ncca_computer_science_partitions",
    "ncca_computer_science_source",
]
