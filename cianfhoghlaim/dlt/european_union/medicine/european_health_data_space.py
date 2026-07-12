"""DLT source for the European Health Data Space (EHDS).

Crawls the EHDS portal (`healthdata.europa.eu`) and emits one row per
dataset × language edition.
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


class EHDSSource(EUInstitutionalSource):
    institution_slug = "ehds"
    document_type = "ehds_dataset"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://www.european-health-data-space.europa.eu",
            },
        )


_EHDS_SOURCE = EHDSSource()


@dlt.resource(
    name="ehds",
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
def ehds(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield EHDS rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _EHDS_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_EHDS_SOURCE.institution_slug,
                document_type=_EHDS_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["dataset_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="ehds")
def european_health_data_space_source(language: str | None = None):
    """DLT source for the EHDS ingestion."""
    return ehds(language=language)


__all__ = ["EHDSSource", "ehds", "european_health_data_space_source"]
