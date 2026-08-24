"""DLT source for the Agenzia Italiana del Farmaco.

Crawls ``https://www.aifa.gov.it`` and emits one row per ``(aifa_id, language)`` for
every document available in at least one of the official languages of
Italy.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/ita/medicine/aifa.py`` with
``source_id="european_nations.ita.medicine.aifa"`` and lands in
the DuckLake table ``oideachais.medicine.european_nations.ita``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/ita/medicine/<lang>/``.

Reference: ``openspec/changes/2026-07-11-european-nations-ukraine-pipeline-v1/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
import structlog

from dlt_sources.european_nations._shared import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class ItalyMedicineSource(NationSource):
    """Agenzia Italiana del Farmaco DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="ita",
            domain="medicine",
            source_slug="aifa",
            supported_languages=('it',),
            document_type="medicine_document",
            extra_metadata={
                "canonical_root": "https://www.aifa.gov.it",
                "title": "Agenzia Italiana del Farmaco",
            },
        )


_NATION_SOURCE = ItalyMedicineSource()


@dlt.resource(
    name="aifa",
    write_disposition="merge",
    primary_key=["aifa_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "aifa_id": {"data_type": "text"},
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
def aifa(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Italy medicine rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "aifa_live_mode_not_implemented",
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
                document_id_key="aifa_id",
                default_status="published",
            )
            if row:
                row["aifa_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="aifa")
def aifa_source(language: str | None = None):
    """DLT source for the Agenzia Italiana del Farmaco ingestion."""
    return aifa(language=language)


__all__ = [
    "ItalyMedicineSource",
    "aifa",
    "aifa_source",
]
