"""Per-subject DLT source for Wales (chemistry, WJEC).

Per-subject DLT source for the British Isles parity change
(`2026-07-12-british-isles-parity-pipeline-v1`).

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/site_scrape_samples/biep/wls/chemistry/<lang>/``.

Reference: ``openspec/changes/2026-07-12-british-isles-parity-pipeline-v1/``.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


SUBJECT = "chemistry"
EXAM_BOARD = "WJEC"
DEFAULT_LEVEL = "a_level"


@dlt.resource(
    name="{nation}_{subject}_syllabus".format(nation="wls", subject=SUBJECT),
    write_disposition="merge",
    primary_key=["url", "language"],
    columns={
        "nation": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "exam_board": {"data_type": "text"},
        "level": {"data_type": "text"},
        "language": {"data_type": "text"},
        "url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "source": {"data_type": "text"},
        "extracted_at": {"data_type": "timestamp"},
    },
)
def wls_chemistry(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Wales chemistry syllabus rows from the canonical cache.

    Honours ``USE_LOCAL_SCRAPES=true`` by reading cached Firecrawl
    snapshots under
    ``stedding/site_scrape_samples/biep/wls/chemistry/<lang>/``.
    """
    import hashlib
    import json
    from datetime import UTC, datetime
    from pathlib import Path

    cache_dir = Path("stedding/site_scrape_samples/biep/wls/chemistry")
    languages = (language,) if language else ('en', 'cy')
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning(
                    "wls_chemistry_cache_parse_failed",
                    path=str(json_path),
                    error=str(exc),
                )
                continue
            metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {
                "nation": "wls",
                "subject": SUBJECT,
                "exam_board": EXAM_BOARD,
                "level": DEFAULT_LEVEL,
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": payload.get("title") or metadata.get("title", "") if isinstance(payload, dict) else "",
                "content_hash": f"sha256:{hashlib.sha256(markdown.encode()).hexdigest()[:16]}" if markdown else "",
                "source": "wjec",
                "extracted_at": datetime.now(UTC).isoformat(),
            }


@dlt.source(name="wls_chemistry")
def wls_chemistry_source(language: str | None = None):
    """DLT source for the Wales chemistry ingestion."""
    return wls_chemistry(language=language)


__all__ = [
    "EXAM_BOARD",
    "SUBJECT",
    "DEFAULT_LEVEL",
    "wls_chemistry",
    "wls_chemistry_source",
]
