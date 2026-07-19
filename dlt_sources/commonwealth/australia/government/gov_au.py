"""DLT source for the Australia.gov.au portal.

Crawls ``https://www.australia.gov.au`` and emits one row per ``(gov_au_id, language)`` for
every document available in at least one of the official languages of
Australia.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/aus/government/gov_au.py`` with
``source_id="commonwealth.aus.government.gov_au"`` and lands in the
DuckLake table ``oideachais.government.commonwealth.aus``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/aus/government/<lang>/``.

Reference: ``openspec/changes/2026-07-11-commonwealth-pipeline-v1/``.
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


class AustraliaGovernmentSource(NationSource):
    """Australia.gov.au portal DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="aus",
            domain="government",
            source_slug="gov_au",
            supported_languages=('en',),
            document_type="government_document",
            extra_metadata={
                "canonical_root": "https://www.australia.gov.au",
                "title": "Australia.gov.au portal",
            },
        )


_NATION_SOURCE = AustraliaGovernmentSource()


@dlt.resource(
    name="gov_au",
    write_disposition="merge",
    primary_key=["gov_au_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "gov_au_id": {"data_type": "text"},
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
def gov_au(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Australia government rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "gov_au_live_mode_not_implemented",
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
                document_id_key="gov_au_id",
                default_status="published",
            )
            if row:
                row["gov_au_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="gov_au")
def gov_au_source(language: str | None = None):
    """DLT source for the Australia.gov.au portal ingestion."""
    return gov_au(language=language)


__all__ = [
    "AustraliaGovernmentSource",
    "gov_au",
    "gov_au_source",
]
