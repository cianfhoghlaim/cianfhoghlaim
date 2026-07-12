"""DLT source for the National Public Health Center (Hungary) (medicine, Hungary).

Crawls ``https://www.nnk.gov.hu`` and emits one row per ``(public_health_hun_id, language)`` for
every document available in at least one of the official languages of
Hungary.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/hun/medicine/public_health_hun.py`` with
``source_id="european_nations.hun.medicine.public_health_hun"`` and lands in
the DuckLake table ``oideachais.medicine.european_nations.hun``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/hun/medicine/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_nations._shared import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class HungaryMedicineSource(NationSource):
    """National Public Health Center (Hungary) DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="hun",
            domain="medicine",
            source_slug="public_health_hun",
            supported_languages=("hu",),
            document_type="health_document",
            extra_metadata={
                "canonical_root": "https://www.nnk.gov.hu",
                "title": "National Public Health Center (Hungary)",
            },
        )


_NATION_SOURCE = HungaryMedicineSource()


@dlt.resource(
    name="public_health_hun",
    write_disposition="merge",
    primary_key=["public_health_hun_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "public_health_hun_id": {"data_type": "text"},
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
def public_health_hun(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Hungary medicine rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "public_health_hun_live_mode_not_implemented",
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
                document_id_key="public_health_hun_id",
                default_status="published",
            )
            if row:
                row["public_health_hun_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="public_health_hun")
def public_health_hun_source(language: str | None = None):
    """DLT source for the National Public Health Center (Hungary) ingestion."""
    return public_health_hun(language=language)


__all__ = [
    "HungaryMedicineSource",
    "public_health_hun",
    "public_health_hun_source",
]
