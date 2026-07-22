"""DLT source for the Government of Slovenia (government, Slovenia).

Crawls ``https://www.gov.si`` and emits one row per ``(gov_portal_svn_id, language)`` for
every document available in at least one of the official languages of
Slovenia.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/svn/government/gov_portal_svn.py`` with
``source_id="european_nations.svn.government.gov_portal_svn"`` and lands in
the DuckLake table ``oideachais.government.european_nations.svn``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/svn/government/<lang>/``.

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


class SloveniaGovernmentSource(NationSource):
    """Government of Slovenia DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="svn",
            domain="government",
            source_slug="gov_portal_svn",
            supported_languages=("sl",),
            document_type="government_document",
            extra_metadata={
                "canonical_root": "https://www.gov.si",
                "title": "Government of Slovenia",
            },
        )


_NATION_SOURCE = SloveniaGovernmentSource()


@dlt.resource(
    name="gov_portal_svn",
    write_disposition="merge",
    primary_key=["gov_portal_svn_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "gov_portal_svn_id": {"data_type": "text"},
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
def gov_portal_svn(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Slovenia government rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "gov_portal_svn_live_mode_not_implemented",
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
                document_id_key="gov_portal_svn_id",
                default_status="published",
            )
            if row:
                row["gov_portal_svn_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="gov_portal_svn")
def gov_portal_svn_source(language: str | None = None):
    """DLT source for the Government of Slovenia ingestion."""
    return gov_portal_svn(language=language)


__all__ = [
    "SloveniaGovernmentSource",
    "gov_portal_svn",
    "gov_portal_svn_source",
]
