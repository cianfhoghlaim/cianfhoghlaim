"""DLT source for Cedefop (cedefop.europa.eu).

Crawls the European Centre for the Development of Vocational Training
catalogue and emits one row per resource × language edition.
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


class CedefopSource(EUInstitutionalSource):
    institution_slug = "cedefop"
    document_type = "vocational_training_resource"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={"canonical_root": "https://cedefop.europa.eu",
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_CEDEFOP_SOURCE = CedefopSource()


@dlt.resource(
    name="cedefop",
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
def cedefop(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Cedefop rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _CEDEFOP_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_CEDEFOP_SOURCE.institution_slug,
                document_type=_CEDEFOP_SOURCE.document_type,
                default_status="published",
            )
            if row:
                row["resource_id"] = row.pop("celex_id", cache_path.stem)
                yield row


@dlt.source(name="cedefop")
def cedefop_source(language: str | None = None):
    """DLT source for the Cedefop ingestion."""
    return cedefop(language=language)


__all__ = ["CedefopSource", "cedefop", "cedefop_source"]
