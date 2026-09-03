"""DLT source for the Commonwealth Foundation.

Crawls the Commonwealth Foundation website
(`commonwealthfoundation.com`) and emits one row per
publication × language edition.
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


class CommonwealthFoundationSource(NationSource):
    """Commonwealth Foundation DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="__commonwealth__",
            domain="government",
            source_slug="commonwealth_foundation",
            supported_languages=("en",),
            document_type="commonwealth_foundation_document",
            extra_metadata={
                "canonical_root": "https://commonwealthfoundation.com",
                "title": "Commonwealth Foundation",
            },
        )


_NATION_SOURCE = CommonwealthFoundationSource()


@dlt.resource(
    name="commonwealth_foundation",
    write_disposition="merge",
    primary_key=["publication_id", "language"],
    columns={
        "publication_id": {"data_type": "text"},
        "language": {"data_type": "text"},
        "title": {"data_type": "text"},
        "publication_date": {"data_type": "text"},
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
def commonwealth_foundation(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Commonwealth Foundation rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "commonwealth_foundation_live_mode_not_implemented",
            hint="This v1 scaffold reads from the local cache.",
        )
    languages = (language,) if language else _NATION_SOURCE.supported_languages
    for lang in languages:
        for cache_path in _NATION_SOURCE.iter_local_cache(lang):
            row = row_from_cache(
                cache_path=cache_path,
                nation=_NATION_SOURCE,
                document_id_key="publication_id",
                default_status="published",
            )
            if row:
                row["publication_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = "commonwealth_foundation"
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="commonwealth_foundation")
def commonwealth_foundation_source(language: str | None = None):
    """DLT source for the Commonwealth Foundation ingestion."""
    return commonwealth_foundation(language=language)


__all__ = [
    "CommonwealthFoundationSource",
    "commonwealth_foundation",
    "commonwealth_foundation_source",
]
