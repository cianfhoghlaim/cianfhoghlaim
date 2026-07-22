"""DLT source for STATEC - Institut national de la statistique.

Crawls ``https://statistiques.public.lu`` and emits one row per ``(national_statistics_id, language)`` for
every document available in at least one of the official languages of
STATEC - Institut national de la statistique.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/lux/statistics/national_statistics.py`` with
``source_id="european_nations.lux.statistics.national_statistics"`` and lands in
the DuckLake table ``oideachais.statistics.european_nations.lux``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/lux/statistics/<lang>/``.

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


class LUXNationalStatisticsSource(NationSource):
    """STATEC - Institut national de la statistique DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="lux",
            domain="statistics",
            source_slug="national_statistics",
            supported_languages=('lb', 'fr', 'de'),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://statistiques.public.lu",
                "title": "STATEC - Institut national de la statistique",
            },
        )


_NATION_SOURCE = LUXNationalStatisticsSource()


@dlt.resource(
    name="national_statistics",
    write_disposition="merge",
    primary_key=["national_statistics_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "national_statistics_id": {"data_type": "text"},
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
def national_statistics(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield STATEC - Institut national de la statistique rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "national_statistics_live_mode_not_implemented",
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
                document_id_key="national_statistics_id",
                default_status="published",
            )
            if row:
                row["national_statistics_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="national_statistics")
def national_statistics_source(language: str | None = None):
    """DLT source for the STATEC - Institut national de la statistique ingestion."""
    return national_statistics(language=language)


__all__ = [
    "LUXNationalStatisticsSource",
    "national_statistics",
    "national_statistics_source",
]
