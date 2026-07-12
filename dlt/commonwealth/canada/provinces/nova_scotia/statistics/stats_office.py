"""DLT source for the Nova Scotia Statistics Office.

Per the
[`2026-07-12-canada-provinces-quebec-montreal-pipeline-v1`](../../../openspec/changes/2026-07-12-canada-provinces-quebec-montreal-pipeline-v1/)
change.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/can/ns/statistics/<lang>/``.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


PROVINCE = "ns"
DOMAIN = "statistics"
SLUG = "stats_office"
CANONICAL_URL = "https://novascotia.ca/finance"
DEFAULT_LANGUAGE = "en"


@dlt.resource(
    name="ns_stats_office",
    write_disposition="merge",
    primary_key=["url", "language"],
    columns={
        "province": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "language": {"data_type": "text"},
        "url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "source": {"data_type": "text"},
        "extracted_at": {"data_type": "timestamp"},
    },
)
def ns_stats_office(language=None):
    """Yield Nova Scotia Statistics Office rows from the canonical cache."""
    import hashlib
    import json
    from datetime import UTC, datetime
    from pathlib import Path

    cache_dir = Path("stedding/ingest_queue/commonwealth/can/ns/statistics")
    languages = (language,) if language else ('en',)
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("ns_stats_office_cache_parse_failed", path=str(json_path), error=str(exc))
                continue
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {
                "province": PROVINCE,
                "domain": DOMAIN,
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": (payload.get("title") or metadata.get("title", "") if isinstance(payload, dict) else ""),
                "content_hash": f"sha256:{hashlib.sha256(markdown.encode()).hexdigest()[:16]}" if markdown else "",
                "source": SLUG,
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="ns_stats_office")
def ns_stats_office_source(language=None):
    """DLT source for the Nova Scotia Statistics Office ingestion."""
    return ns_stats_office(language=language)


__all__ = [
    "CANONICAL_URL",
    "DEFAULT_LANGUAGE",
    "DOMAIN",
    "PROVINCE",
    "SLUG",
    "ns_stats_office",
    "ns_stats_office_source",
]
