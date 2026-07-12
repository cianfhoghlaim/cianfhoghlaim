"""DLT source for the Quebec Montreal university cluster (McGill + UdeM + UQAM + Concordia).

The Quebec deep education cluster source. Honours
``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/can/qc/education/mcgill_universities/<lang>/``.

Reference: ``openspec/changes/2026-07-12-canada-provinces-quebec-montreal-pipeline-v1/``.
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


SLUG = "mcgill_universities"
CANONICAL_URL = "https://www.mcgill.ca"


@dlt.resource(
    name="qc_mcgill_universities",
    write_disposition="merge",
    primary_key=["url", "language"],
    columns={
        "province": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "school_board": {"data_type": "text"},
        "language": {"data_type": "text"},
        "url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "source": {"data_type": "text"},
        "extracted_at": {"data_type": "timestamp"},
    },
)
def qc_mcgill_universities(language=None):
    """Yield Quebec Montreal university cluster (McGill + UdeM + UQAM + Concordia) rows from the canonical cache."""
    cache_dir = Path("stedding/ingest_queue/commonwealth/can/qc/education/mcgill_universities")
    languages = (language,) if language else ("fr", "en")
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("qc_mcgill_universities_cache_parse_failed", path=str(json_path), error=str(exc))
                continue
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {
                "province": "qc",
                "domain": "education",
                "school_board": SLUG,
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": (payload.get("title") or metadata.get("title", "") if isinstance(payload, dict) else ""),
                "content_hash": f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}" if markdown else "",
                "source": SLUG,
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="qc_mcgill_universities")
def qc_mcgill_universities_source(language=None):
    """DLT source for the Quebec Montreal university cluster (McGill + UdeM + UQAM + Concordia) ingestion."""
    return qc_mcgill_universities(language=language)


__all__ = [
    "CANONICAL_URL",
    "SLUG",
    "qc_mcgill_universities",
    "qc_mcgill_universities_source",
]
