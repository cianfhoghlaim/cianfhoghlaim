"""DLT source for EU treaties (TEU, TFEU, Charter, accession treaties).

Sibling of :mod:`cianfhoghlaim.dlt.europeanunion.eur_lex.regulations`
emitting one row per ``(celex_id, language)`` for every EU treaty
available on eur-lex.europa.eu.
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


class EURLexTreatiesSource(EUInstitutionalSource):
    institution_slug = "eur_lex"
    document_type = "treaty"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_EUR_LEX_TREATIES_SOURCE = EURLexTreatiesSource()


@dlt.resource(
    name="eur_lex_treaties",
    write_disposition="merge",
    primary_key=["celex_id", "language"],
    columns={
        "celex_id": {"data_type": "text"},
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
def eur_lex_treaties(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield EU treaty rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _EUR_LEX_TREATIES_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_EUR_LEX_TREATIES_SOURCE.institution_slug,
                document_type=_EUR_LEX_TREATIES_SOURCE.document_type,
                default_status="in_force",
            )
            if row:
                yield row


@dlt.source(name="eur_lex_treaties")
def eur_lex_treaties_source(language: str | None = None):
    """DLT source for the EU treaties ingestion."""
    return eur_lex_treaties(language=language)


__all__ = ["EURLexTreatiesSource", "eur_lex_treaties", "eur_lex_treaties_source"]
