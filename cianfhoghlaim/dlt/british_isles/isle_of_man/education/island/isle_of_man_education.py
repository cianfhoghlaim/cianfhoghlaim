"""Per-island DLT source for Isle of Man Government.

Phase 2 (BIEP parity) change: the previous
``dlt/british_isles/isle_of_man/education/channel_islands.py`` was a
single shared source. This change splits it into per-island
sources that route through the canonical
``dlt/common/endpoint_recovery`` helper.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/site_scrape_samples/biep/crown/isle_of_man/education/<lang>/``.
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.common.endpoint_recovery import (
    EndpointRecoveryStrategy,
    fetch,
)

logger = structlog.get_logger(__name__)


ISLAND = "isle_of_man"
CANONICAL_URL = "https://www.gov.im/categories/education-training-and-careers/"


@dlt.resource(
    name="isle_of_man_education",
    write_disposition="merge",
    primary_key=["url", "language"],
    columns={
        "island": {"data_type": "text"},
        "language": {"data_type": "text"},
        "url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "source": {"data_type": "text"},
        "extracted_at": {"data_type": "timestamp"},
    },
)
def isle_of_man_education(language=None):
    """Yield Isle of Man Government education rows from the canonical cache."""
    cache_dir = Path("stedding/site_scrape_samples/biep/crown/isle_of_man/education")
    languages = (language,) if language else ('en', 'gv')
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("isle_of_man_cache_parse_failed", path=str(json_path), error=str(exc))
                continue
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {
                "island": ISLAND,
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": (payload.get("title") or metadata.get("title", "") if isinstance(payload, dict) else ""),
                "content_hash": f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}" if markdown else "",
                "source": ISLAND,
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="isle_of_man_education")
def isle_of_man_education_source(language=None):
    """DLT source for the Isle of Man Government ingestion."""
    return isle_of_man_education(language=language)


__all__ = [
    "CANONICAL_URL",
    "ISLAND",
    "isle_of_man_education",
    "isle_of_man_education_source",
]
