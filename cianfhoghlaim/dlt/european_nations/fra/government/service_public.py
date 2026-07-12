"""DLT source for the Service-Public.fr portal.

Crawls ``https://www.service-public.fr`` and emits one row per ``(service_public_id, language)`` for
every document available in at least one of the official languages of
France.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/fra/government/service_public.py`` with
``source_id="european_nations.fra.government.service_public"`` and lands in
the DuckLake table ``oideachais.government.european_nations.fra``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/fra/government/<lang>/``.

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


class FRAGovernmentSource(NationSource):
    """Service-Public.fr portal DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="fra",
            domain="government",
            source_slug="service_public",
            supported_languages=('fr',),
            document_type="government_document",
            extra_metadata={
                "canonical_root": "https://www.service-public.fr",
                "title": "Service-Public.fr portal",
            },
        )


_NATION_SOURCE = FRAGovernmentSource()


@dlt.resource(
    name="service_public",
    write_disposition="merge",
    primary_key=["service_public_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "service_public_id": {"data_type": "text"},
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
def service_public(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield France government rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "service_public_live_mode_not_implemented",
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
                document_id_key="service_public_id",
                default_status="published",
            )
            if row:
                row["service_public_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="service_public")
def service_public_source(language: str | None = None):
    """DLT source for the Service-Public.fr portal ingestion."""
    return service_public(language=language)


__all__ = [
    "FRAGovernmentSource",
    "service_public",
    "service_public_source",
]
