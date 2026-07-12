"""DLT source for the Statistics Office of Albania.

Crawls ``https://instat.gov.al`` and emits one row per ``(stat_office_id, language)``
for every document available in at least one of the official
languages of Albania.

Per the canonical
[`cross-region-pipeline`](../../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/alb/statistics/statistics_office.py`` with
``source_id="european_nations.alb.statistics.statistics_office"`` and lands in
the DuckLake table ``oideachais.statistics.european_nations.alb``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/alb/statistics/<lang>/``.

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


class ALBStatisticsSource(NationSource):
    """Statistics Office of Albania DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="alb",
            domain="statistics",
            source_slug="statistics_office",
            supported_languages=('sq',),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://instat.gov.al",
                "title": "Statistics Office of Albania",
            },
        )


_NATION_SOURCE = ALBStatisticsSource()


@dlt.resource(
    name="statistics_office",
    write_disposition="merge",
    primary_key=["stat_office_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "stat_office_id": {"data_type": "text"},
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
def statistics_office(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Albania Statistics Office rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "statistics_office_live_mode_not_implemented",
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
                document_id_key="stat_office_id",
                default_status="published",
            )
            if row:
                row["stat_office_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="statistics_office")
def statistics_office_source(language: str | None = None):
    """DLT source for the Statistics Office of Albania ingestion."""
    return statistics_office(language=language)


__all__ = [
    "ALBStatisticsSource",
    "statistics_office",
    "statistics_office_source",
]
