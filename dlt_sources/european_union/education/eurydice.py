"""DLT source for Eurydice (eurydice.eacea.ec.europa.eu).

Crawls the Eurydice network of national education systems and emits
one row per national education-structure entry.
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


class EurydiceSource(EUInstitutionalSource):
    institution_slug = "eurydice"
    document_type = "national_education_structure"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://eurydice.eacea.ec.europa.eu",
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_EURYDICE_SOURCE = EurydiceSource()


@dlt.resource(
    name="eurydice",
    write_disposition="merge",
    primary_key=["country_code", "language"],
    columns={
        "country_code": {"data_type": "text"},
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
def eurydice(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Eurydice rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _EURYDICE_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_EURYDICE_SOURCE.institution_slug,
                document_type=_EURYDICE_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["country_code"] = row.pop("celex_id", cache_path.stem)[:3]
                yield row


@dlt.source(name="eurydice")
def eurydice_source(language: str | None = None):
    """DLT source for the Eurydice ingestion."""
    return eurydice(language=language)


__all__ = ["EurydiceSource", "eurydice", "eurydice_source"]
