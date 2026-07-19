"""DLT source for the Stats NZ — Tatauranga Aotearoa.

Crawls ``https://www.stats.govt.nz`` and emits one row per ``(stats_nz_id, language)`` for
every document available in at least one of the official languages of
New Zealand.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/nzl/statistics/stats_nz.py`` with
``source_id="commonwealth.nzl.statistics.stats_nz"`` and lands in the
DuckLake table ``oideachais.statistics.commonwealth.nzl``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/nzl/statistics/<lang>/``.

Reference: ``openspec/changes/2026-07-11-commonwealth-pipeline-v1/``.
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


class NewZealandStatisticsSource(NationSource):
    """Stats NZ — Tatauranga Aotearoa DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="nzl",
            domain="statistics",
            source_slug="stats_nz",
            supported_languages=('en',),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://www.stats.govt.nz",
                "title": "Stats NZ — Tatauranga Aotearoa",
            },
        )


_NATION_SOURCE = NewZealandStatisticsSource()


@dlt.resource(
    name="stats_nz",
    write_disposition="merge",
    primary_key=["stats_nz_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "stats_nz_id": {"data_type": "text"},
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
def stats_nz(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield New Zealand statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "stats_nz_live_mode_not_implemented",
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
                document_id_key="stats_nz_id",
                default_status="published",
            )
            if row:
                row["stats_nz_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="stats_nz")
def stats_nz_source(language: str | None = None):
    """DLT source for the Stats NZ — Tatauranga Aotearoa ingestion."""
    return stats_nz(language=language)


__all__ = [
    "NewZealandStatisticsSource",
    "stats_nz",
    "stats_nz_source",
]
