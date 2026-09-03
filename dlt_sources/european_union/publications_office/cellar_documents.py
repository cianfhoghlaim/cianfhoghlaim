"""DLT source for the EU CELLAR metadata repository.

Crawls the CELLAR repository (cellar.publications.europa.eu) and emits
one row per resource × language edition.
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


class CellarDocumentsSource(EUInstitutionalSource):
    institution_slug = "cellar"
    document_type = "cellar_resource"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://cellar.publications.europa.eu",
            },
        )


_CELLAR_SOURCE = CellarDocumentsSource()


@dlt.resource(
    name="cellar_documents",
    write_disposition="merge",
    primary_key=["resource_id", "language"],
    columns={
        "resource_id": {"data_type": "text"},
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
def cellar_documents(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield CELLAR rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _CELLAR_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_CELLAR_SOURCE.institution_slug,
                document_type=_CELLAR_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["resource_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="cellar_documents")
def cellar_documents_source(language: str | None = None):
    """DLT source for the EU CELLAR ingestion."""
    return cellar_documents(language=language)


__all__ = ["CellarDocumentsSource", "cellar_documents", "cellar_documents_source"]
