"""DLT source for the Government of Estonia (government, Estonia).

Crawls ``https://www.valitsus.ee`` and emits one row per ``(gov_portal_est_id, language)`` for
every document available in at least one of the official languages of
Estonia.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/est/government/gov_portal_est.py`` with
``source_id="european_nations.est.government.gov_portal_est"`` and lands in
the DuckLake table ``oideachais.government.european_nations.est``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/est/government/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
import structlog

from dlt_sources.european_nations._shared import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class EstoniaGovernmentSource(NationSource):
    """Government of Estonia DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="est",
            domain="government",
            source_slug="gov_portal_est",
            supported_languages=("et",),
            document_type="government_document",
            extra_metadata={
                "canonical_root": "https://www.valitsus.ee",
                "title": "Government of Estonia",
            },
        )


_NATION_SOURCE = EstoniaGovernmentSource()


@dlt.resource(
    name="gov_portal_est",
    write_disposition="merge",
    primary_key=["gov_portal_est_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "gov_portal_est_id": {"data_type": "text"},
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
def gov_portal_est(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Estonia government rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "gov_portal_est_live_mode_not_implemented",
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
                document_id_key="gov_portal_est_id",
                default_status="published",
            )
            if row:
                row["gov_portal_est_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="gov_portal_est")
def gov_portal_est_source(language: str | None = None):
    """DLT source for the Government of Estonia ingestion."""
    return gov_portal_est(language=language)


__all__ = [
    "EstoniaGovernmentSource",
    "gov_portal_est",
    "gov_portal_est_source",
]
