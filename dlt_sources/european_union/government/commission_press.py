"""DLT source for the European Commission press releases.

Crawls the European Commission press release database
(`ec.europa.eu/commission/presscorner`) and emits one row per press
release × language edition.
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


class CommissionPressSource(EUInstitutionalSource):
    institution_slug = "commission"
    document_type = "press_release"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://ec.europa.eu/commission/presscorner",
            },
        )


_COMMISSION_PRESS_SOURCE = CommissionPressSource()


@dlt.resource(
    name="commission_press",
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
def commission_press(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Commission press-release rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _COMMISSION_PRESS_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_COMMISSION_PRESS_SOURCE.institution_slug,
                document_type=_COMMISSION_PRESS_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["press_release_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="commission_press")
def commission_press_source(language: str | None = None):
    """DLT source for the Commission press ingestion."""
    return commission_press(language=language)


__all__ = [
    "CommissionPressSource",
    "commission_press",
    "commission_press_source",
]
