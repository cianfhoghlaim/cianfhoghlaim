"""Per-subject DLT source for the Ukraine {Biology} curriculum.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/ukr/education/subjects/biology/uk/sample.json``.
"""

from __future__ import annotations
import dlt


import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

logger = structlog.get_logger(__name__)


SUBJECT_KEY = "biology"
SUBJECT_LABEL = "Biology"


@dlt.resource(
    name="ukr_biology",
    write_disposition="merge",
    primary_key=["url", "language"],
    columns={{
        "country": {{"data_type": "text"}},
        "jurisdiction": {{"data_type": "text"}},
        "subject": {{"data_type": "text"}},
        "language": {{"data_type": "text"}},
        "url": {{"data_type": "text"}},
        "title": {{"data_type": "text"}},
        "content_hash": {{"data_type": "text"}},
        "document_type": {{"data_type": "text"}},
        "institution": {{"data_type": "text"}},
        "region": {{"data_type": "text"}},
        "official_status": {{"data_type": "text"}},
        "extracted_at": {{"data_type": "timestamp"}},
        "source": {{"data_type": "text"}},
        "source_file": {{"data_type": "text"}},
    }},
)
def ukr_biology(language=None) -> Iterator[dict[str, Any]]:
    """Yield Ukraine Biology rows from the canonical cache."""
    cache_dir = Path("stedding/ingest_queue/european_nations/ukr/education/subjects/biology")
    languages = (language,) if language else ('uk', 'en')
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning(
                    "ukr_biology_cache_parse_failed",
                    path=str(json_path),
                    error=str(exc),
                )
                continue
            metadata = payload.get("metadata", {{}}) if isinstance(payload, dict) else {{}}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {{
                "country": "Ukraine",
                "jurisdiction": "ukr",
                "subject": SUBJECT_LABEL,
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": (payload.get("title") or metadata.get("title", "") if isinstance(payload, dict) else ""),
                "content_hash": f"sha256:{{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}}" if markdown else "",
                "document_type": "Biology_curriculum",
                "institution": "Ministry of Education and Science of Ukraine",
                "region": "european_nations",
                "official_status": metadata.get("official_status", "published"),
                "extracted_at": datetime.now(UTC).isoformat(),
                "source": "Ministry of Education and Science of Ukraine",
                "source_file": str(json_path),
            }}


@dlt.source(name="ukr_biology")
def ukr_biology_source(language=None):
    """DLT source for the Ukraine Biology ingestion."""
    return ukr_biology(language=language)


__all__ = [
    "SUBJECT_KEY",
    "SUBJECT_LABEL",
    "ukr_biology",
    "ukr_biology_source",
]
