"""DLT source for EU Publications Office (publications.europa.eu).

Crawls the Publications Office catalogue and emits one row per
publication × language edition.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
import structlog

from dlt_sources.european_union._shared import EUInstitutionalSource
from dlt_sources.european_union._shared.registries import EU_LANGUAGES
from dlt_sources.european_union.eur_lex.regulations import _row_from_cache

logger = structlog.get_logger(__name__)


class EUPublicationsSource(EUInstitutionalSource):
    institution_slug = "publications_office"
    document_type = "eu_publication"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://publications.europa.eu",
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_EU_PUBLICATIONS_SOURCE = EUPublicationsSource()


@dlt.resource(
    name="eu_publications",
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
def eu_publications(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield EU Publications rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _EU_PUBLICATIONS_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_EU_PUBLICATIONS_SOURCE.institution_slug,
                document_type=_EU_PUBLICATIONS_SOURCE.document_type,
                default_status="published",
            )
            if row:
                # Rename celex_id → publication_id for the
                # Publications Office namespace.
                row["publication_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="eu_publications")
def eu_publications_source(language: str | None = None):
    """DLT source for the EU Publications ingestion."""
    return eu_publications(language=language)


__all__ = ["EUPublicationsSource", "eu_publications", "eu_publications_source"]
