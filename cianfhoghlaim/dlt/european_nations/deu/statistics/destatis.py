"""DLT source for the Statistisches Bundesamt.

Crawls ``https://www.destatis.de`` and emits one row per ``(destatis_id, language)`` for
every document available in at least one of the official languages of
Germany.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/deu/statistics/destatis.py`` with
``source_id="european_nations.deu.statistics.destatis"`` and lands in
the DuckLake table ``oideachais.statistics.european_nations.deu``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/deu/statistics/<lang>/``.

Reference: ``openspec/changes/2026-07-11-european-nations-ukraine-pipeline-v1/``.
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


class DEUStatisticsSource(NationSource):
    """Statistisches Bundesamt DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="deu",
            domain="statistics",
            source_slug="destatis",
            supported_languages=('de',),
            document_type="statistics_document",
            extra_metadata={
                "canonical_root": "https://www.destatis.de",
                "title": "Statistisches Bundesamt",
            },
        )


_NATION_SOURCE = DEUStatisticsSource()


@dlt.resource(
    name="destatis",
    write_disposition="merge",
    primary_key=["destatis_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "destatis_id": {"data_type": "text"},
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
def destatis(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Germany statistics rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "destatis_live_mode_not_implemented",
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
                document_id_key="destatis_id",
                default_status="published",
            )
            if row:
                row["destatis_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="destatis")
def destatis_source(language: str | None = None):
    """DLT source for the Statistisches Bundesamt ingestion."""
    return destatis(language=language)


__all__ = [
    "DEUStatisticsSource",
    "destatis",
    "destatis_source",
]
