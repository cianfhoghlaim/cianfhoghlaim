"""Per-subject DLT source for Estonia (Chemistry, EHIS).

Per-subject DLT source for the EU nations full-depth expansion
(`2026-07-13-eu-nations-full-depth-expansion-v1`).

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/est/education/subjects/chemistry/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
"""
from __future__ import annotations
import dlt


import hashlib
import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

logger = structlog.get_logger(__name__)


SUBJECT = "chemistry"
EXAM_BOARD = "EHIS"
DEFAULT_LEVEL = "upper_secondary"
COUNTRY_CODE = "est"
CANONICAL_ROOT = "https://hm.ee"
SUPPORTED_LANGUAGES: tuple[str, ...] = ("et",)
DEFAULT_LANGUAGE = "et"


@dlt.resource(
    name="{nation}_{subject}_syllabus".format(nation=COUNTRY_CODE, subject=SUBJECT),
    write_disposition="merge",
    primary_key=["url", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "exam_board": {"data_type": "text"},
        "level": {"data_type": "text"},
        "language": {"data_type": "text"},
        "url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "source": {"data_type": "text"},
        "extracted_at": {"data_type": "timestamp"},
        "region": {"data_type": "text"},
    },
)
def est_chemistry(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Estonia Chemistry syllabus rows from the canonical cache.

    Honours ``USE_LOCAL_SCRAPES=true`` by reading cached Firecrawl
    snapshots under ``stedding/ingest_queue/european_nations/est/education/subjects/chemistry/<lang>/``.
    """
    cache_dir = Path("stedding/ingest_queue/european_nations/est/education/subjects/chemistry")
    languages = (language,) if language else SUPPORTED_LANGUAGES
    for lang in languages:
        if lang not in SUPPORTED_LANGUAGES:
            continue
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning(
                    "est_chemistry_cache_parse_failed",
                    path=str(json_path),
                    error=str(exc),
                )
                continue
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {
                "country_code": COUNTRY_CODE,
                "subject": SUBJECT,
                "exam_board": EXAM_BOARD,
                "level": DEFAULT_LEVEL,
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": (payload.get("title") if isinstance(payload, dict) else None)
                    or metadata.get("title", ""),
                "content_hash": (
                    f"sha256:{hashlib.sha256(markdown.encode()).hexdigest()[:16]}"
                    if markdown
                    else ""
                ),
                "source": "est",
                "region": "european_nations",
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="est_chemistry")
def est_chemistry_source(language: str | None = None):
    """DLT source for the Estonia Chemistry ingestion."""
    return est_chemistry(language=language)


__all__ = [
    "CANONICAL_ROOT",
    "COUNTRY_CODE",
    "DEFAULT_LANGUAGE",
    "DEFAULT_LEVEL",
    "EXAM_BOARD",
    "SUBJECT",
    "SUPPORTED_LANGUAGES",
    "est_chemistry",
    "est_chemistry_source",
]
