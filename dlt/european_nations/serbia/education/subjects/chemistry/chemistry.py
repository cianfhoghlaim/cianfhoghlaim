"""Per-subject DLT source for Serbia (Chemistry).

Per-subject DLT source for the EU candidate / neighbour states
full-depth expansion
(`2026-07-13-eu-nations-full-depth-expansion-v1`).

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/srb/education/subjects/chemistry/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
"""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_nations._shared import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


SUBJECT = "chemistry"
EXAM_BOARD = "ZVO"
DEFAULT_LEVEL = "upper_secondary"


class SRBChemistrySource(NationSource):
    """Serbia Chemistry DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="srb",
            domain="education",
            source_slug="education_subjects_chemistry",
            supported_languages=('sr',),
            document_type="education_subject_document",
            extra_metadata={
                "canonical_root": "https://mpn.gov.rs",
                "title": "Serbia Chemistry (SRB)",
                "subject": SUBJECT,
                "exam_board": EXAM_BOARD,
            },
        )


_NATION_SOURCE = SRBChemistrySource()


@dlt.resource(
    name="education_subjects_chemistry",
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
def srb_chemistry(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Serbia Chemistry rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "srb_chemistry_live_mode_not_implemented",
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
            / "srb"
            / "education"
            / "subjects"
            / "chemistry"
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


@dlt.source(name="srb_chemistry")
def srb_chemistry_source(language: str | None = None):
    """DLT source for the Serbia Chemistry ingestion."""
    return srb_chemistry(language=language)


__all__ = [
    "EXAM_BOARD",
    "SUBJECT",
    "DEFAULT_LEVEL",
    "SRBChemistrySource",
    "srb_chemistry",
    "srb_chemistry_source",
]
