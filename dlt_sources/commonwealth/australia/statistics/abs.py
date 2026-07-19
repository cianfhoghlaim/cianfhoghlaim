"""DLT source for the Australian Bureau of Statistics.

Crawls ``https://www.abs.gov.au`` and emits one row per ``(abs_id, language)`` for
every document available in at least one of the official languages of
Australia.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/aus/statistics/abs.py`` with
``source_id="commonwealth.aus.statistics.abs"`` and lands in the
DuckLake table ``oideachais.statistics.commonwealth.aus``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/aus/statistics/<lang>/``.

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


class AustraliaStatisticsSource(NationSource):
    """Australian Bureau of Statistics DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="aus",
            domain="statistics",
            source_slug="abs",
            supported_languages=('en',),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://www.abs.gov.au",
                "title": "Australian Bureau of Statistics",
            },
        )


_NATION_SOURCE = AustraliaStatisticsSource()


@dlt.resource(
    name="abs",
    write_disposition="merge",
    primary_key=["abs_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "abs_id": {"data_type": "text"},
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
def abs(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Australia statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "abs_live_mode_not_implemented",
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
                document_id_key="abs_id",
                default_status="published",
            )
            if row:
                row["abs_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="abs")
def abs_source(language: str | None = None):
    """DLT source for the Australian Bureau of Statistics ingestion."""
    return abs(language=language)


__all__ = [
    "AustraliaStatisticsSource",
    "abs",
    "abs_source",
]
