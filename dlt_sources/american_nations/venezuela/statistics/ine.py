"""DLT source for the Instituto Nacional de Estadística.

Crawls ``http://www.ine.gov.ve`` and emits one row per ``(ine_id, language)`` for
every document available in at least one of the official languages of
Venezuela.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/americas/Venezuela/statistics/ine.py`` with
``source_id="americas.Venezuela.statistics.ine"`` and lands in the
DuckLake table ``oideachais.statistics.americas.Venezuela``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/americas/Venezuela/statistics/<lang>/``.

Reference: ``openspec/changes/2026-07-11-americas-california-pipeline-v1/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
import structlog

from dlt_sources.european_nations._shared.nation_source import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class VenezuelaStatisticsSource(NationSource):
    """Instituto Nacional de Estadística DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="Venezuela",
            domain="statistics",
            source_slug="ine",
            supported_languages=('es',),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "http://www.ine.gov.ve",
                "title": "Instituto Nacional de Estadística",
            },
        )


_NATION_SOURCE = VenezuelaStatisticsSource()


@dlt.resource(
    name="ine",
    write_disposition="merge",
    primary_key=["ine_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "jurisdiction": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "ine_id": {"data_type": "text"},
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
def ine(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Venezuela statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "ine_live_mode_not_implemented",
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
                document_id_key="ine_id",
                default_status="published",
            )
            if row:
                row["ine_id"] = row.pop("document_id", cache_path.stem)
                row["jurisdiction"] = _NATION_SOURCE.country_code
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "americas"
                yield row


@dlt.source(name="ine")
def ine_source(language: str | None = None):
    """DLT source for the Instituto Nacional de Estadística ingestion."""
    return ine(language=language)


__all__ = [
    "VenezuelaStatisticsSource",
    "ine",
    "ine_source",
]
