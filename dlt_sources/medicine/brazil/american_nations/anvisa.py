"""DLT source for the Agência Nacional de Vigilância Sanitária.

Crawls ``https://www.gov.br/anvisa`` and emits one row per ``(anvisa_id, language)`` for
every document available in at least one of the official languages of
Brazil.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/americas/Brazil/medicine/anvisa.py`` with
``source_id="americas.Brazil.medicine.anvisa"`` and lands in the
DuckLake table ``oideachais.medicine.americas.Brazil``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/americas/Brazil/medicine/<lang>/``.

Reference: ``openspec/changes/2026-07-11-americas-california-pipeline-v1/``.
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


class BrazilMedicineSource(JurisdictionPipelineBase):
    """Agência Nacional de Vigilância Sanitária DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="Brazil",
            domain="medicine",
            source_slug="anvisa",
            supported_languages=('pt',),
            document_type="medicine_document",
            extra_metadata={
                "canonical_root": "https://www.gov.br/anvisa",
                "title": "Agência Nacional de Vigilância Sanitária",
            },
        )


_NATION_SOURCE = BrazilMedicineSource()


@dlt.resource(
    name="anvisa",
    write_disposition="merge",
    primary_key=["anvisa_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "jurisdiction": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "anvisa_id": {"data_type": "text"},
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
def anvisa(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Brazil medicine rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "anvisa_live_mode_not_implemented",
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
                document_id_key="anvisa_id",
                default_status="published",
            )
            if row:
                row["anvisa_id"] = row.pop("document_id", cache_path.stem)
                row["jurisdiction"] = _NATION_SOURCE.country_code
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "americas"
                yield row


@dlt.source(name="anvisa")
def anvisa_source(language: str | None = None):
    """DLT source for the Agência Nacional de Vigilância Sanitária ingestion."""
    return anvisa(language=language)


__all__ = [
    "BrazilMedicineSource",
    "anvisa",
    "anvisa_source",
]
