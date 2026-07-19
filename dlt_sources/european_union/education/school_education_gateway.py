"""DLT source for the School Education Gateway (school-education.ec.europa.eu).

Crawls the European School Education Gateway and emits one row per
resource × language edition.
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


class SchoolEducationGatewaySource(EUInstitutionalSource):
    institution_slug = "school_education_gateway"
    document_type = "school_education_resource"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://school-education.ec.europa.eu",
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_SEG_SOURCE = SchoolEducationGatewaySource()


@dlt.resource(
    name="school_education_gateway",
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
def school_education_gateway(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield School Education Gateway rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _SEG_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_SEG_SOURCE.institution_slug,
                document_type=_SEG_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["resource_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="school_education_gateway")
def school_education_gateway_source(language: str | None = None):
    """DLT source for the School Education Gateway ingestion."""
    return school_education_gateway(language=language)


__all__ = [
    "SchoolEducationGatewaySource",
    "school_education_gateway",
    "school_education_gateway_source",
]
