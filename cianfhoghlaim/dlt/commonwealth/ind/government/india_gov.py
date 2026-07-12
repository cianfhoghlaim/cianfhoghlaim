"""DLT source for the India.gov.in portal.

Crawls ``https://www.india.gov.in`` and emits one row per ``(india_gov_id, language)`` for
every document available in at least one of the official languages of
India.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/ind/government/india_gov.py`` with
``source_id="commonwealth.ind.government.india_gov"`` and lands in the
DuckLake table ``oideachais.government.commonwealth.ind``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/ind/government/<lang>/``.

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


class IndiaGovernmentSource(NationSource):
    """India.gov.in portal DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="ind",
            domain="government",
            source_slug="india_gov",
            supported_languages=('en', 'hi'),
            document_type="government_document",
            extra_metadata={
                "canonical_root": "https://www.india.gov.in",
                "title": "India.gov.in portal",
            },
        )


_NATION_SOURCE = IndiaGovernmentSource()


@dlt.resource(
    name="india_gov",
    write_disposition="merge",
    primary_key=["india_gov_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "india_gov_id": {"data_type": "text"},
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
def india_gov(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield India government rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "india_gov_live_mode_not_implemented",
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
                document_id_key="india_gov_id",
                default_status="published",
            )
            if row:
                row["india_gov_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="india_gov")
def india_gov_source(language: str | None = None):
    """DLT source for the India.gov.in portal ingestion."""
    return india_gov(language=language)


__all__ = [
    "IndiaGovernmentSource",
    "india_gov",
    "india_gov_source",
]
