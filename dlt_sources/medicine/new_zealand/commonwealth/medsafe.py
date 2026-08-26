"""DLT source for the Medsafe — Medicines and Medical Devices Safety Authority.

Crawls ``https://www.medsafe.govt.nz`` and emits one row per ``(medsafe_id, language)`` for
every document available in at least one of the official languages of
New Zealand.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/nzl/medicine/medsafe.py`` with
``source_id="commonwealth.nzl.medicine.medsafe"`` and lands in the
DuckLake table ``oideachais.medicine.commonwealth.nzl``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/nzl/medicine/<lang>/``.

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


class NewZealandMedicineSource(JurisdictionPipelineBase):
    """Medsafe — Medicines and Medical Devices Safety Authority DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="nzl",
            domain="medicine",
            source_slug="medsafe",
            supported_languages=('en',),
            document_type="medicine_document",
            extra_metadata={
                "canonical_root": "https://www.medsafe.govt.nz",
                "title": "Medsafe — Medicines and Medical Devices Safety Authority",
            },
        )


_NATION_SOURCE = NewZealandMedicineSource()


@dlt.resource(
    name="medsafe",
    write_disposition="merge",
    primary_key=["medsafe_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "medsafe_id": {"data_type": "text"},
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
def medsafe(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield New Zealand medicine rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "medsafe_live_mode_not_implemented",
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
                document_id_key="medsafe_id",
                default_status="published",
            )
            if row:
                row["medsafe_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="medsafe")
def medsafe_source(language: str | None = None):
    """DLT source for the Medsafe — Medicines and Medical Devices Safety Authority ingestion."""
    return medsafe(language=language)


__all__ = [
    "NewZealandMedicineSource",
    "medsafe",
    "medsafe_source",
]
