"""DLT source for the European Centre for Disease Prevention & Control.

Crawls the ECDC surveillance atlas (`ecdc.europa.eu`) and the
health-alerts feed, emitting one row per surveillance dataset /
alert × language edition.
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


class ECDCSurveillanceSource(EUInstitutionalSource):
    institution_slug = "ecdc"
    document_type = "surveillance_dataset"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={"canonical_root": "https://www.ecdc.europa.eu",
                "language_availability": {"en": "full", "ga": "partial"},
            },
        )


_ECDC_SOURCE = ECDCSurveillanceSource()


@dlt.resource(
    name="ecdc_surveillance",
    write_disposition="merge",
    primary_key=["dataset_id", "language"],
    columns={
        "dataset_id": {"data_type": "text"},
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
def ecdc_surveillance(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield ECDC surveillance rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _ECDC_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_ECDC_SOURCE.institution_slug,
                document_type=_ECDC_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["dataset_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="ecdc_surveillance")
def ecdc_surveillance_source(language: str | None = None):
    """DLT source for the ECDC surveillance ingestion."""
    return ecdc_surveillance(language=language)


__all__ = ["ECDCSurveillanceSource", "ecdc_surveillance", "ecdc_surveillance_source"]
