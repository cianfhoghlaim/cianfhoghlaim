"""DLT source for the California Legislative Information.

Crawls ``https://leginfo.legislature.ca.gov`` and emits one row per ``(ca_leginfo_id, language)`` for
every document available in at least one of the official languages of
California.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/americas/us/us_ca/law/ca_leginfo.py`` with
``source_id="americas.California.law.ca_leginfo"`` and lands in the
DuckLake table ``oideachais.law.americas.California``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/americas/California/law/<lang>/``.

Reference: ``openspec/changes/2026-07-11-americas-california-pipeline-v1/``.
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


class US_US_CALawSource(NationSource):
    """California Legislative Information DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="California",
            domain="law",
            source_slug="ca_leginfo",
            supported_languages=('en',),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://leginfo.legislature.ca.gov",
                "title": "California Legislative Information",
            },
        )


_NATION_SOURCE = US_US_CALawSource()


@dlt.resource(
    name="ca_leginfo",
    write_disposition="merge",
    primary_key=["ca_leginfo_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "jurisdiction": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "ca_leginfo_id": {"data_type": "text"},
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
def ca_leginfo(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield California law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "ca_leginfo_live_mode_not_implemented",
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
                document_id_key="ca_leginfo_id",
                default_status="published",
            )
            if row:
                row["ca_leginfo_id"] = row.pop("document_id", cache_path.stem)
                row["jurisdiction"] = _NATION_SOURCE.country_code
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "americas"
                yield row


@dlt.source(name="ca_leginfo")
def ca_leginfo_source(language: str | None = None):
    """DLT source for the California Legislative Information ingestion."""
    return ca_leginfo(language=language)


__all__ = [
    "US_US_CALawSource",
    "ca_leginfo",
    "ca_leginfo_source",
]
