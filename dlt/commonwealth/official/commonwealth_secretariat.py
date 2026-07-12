"""DLT source for the Commonwealth Secretariat.

Crawls the Commonwealth Secretariat website
(`thecommonwealth.org`) and emits one row per press release /
publication × language edition.
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_nations._shared.nation_source import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class CommonwealthSecretariatSource(NationSource):
    """Commonwealth Secretariat DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="__commonwealth__",
            domain="government",
            source_slug="commonwealth_secretariat",
            supported_languages=("en",),
            document_type="commonwealth_secretariat_document",
            extra_metadata={
                "canonical_root": "https://thecommonwealth.org",
                "title": "Commonwealth Secretariat",
            },
        )


_NATION_SOURCE = CommonwealthSecretariatSource()


@dlt.resource(
    name="commonwealth_secretariat",
    write_disposition="merge",
    primary_key=["press_release_id", "language"],
    columns={
        "press_release_id": {"data_type": "text"},
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
def commonwealth_secretariat(
    language: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield Commonwealth Secretariat rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "commonwealth_secretariat_live_mode_not_implemented",
            hint="This v1 scaffold reads from the local cache.",
        )
    languages = (language,) if language else _NATION_SOURCE.supported_languages
    for lang in languages:
        for cache_path in _NATION_SOURCE.iter_local_cache(lang):
            row = row_from_cache(
                cache_path=cache_path,
                nation=_NATION_SOURCE,
                document_id_key="press_release_id",
                default_status="published",
            )
            if row:
                row["press_release_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = "commonwealth_secretariat"
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="commonwealth_secretariat")
def commonwealth_secretariat_source(language: str | None = None):
    """DLT source for the Commonwealth Secretariat ingestion."""
    return commonwealth_secretariat(language=language)


__all__ = [
    "CommonwealthSecretariatSource",
    "commonwealth_secretariat",
    "commonwealth_secretariat_source",
]
