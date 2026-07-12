"""DLT source for the Instituto Brasileiro de Geografia e Estatística.

Crawls ``https://www.ibge.gov.br`` and emits one row per ``(ibge_id, language)`` for
every document available in at least one of the official languages of
Brazil.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/americas/Brazil/statistics/ibge.py`` with
``source_id="americas.Brazil.statistics.ibge"`` and lands in the
DuckLake table ``oideachais.statistics.americas.Brazil``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/americas/Brazil/statistics/<lang>/``.

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


class BRAStatisticsSource(NationSource):
    """Instituto Brasileiro de Geografia e Estatística DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="Brazil",
            domain="statistics",
            source_slug="ibge",
            supported_languages=('pt',),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://www.ibge.gov.br",
                "title": "Instituto Brasileiro de Geografia e Estatística",
            },
        )


_NATION_SOURCE = BRAStatisticsSource()


@dlt.resource(
    name="ibge",
    write_disposition="merge",
    primary_key=["ibge_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "jurisdiction": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "ibge_id": {"data_type": "text"},
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
def ibge(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Brazil statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "ibge_live_mode_not_implemented",
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
                document_id_key="ibge_id",
                default_status="published",
            )
            if row:
                row["ibge_id"] = row.pop("document_id", cache_path.stem)
                row["jurisdiction"] = _NATION_SOURCE.country_code
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "americas"
                yield row


@dlt.source(name="ibge")
def ibge_source(language: str | None = None):
    """DLT source for the Instituto Brasileiro de Geografia e Estatística ingestion."""
    return ibge(language=language)


__all__ = [
    "BRAStatisticsSource",
    "ibge",
    "ibge_source",
]
