"""DLT source for the Gobierno Bolivariano de Venezuela portal.

Crawls ``http://www.gobiernoenlinea.gob.ve`` and emits one row per ``(gov_ve_id, language)`` for
every document available in at least one of the official languages of
Venezuela.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/americas/Venezuela/government/gov_ve.py`` with
``source_id="americas.Venezuela.government.gov_ve"`` and lands in the
DuckLake table ``oideachais.government.americas.Venezuela``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/americas/Venezuela/government/<lang>/``.

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


class VENGovernmentSource(NationSource):
    """Gobierno Bolivariano de Venezuela portal DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="Venezuela",
            domain="government",
            source_slug="gov_ve",
            supported_languages=('es',),
            document_type="government_document",
            extra_metadata={
                "canonical_root": "http://www.gobiernoenlinea.gob.ve",
                "title": "Gobierno Bolivariano de Venezuela portal",
            },
        )


_NATION_SOURCE = VENGovernmentSource()


@dlt.resource(
    name="gov_ve",
    write_disposition="merge",
    primary_key=["gov_ve_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "jurisdiction": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "gov_ve_id": {"data_type": "text"},
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
def gov_ve(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Venezuela government rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "gov_ve_live_mode_not_implemented",
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
                document_id_key="gov_ve_id",
                default_status="published",
            )
            if row:
                row["gov_ve_id"] = row.pop("document_id", cache_path.stem)
                row["jurisdiction"] = _NATION_SOURCE.country_code
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "americas"
                yield row


@dlt.source(name="gov_ve")
def gov_ve_source(language: str | None = None):
    """DLT source for the Gobierno Bolivariano de Venezuela portal ingestion."""
    return gov_ve(language=language)


__all__ = [
    "VENGovernmentSource",
    "gov_ve",
    "gov_ve_source",
]
