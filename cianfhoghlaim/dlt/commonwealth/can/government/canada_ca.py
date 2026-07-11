"""DLT source for the Canada.ca portal.

Crawls ``https://www.canada.ca`` and emits one row per ``(canada_ca_id, language)`` for
every document available in at least one of the official languages of
Canada.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/can/government/canada_ca.py`` with
``source_id="commonwealth.can.government.canada_ca"`` and lands in the
DuckLake table ``oideachais.government.commonwealth.can``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/can/government/<lang>/``.

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


class CANGovernmentSource(NationSource):
    """Canada.ca portal DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="can",
            domain="government",
            source_slug="canada_ca",
            supported_languages=('en', 'fr'),
            document_type="government_document",
            extra_metadata={
                "canonical_root": "https://www.canada.ca",
                "title": "Canada.ca portal",
            },
        )


_NATION_SOURCE = CANGovernmentSource()


@dlt.resource(
    name="canada_ca",
    write_disposition="merge",
    primary_key=["canada_ca_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "canada_ca_id": {"data_type": "text"},
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
def canada_ca(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Canada government rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "canada_ca_live_mode_not_implemented",
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
                document_id_key="canada_ca_id",
                default_status="published",
            )
            if row:
                row["canada_ca_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="canada_ca")
def canada_ca_source(language: str | None = None):
    """DLT source for the Canada.ca portal ingestion."""
    return canada_ca(language=language)


__all__ = [
    "CANGovernmentSource",
    "canada_ca",
    "canada_ca_source",
]
