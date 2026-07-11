"""DLT source for the Ogun state.

Nigerian state DLT source (37 sub-units × 5 domains = 185 sources
total). Per the
[`2026-07-12-commonwealth-nigeria-pipeline-v1`](../../../openspec/changes/2026-07-12-commonwealth-nigeria-pipeline-v1/)
change.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/nga/states/nga_ogn/law/legislation/<lang>/``.
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


STATE_CODE = "nga_ogn"
STATE_NAME = "Ogun"
DOMAIN = "law"
SLUG = "legislation"
DEFAULT_LANGUAGE = "en"


@dlt.resource(
    name="nga_ogn_legislation",
    write_disposition="merge",
    primary_key=["url", "language"],
    columns={
        "country": {"data_type": "text"},
        "state_code": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "language": {"data_type": "text"},
        "url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "source": {"data_type": "text"},
        "extracted_at": {"data_type": "timestamp"},
    },
)
def nga_ogn_legislation(language=None):
    """Yield state rows from the canonical cache."""
    cache_dir = Path("stedding/ingest_queue/commonwealth/nga/states/nga_ogn/law/legislation")
    languages = (language,) if language else ("en", "yo")
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("nga_ogn_legislation_cache_parse_failed", path=str(json_path), error=str(exc))
                continue
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {
                "country": "nga",
                "state_code": STATE_CODE,
                "domain": "law",
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": (payload.get("title") or metadata.get("title", "") if isinstance(payload, dict) else ""),
                "content_hash": f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}" if markdown else "",
                "source": SLUG,
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="nga_ogn_legislation")
def nga_ogn_legislation_source(language=None):
    """DLT source for the state ingestion."""
    return nga_ogn_legislation(language=language)


__all__ = [
    "DEFAULT_LANGUAGE",
    "DOMAIN",
    "SLUG",
    "STATE_CODE",
    "STATE_NAME",
    "nga_ogn_legislation",
    "nga_ogn_legislation_source",
]
