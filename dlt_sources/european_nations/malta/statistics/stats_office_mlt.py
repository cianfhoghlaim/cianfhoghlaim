"""DLT source for the National Statistics Office (Malta) (statistics, Malta).

Crawls ``https://nso.gov.mt`` and emits one row per ``(stats_office_mlt_id, language)`` for
every document available in at least one of the official languages of
Malta.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/mlt/statistics/stats_office_mlt.py`` with
``source_id="european_nations.mlt.statistics.stats_office_mlt"`` and lands in
the DuckLake table ``oideachais.statistics.european_nations.mlt``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/mlt/statistics/<lang>/``.

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


class MaltaStatisticsSource(NationSource):
    """National Statistics Office (Malta) DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="mlt",
            domain="statistics",
            source_slug="stats_office_mlt",
            supported_languages=("mt", "en",),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://nso.gov.mt",
                "title": "National Statistics Office (Malta)",
            },
        )


_NATION_SOURCE = MaltaStatisticsSource()


@dlt.resource(
    name="stats_office_mlt",
    write_disposition="merge",
    primary_key=["stats_office_mlt_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "stats_office_mlt_id": {"data_type": "text"},
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
def stats_office_mlt(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Malta statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "stats_office_mlt_live_mode_not_implemented",
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
                document_id_key="stats_office_mlt_id",
                default_status="published",
            )
            if row:
                row["stats_office_mlt_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="stats_office_mlt")
def stats_office_mlt_source(language: str | None = None):
    """DLT source for the National Statistics Office (Malta) ingestion."""
    return stats_office_mlt(language=language)


__all__ = [
    "MaltaStatisticsSource",
    "stats_office_mlt",
    "stats_office_mlt_source",
]
