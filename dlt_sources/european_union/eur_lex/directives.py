"""DLT source for EUR-Lex directives (EU institutional pipeline).

Sibling of :mod:`cianfhoghlaim.dlt.europeanunion.eur_lex.regulations`
emitting one row per ``(celex_id, language)`` for every EU directive
available on eur-lex.europa.eu.
"""
from __future__ import annotations
import dlt


import json
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

from dlt_sources.european_union._shared import EUInstitutionalSource
from dlt_sources.european_union._shared.registries import EU_LANGUAGES
from dlt_sources.european_union.eur_lex.regulations import _row_from_cache

logger = structlog.get_logger(__name__)


class EURLexDirectivesSource(EUInstitutionalSource):
    institution_slug = "eur_lex"
    document_type = "directive"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={"canonical_root": "https://eur-lex.europa.eu",
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_EUR_LEX_DIRECTIVES_SOURCE = EURLexDirectivesSource()


@dlt.resource(
    name="eur_lex_directives",
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
def eur_lex_directives(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield EUR-Lex directive rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _EUR_LEX_DIRECTIVES_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_EUR_LEX_DIRECTIVES_SOURCE.institution_slug,
                document_type=_EUR_LEX_DIRECTIVES_SOURCE.document_type,
                default_status="in_force",
            )
            if row:
                yield row


@dlt.source(name="eur_lex_directives")
def eur_lex_directives_source(language: str | None = None):
    """DLT source for the EUR-Lex directives ingestion."""
    return eur_lex_directives(language=language)


__all__ = ["EURLexDirectivesSource", "eur_lex_directives", "eur_lex_directives_source"]
