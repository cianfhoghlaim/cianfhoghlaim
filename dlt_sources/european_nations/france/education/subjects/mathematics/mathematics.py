"""Per-subject DLT source for the France {Mathematics} curriculum.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/fra/education/subjects/mathematics/fr/sample.json``.
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


SUBJECT_KEY = "mathematics"
SUBJECT_LABEL = "Mathematics"


@dlt.resource(
    name="fra_mathematics",
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
def fra_mathematics(language=None) -> Iterator[dict[str, Any]]:
    """Yield France Mathematics rows from the canonical cache."""
    cache_dir = Path("stedding/ingest_queue/european_nations/fra/education/subjects/mathematics")
    languages = (language,) if language else ('fr', 'en')
    for lang in languages:
        lang_dir = cache_dir / lang
        if not lang_dir.exists():
            continue
        for json_path in sorted(lang_dir.glob("*.json")):
            try:
                payload = json.loads(json_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning(
                    "fra_mathematics_cache_parse_failed",
                    path=str(json_path),
                    error=str(exc),
                )
                continue
            metadata = payload.get("metadata", {{}}) if isinstance(payload, dict) else {{}}
            markdown = payload.get("markdown", "") if isinstance(payload, dict) else ""
            yield {{
                "country": "France",
                "jurisdiction": "fra",
                "subject": SUBJECT_LABEL,
                "language": lang,
                "url": metadata.get("sourceURL") or metadata.get("url") or "",
                "title": (payload.get("title") or metadata.get("title", "") if isinstance(payload, dict) else ""),
                "content_hash": f"sha256:{{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}}" if markdown else "",
                "document_type": "Mathematics_curriculum",
                "institution": "Ministère de l'Éducation nationale",
                "region": "european_nations",
                "official_status": metadata.get("official_status", "published"),
                "extracted_at": datetime.now(UTC).isoformat(),
                "source": "Ministère de l'Éducation nationale",
                "source_file": str(json_path),
            }}


@dlt.source(name="fra_mathematics")
def fra_mathematics_source(language=None):
    """DLT source for the France Mathematics ingestion."""
    return fra_mathematics(language=language)


__all__ = [
    "SUBJECT_KEY",
    "SUBJECT_LABEL",
    "fra_mathematics",
    "fra_mathematics_source",
]
