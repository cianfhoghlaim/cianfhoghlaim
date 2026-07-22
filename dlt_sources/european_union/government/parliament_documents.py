"""DLT source for European Parliament documents.

Crawls the European Parliament document register
(`europarl.europa.eu`) and emits one row per document × language edition.
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


class ParliamentDocumentsSource(EUInstitutionalSource):
    institution_slug = "parliament"
    document_type = "parliamentary_document"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://www.europarl.europa.eu",
            },
        )


_PARLIAMENT_SOURCE = ParliamentDocumentsSource()


@dlt.resource(
    name="parliament_documents",
    write_disposition="merge",
    primary_key=["document_id", "language"],
    columns={
        "document_id": {"data_type": "text"},
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
def parliament_documents(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Parliament document rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _PARLIAMENT_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_PARLIAMENT_SOURCE.institution_slug,
                document_type=_PARLIAMENT_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["document_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="parliament_documents")
def parliament_documents_source(language: str | None = None):
    """DLT source for the Parliament documents ingestion."""
    return parliament_documents(language=language)


__all__ = [
    "ParliamentDocumentsSource",
    "parliament_documents",
    "parliament_documents_source",
]
