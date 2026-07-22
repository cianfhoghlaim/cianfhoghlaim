"""DLT source for the Public Health Institute of Bosnia and Herzegovina.

Crawls ``https://fmz.gov.ba`` and emits one row per ``(phi_id, language)``
for every document available in at least one of the official
languages of Bosnia and Herzegovina.

Per the canonical
[`cross-region-pipeline`](../../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/bih/medicine/public_health_institute.py`` with
``source_id="european_nations.bih.medicine.public_health_institute"`` and lands in
the DuckLake table ``oideachais.medicine.european_nations.bih``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/bih/medicine/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
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


class BIHMedicineSource(NationSource):
    """Public Health Institute of Bosnia and Herzegovina DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="bih",
            domain="medicine",
            source_slug="public_health_institute",
            supported_languages=('bs', 'hr', 'sr'),
            document_type="medicine_document",
            extra_metadata={
                "canonical_root": "https://fmz.gov.ba",
                "title": "Public Health Institute of Bosnia and Herzegovina",
            },
        )


_NATION_SOURCE = BIHMedicineSource()


@dlt.resource(
    name="public_health_institute",
    write_disposition="merge",
    primary_key=["phi_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "phi_id": {"data_type": "text"},
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
def public_health_institute(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Bosnia and Herzegovina Public Health Institute rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "public_health_institute_live_mode_not_implemented",
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
                document_id_key="phi_id",
                default_status="published",
            )
            if row:
                row["phi_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="public_health_institute")
def public_health_institute_source(language: str | None = None):
    """DLT source for the Public Health Institute of Bosnia and Herzegovina ingestion."""
    return public_health_institute(language=language)


__all__ = [
    "BIHMedicineSource",
    "public_health_institute",
    "public_health_institute_source",
]
