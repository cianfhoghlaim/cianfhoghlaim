"""DLT source for the Central Statistical Bureau of Latvia (statistics, Latvia).

Crawls ``https://stat.gov.lv`` and emits one row per ``(stats_office_lva_id, language)`` for
every document available in at least one of the official languages of
Latvia.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/lva/statistics/stats_office_lva.py`` with
``source_id="european_nations.lva.statistics.stats_office_lva"`` and lands in
the DuckLake table ``oideachais.statistics.european_nations.lva``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/lva/statistics/<lang>/``.

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


class LatviaStatisticsSource(NationSource):
    """Central Statistical Bureau of Latvia DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="lva",
            domain="statistics",
            source_slug="stats_office_lva",
            supported_languages=("lv",),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://stat.gov.lv",
                "title": "Central Statistical Bureau of Latvia",
            },
        )


_NATION_SOURCE = LatviaStatisticsSource()


@dlt.resource(
    name="stats_office_lva",
    write_disposition="merge",
    primary_key=["stats_office_lva_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "stats_office_lva_id": {"data_type": "text"},
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
def stats_office_lva(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Latvia statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "stats_office_lva_live_mode_not_implemented",
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
                document_id_key="stats_office_lva_id",
                default_status="published",
            )
            if row:
                row["stats_office_lva_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="stats_office_lva")
def stats_office_lva_source(language: str | None = None):
    """DLT source for the Central Statistical Bureau of Latvia ingestion."""
    return stats_office_lva(language=language)


__all__ = [
    "LatviaStatisticsSource",
    "stats_office_lva",
    "stats_office_lva_source",
]
