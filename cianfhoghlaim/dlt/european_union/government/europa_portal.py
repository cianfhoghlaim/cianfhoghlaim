"""DLT source for the `europa.eu` portal.

Crawls the Europa portal landing page + the language picker, emitting
one row per portal entry × language edition.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_union._shared import EUInstitutionalSource
from cianfhoghlaim.dlt.european_union._shared.registries import EU_LANGUAGES
from cianfhoghlaim.dlt.european_union.eur_lex.regulations import _row_from_cache

logger = structlog.get_logger(__name__)


class EuropaPortalSource(EUInstitutionalSource):
    institution_slug = "europa_portal"
    document_type = "portal_entry"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={"canonical_root": "https://europa.eu"},
        )


_EUROPA_PORTAL_SOURCE = EuropaPortalSource()


@dlt.resource(
    name="europa_portal",
    write_disposition="merge",
    primary_key=["entry_id", "language"],
    columns={
        "entry_id": {"data_type": "text"},
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
def europa_portal(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Europa portal rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _EUROPA_PORTAL_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_EUROPA_PORTAL_SOURCE.institution_slug,
                document_type=_EUROPA_PORTAL_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["entry_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="europa_portal")
def europa_portal_source(language: str | None = None):
    """DLT source for the Europa portal ingestion."""
    return europa_portal(language=language)


__all__ = ["EuropaPortalSource", "europa_portal", "europa_portal_source"]
