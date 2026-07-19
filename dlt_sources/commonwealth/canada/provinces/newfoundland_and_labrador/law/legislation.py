"""DLT source for the Newfoundland and Labrador Legislation.

Per the
[`2026-07-12-canada-provinces-quebec-montreal-pipeline-v1`](../../../openspec/changes/2026-07-12-canada-provinces-quebec-montreal-pipeline-v1/)
change.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/can/nl/law/<lang>/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
import structlog

logger = structlog.get_logger(__name__)


PROVINCE = "nl"
DOMAIN = "law"
SLUG = "legislation"
CANONICAL_URL = "https://www.assembly.nl.ca/legislation"
DEFAULT_LANGUAGE = "en"


@dlt.resource(
    name="nl_legislation",
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
def nl_legislation(language=None):
    """Yield Newfoundland and Labrador Legislation rows from the canonical cache."""
    import hashlib
    import json
    from datetime import UTC, datetime
    from pathlib import Path

    cache_dir = Path("stedding/ingest_queue/commonwealth/can/nl/law")
    languages = (language,) if language else ('en',)
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("nl_legislation_cache_parse_failed", path=str(json_path), error=str(exc))
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


@dlt.source(name="nl_legislation")
def nl_legislation_source(language=None):
    """DLT source for the Newfoundland and Labrador Legislation ingestion."""
    return nl_legislation(language=language)


__all__ = [
    "CANONICAL_URL",
    "DEFAULT_LANGUAGE",
    "DOMAIN",
    "PROVINCE",
    "SLUG",
    "nl_legislation",
    "nl_legislation_source",
]
