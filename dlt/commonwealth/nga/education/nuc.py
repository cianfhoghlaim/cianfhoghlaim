"""DLT source for the Nigerian federal National Universities Commission.

Federal Nigerian DLT source (10 total). Per the
[`2026-07-12-commonwealth-nigeria-pipeline-v1`](../../../openspec/changes/2026-07-12-commonwealth-nigeria-pipeline-v1/)
change.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/nga/education/nuc/<lang>/``.
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


FEDERAL_INSTITUTION = "nuc"
CANONICAL_URL = "https://www.nuc.edu.ng"
DEFAULT_LANGUAGE = "en"


@dlt.resource(
    name="nga_federal_nuc",
    write_disposition="merge",
    primary_key=["url", "language"],
    columns={
        "country": {"data_type": "text"},
        "federal_institution": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "language": {"data_type": "text"},
        "url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "source": {"data_type": "text"},
        "extracted_at": {"data_type": "timestamp"},
    },
)
def nga_federal_nuc(language=None):
    """Yield Nigerian federal rows from the canonical cache."""
    cache_dir = Path("stedding/ingest_queue/commonwealth/nga/education/nuc")
    languages = (language,) if language else ("en", "ha", "yo", "ig", "pcm")
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning("nga_federal_nuc_cache_parse_failed", path=str(json_path), error=str(exc))
                continue
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {
                "country": "nga",
                "federal_institution": FEDERAL_INSTITUTION,
                "domain": "education",
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": (payload.get("title") or metadata.get("title", "") if isinstance(payload, dict) else ""),
                "content_hash": f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}" if markdown else "",
                "source": FEDERAL_INSTITUTION,
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="nga_federal_nuc")
def nga_federal_nuc_source(language=None):
    """DLT source for the Nigerian federal ingestion."""
    return nga_federal_nuc(language=language)


__all__ = [
    "CANONICAL_URL",
    "DEFAULT_LANGUAGE",
    "FEDERAL_INSTITUTION",
    "nga_federal_nuc",
    "nga_federal_nuc_source",
]
