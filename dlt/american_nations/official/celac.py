"""DLT source for the Community of Latin American and Caribbean States (Community of Latin American and Caribbean States)."""
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


class CELACSource(NationSource):
    """Community of Latin American and Caribbean States DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="__celac__",
            domain="government",
            source_slug="celac",
            supported_languages=("es", "pt", "en", "fr"),
            document_type="celac_document",
            extra_metadata={
                "canonical_root": "https://www.celac.org",
                "title": "Community of Latin American and Caribbean States",
            },
        )


_NATION_SOURCE = CELACSource()


@dlt.resource(
    name="celac",
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
def celac(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Community of Latin American and Caribbean States rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "celac_live_mode_not_implemented",
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
                row["institution"] = "celac"
                row["region"] = "americas"
                yield row


@dlt.source(name="celac")
def celac_source(language: str | None = None):
    """DLT source for the Community of Latin American and Caribbean States ingestion."""
    return celac(language=language)


__all__ = ["CELACSource", "celac", "celac_source"]
