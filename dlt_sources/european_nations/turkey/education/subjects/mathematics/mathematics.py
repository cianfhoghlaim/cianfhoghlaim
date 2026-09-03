"""Per-subject DLT source for Turkey (Mathematics).

Per-subject DLT source for the EU candidate / neighbour states
full-depth expansion
(`2026-07-13-eu-nations-full-depth-expansion-v1`).

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/tur/education/subjects/mathematics/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

from dlt_sources.european_nations._shared import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


SUBJECT = "mathematics"
EXAM_BOARD = "MEB"
DEFAULT_LEVEL = "upper_secondary"


class TurkeyMathematicsSource(NationSource):
    """Turkey Mathematics DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="tur",
            domain="education",
            source_slug="education_subjects_mathematics",
            supported_languages=('tr',),
            document_type="education_subject_document",
            extra_metadata={
                "canonical_root": "https://meb.gov.tr",
                "title": "Turkey Mathematics (TUR)",
                "subject": SUBJECT,
                "exam_board": EXAM_BOARD,
            },
        )


_NATION_SOURCE = TURMathematicsSource()


@dlt.resource(
    name="education_subjects_mathematics",
    write_disposition="merge",
    primary_key=["country_code", "subject", "language", "source_url"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "exam_board": {"data_type": "text"},
        "level": {"data_type": "text"},
        "source_url": {"data_type": "text"},
        "title": {"data_type": "text"},
        "content_hash": {"data_type": "text"},
        "document_type": {"data_type": "text"},
        "institution": {"data_type": "text"},
        "region": {"data_type": "text"},
        "official_status": {"data_type": "text"},
        "extracted_at": {"data_type": "timestamp"},
        "source": {"data_type": "text"},
        "source_file": {"data_type": "text"},
    },
)
def tur_mathematics(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Turkey Mathematics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "tur_mathematics_live_mode_not_implemented",
            hint="This v1 scaffold reads from the local cache.",
        )
    languages = (language,) if language else _NATION_SOURCE.supported_languages
    for lang in languages:
        if lang not in _NATION_SOURCE.supported_languages:
            continue
        cache_dir = (
            Path(__file__).resolve().parents[6]
            / "stedding"
            / "ingest_queue"
            / "european_nations"
            / "tur"
            / "education"
            / "subjects"
            / "mathematics"
            / lang
        )
        if not cache_dir.exists():
            continue
        for cache_path in sorted(cache_dir.glob("*.json")):
            row = row_from_cache(
                cache_path=cache_path,
                nation=_NATION_SOURCE,
                document_id_key="subject_document_id",
                default_status="published",
            )
            if row:
                row["subject_document_id"] = row.pop("document_id", cache_path.stem)
                row["subject"] = SUBJECT
                row["exam_board"] = EXAM_BOARD
                row["level"] = DEFAULT_LEVEL
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="tur_mathematics")
def tur_mathematics_source(language: str | None = None):
    """DLT source for the Turkey Mathematics ingestion."""
    return tur_mathematics(language=language)


__all__ = [
    "EXAM_BOARD",
    "SUBJECT",
    "DEFAULT_LEVEL",
    "TURMathematicsSource",
    "tur_mathematics",
    "tur_mathematics_source",
]
