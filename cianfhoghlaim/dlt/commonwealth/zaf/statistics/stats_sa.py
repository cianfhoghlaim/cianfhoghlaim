"""DLT source for the Statistics South Africa.

Crawls ``http://www.statssa.gov.za`` and emits one row per ``(stats_sa_id, language)`` for
every document available in at least one of the official languages of
South Africa.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/zaf/statistics/stats_sa.py`` with
``source_id="commonwealth.zaf.statistics.stats_sa"`` and lands in the
DuckLake table ``oideachais.statistics.commonwealth.zaf``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/zaf/statistics/<lang>/``.

Reference: ``openspec/changes/2026-07-11-commonwealth-pipeline-v1/``.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_nations._shared.nation_source import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class SouthAfricaStatisticsSource(NationSource):
    """Statistics South Africa DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="zaf",
            domain="statistics",
            source_slug="stats_sa",
            supported_languages=('en', 'af', 'zu', 'xh', 'nso', 'tn', 'st', 'ts', 'ss', 've', 'nr'),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "http://www.statssa.gov.za",
                "title": "Statistics South Africa",
            },
        )


_NATION_SOURCE = SouthAfricaStatisticsSource()


@dlt.resource(
    name="stats_sa",
    write_disposition="merge",
    primary_key=["stats_sa_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "stats_sa_id": {"data_type": "text"},
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
def stats_sa(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield South Africa statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "stats_sa_live_mode_not_implemented",
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
                document_id_key="stats_sa_id",
                default_status="published",
            )
            if row:
                row["stats_sa_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="stats_sa")
def stats_sa_source(language: str | None = None):
    """DLT source for the Statistics South Africa ingestion."""
    return stats_sa(language=language)


__all__ = [
    "SouthAfricaStatisticsSource",
    "stats_sa",
    "stats_sa_source",
]
