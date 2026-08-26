"""DLT source for the South African Government Gazette.

Crawls ``https://www.gov.za/documents/government-gazette`` and emits one row per ``(sa_government_gazette_id, language)`` for
every document available in at least one of the official languages of
South Africa.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/zaf/law/sa_government_gazette.py`` with
``source_id="commonwealth.zaf.law.sa_government_gazette"`` and lands in the
DuckLake table ``oideachais.law.commonwealth.zaf``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/zaf/law/<lang>/``.

Reference: ``openspec/changes/2026-07-11-commonwealth-pipeline-v1/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
import structlog

from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import (
    JurisdictionPipelineBase,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class SouthAfricaLawSource(JurisdictionPipelineBase):
    """South African Government Gazette DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="zaf",
            domain="law",
            source_slug="sa_government_gazette",
            supported_languages=('en', 'af', 'zu', 'xh', 'nso', 'tn', 'st', 'ts', 'ss', 've', 'nr'),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://www.gov.za/documents/government-gazette",
                "title": "South African Government Gazette",
            },
        )


_NATION_SOURCE = SouthAfricaLawSource()


@dlt.resource(
    name="sa_government_gazette",
    write_disposition="merge",
    primary_key=["sa_government_gazette_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "sa_government_gazette_id": {"data_type": "text"},
        "title": {"data_type": "text"},
        "source_url": {"data_type": "text"},
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
def sa_government_gazette(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield South Africa law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "sa_government_gazette_live_mode_not_implemented",
            hint="This v1 scaffold reads from the local cache.",
        )
    languages = (language,) if language else _NATION_SOURCE.supported_languages
    for lang in languages:
        if lang not in _NATION_SOURCE.supported_languages:
            continue
        for cache_path in _NATION_SOURCE.iter_local_cache(lang):
            row = row_from_cache(
                cache_path=cache_path,
                nation=_NATION_SOURCE,
                document_id_key="sa_government_gazette_id",
                default_status="published",
            )
            if row:
                row["sa_government_gazette_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="sa_government_gazette")
def sa_government_gazette_source(language: str | None = None):
    """DLT source for the South African Government Gazette ingestion."""
    return sa_government_gazette(language=language)


__all__ = [
    "SouthAfricaLawSource",
    "sa_government_gazette",
    "sa_government_gazette_source",
]
