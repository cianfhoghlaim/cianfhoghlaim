"""DLT source for Eurostat (ec.europa.eu/eurostat).

Crawls the Eurostat data browser and emits one row per dataset
metadata entry × language edition.
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


class EurostatSource(EUInstitutionalSource):
    institution_slug = "eurostat"
    document_type = "dataset_metadata"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://ec.europa.eu/eurostat",
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_EUROSTAT_SOURCE = EurostatSource()


@dlt.resource(
    name="eurostat",
    write_disposition="merge",
    primary_key=["dataset_id", "language"],
    columns={
        "dataset_id": {"data_type": "text"},
        "language": {"data_type": "text"},
        "title": {"data_type": "text"},
        "last_updated": {"data_type": "text"},
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
def eurostat(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Eurostat rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _EUROSTAT_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_EUROSTAT_SOURCE.institution_slug,
                document_type=_EUROSTAT_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["dataset_id"] = row.pop("celex_id", cache_path.stem)
                row["last_updated"] = row.pop("publication_date", None)
                yield row


@dlt.source(name="eurostat")
def eurostat_source(language: str | None = None):
    """DLT source for the Eurostat ingestion."""
    return eurostat(language=language)


__all__ = ["EurostatSource", "eurostat", "eurostat_source"]
