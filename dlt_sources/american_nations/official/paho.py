"""DLT source for the Pan American Health Organization (Pan American Health Organization).

Crawls the Pan American Health Organization website (`paho.org`) and emits one row per
epidemiological bulletin / publication × language edition (English
/ Spanish / French / Portuguese).
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


class PanAmericanHealthOrganizationSource(NationSource):
    """Pan American Health Organization DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="__paho__",
            domain="medicine",
            source_slug="paho",
            supported_languages=("en", "es", "fr", "pt"),
            document_type="paho_document",
            extra_metadata={
                "canonical_root": "https://www.paho.org",
                "title": "Pan American Health Organization",
            },
        )


_NATION_SOURCE = PAHOSource()


@dlt.resource(
    name="paho",
    write_disposition="merge",
    primary_key=["bulletin_id", "language"],
    columns={
        "bulletin_id": {"data_type": "text"},
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
def paho(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Pan American Health Organization rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "paho_live_mode_not_implemented",
            hint="This v1 scaffold reads from the local cache.",
        )
    languages = (language,) if language else _NATION_SOURCE.supported_languages
    for lang in languages:
        for cache_path in _NATION_SOURCE.iter_local_cache(lang):
            row = row_from_cache(
                cache_path=cache_path,
                nation=_NATION_SOURCE,
                document_id_key="bulletin_id",
                default_status="published",
            )
            if row:
                row["bulletin_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = "paho"
                row["region"] = "americas"
                yield row


@dlt.source(name="paho")
def paho_source(language: str | None = None):
    """DLT source for the Pan American Health Organization ingestion."""
    return paho(language=language)


__all__ = ["PAHOSource", "paho", "paho_source"]
