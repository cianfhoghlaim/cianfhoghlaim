"""DLT source for the Instituto Nacional de Estadística y Geografía.

Crawls ``https://www.inegi.org.mx`` and emits one row per ``(inegi_id, language)`` for
every document available in at least one of the official languages of
Mexico.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/americas/Mexico/statistics/inegi.py`` with
``source_id="americas.Mexico.statistics.inegi"`` and lands in the
DuckLake table ``oideachais.statistics.americas.Mexico``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/americas/Mexico/statistics/<lang>/``.

Reference: ``openspec/changes/2026-07-11-americas-california-pipeline-v1/``.
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


class MEXStatisticsSource(NationSource):
    """Instituto Nacional de Estadística y Geografía DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="Mexico",
            domain="statistics",
            source_slug="inegi",
            supported_languages=('es',),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://www.inegi.org.mx",
                "title": "Instituto Nacional de Estadística y Geografía",
            },
        )


_NATION_SOURCE = MEXStatisticsSource()


@dlt.resource(
    name="inegi",
    write_disposition="merge",
    primary_key=["inegi_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "jurisdiction": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "inegi_id": {"data_type": "text"},
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
def inegi(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Mexico statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "inegi_live_mode_not_implemented",
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
                document_id_key="inegi_id",
                default_status="published",
            )
            if row:
                row["inegi_id"] = row.pop("document_id", cache_path.stem)
                row["jurisdiction"] = _NATION_SOURCE.country_code
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "americas"
                yield row


@dlt.source(name="inegi")
def inegi_source(language: str | None = None):
    """DLT source for the Instituto Nacional de Estadística y Geografía ingestion."""
    return inegi(language=language)


__all__ = [
    "MEXStatisticsSource",
    "inegi",
    "inegi_source",
]
