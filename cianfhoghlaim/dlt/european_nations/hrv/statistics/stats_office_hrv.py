"""DLT source for the Croatian Bureau of Statistics (statistics, Croatia).

Crawls ``https://dzs.gov.hr`` and emits one row per ``(stats_office_hrv_id, language)`` for
every document available in at least one of the official languages of
Croatia.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/hrv/statistics/stats_office_hrv.py`` with
``source_id="european_nations.hrv.statistics.stats_office_hrv"`` and lands in
the DuckLake table ``oideachais.statistics.european_nations.hrv``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/hrv/statistics/<lang>/``.

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


class CroatiaStatisticsSource(NationSource):
    """Croatian Bureau of Statistics DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="hrv",
            domain="statistics",
            source_slug="stats_office_hrv",
            supported_languages=("hr",),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://dzs.gov.hr",
                "title": "Croatian Bureau of Statistics",
            },
        )


_NATION_SOURCE = CroatiaStatisticsSource()


@dlt.resource(
    name="stats_office_hrv",
    write_disposition="merge",
    primary_key=["stats_office_hrv_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "stats_office_hrv_id": {"data_type": "text"},
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
def stats_office_hrv(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Croatia statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "stats_office_hrv_live_mode_not_implemented",
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
                document_id_key="stats_office_hrv_id",
                default_status="published",
            )
            if row:
                row["stats_office_hrv_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="stats_office_hrv")
def stats_office_hrv_source(language: str | None = None):
    """DLT source for the Croatian Bureau of Statistics ingestion."""
    return stats_office_hrv(language=language)


__all__ = [
    "CroatiaStatisticsSource",
    "stats_office_hrv",
    "stats_office_hrv_source",
]
