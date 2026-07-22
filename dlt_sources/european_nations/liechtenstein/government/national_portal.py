"""DLT source for Regierung des Fuerstentums Liechtenstein.

Crawls ``https://www.regierung.li`` and emits one row per ``(national_portal_id, language)`` for
every document available in at least one of the official languages of
Regierung des Fuerstentums Liechtenstein.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/lie/government/national_portal.py`` with
``source_id="european_nations.lie.government.national_portal"`` and lands in
the DuckLake table ``oideachais.government.european_nations.lie``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/lie/government/<lang>/``.

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


class LIENationalPortalSource(NationSource):
    """Regierung des Fuerstentums Liechtenstein DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="lie",
            domain="government",
            source_slug="national_portal",
            supported_languages=('de',),
            document_type="government_document",
            extra_metadata={
                "canonical_root": "https://www.regierung.li",
                "title": "Regierung des Fuerstentums Liechtenstein",
            },
        )


_NATION_SOURCE = LIENationalPortalSource()


@dlt.resource(
    name="national_portal",
    write_disposition="merge",
    primary_key=["national_portal_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "national_portal_id": {"data_type": "text"},
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
def national_portal(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Regierung des Fuerstentums Liechtenstein rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "national_portal_live_mode_not_implemented",
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
                document_id_key="national_portal_id",
                default_status="published",
            )
            if row:
                row["national_portal_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="national_portal")
def national_portal_source(language: str | None = None):
    """DLT source for the Regierung des Fuerstentums Liechtenstein ingestion."""
    return national_portal(language=language)


__all__ = [
    "LIENationalPortalSource",
    "national_portal",
    "national_portal_source",
]
