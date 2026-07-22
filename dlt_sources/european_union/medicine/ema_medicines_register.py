"""DLT source for the European Medicines Agency medicines register.

Crawls the EMA register (`ema.europa.eu`) and emits one row per
centrally authorised medicine × language edition.
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


class EMAMedicinesRegisterSource(EUInstitutionalSource):
    institution_slug = "ema"
    document_type = "epar"
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={"canonical_root": "https://www.ema.europa.eu",
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_EMA_SOURCE = EMAMedicinesRegisterSource()


@dlt.resource(
    name="ema_medicines_register",
    write_disposition="merge",
    primary_key=["medicine_id", "language"],
    columns={
        "medicine_id": {"data_type": "text"},
        "language": {"data_type": "text"},
        "medicine_name": {"data_type": "text"},
        "active_substance": {"data_type": "text"},
        "atc_code": {"data_type": "text"},
        "authorisation_status": {"data_type": "text"},
        "title": {"data_type": "text"},
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
def ema_medicines_register(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield EMA medicines register rows from the canonical cache."""
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        for cache_path in _EMA_SOURCE.iter_local_cache(lang):
            try:
                import json
                payload = json.loads(cache_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning(
                    "ema_cache_parse_failed",
                    path=str(cache_path),
                    error=str(exc),
                )
                continue
            metadata = (
                payload.get("metadata", {}) if isinstance(payload, dict) else {}
            )
            medicine_id = (
                metadata.get("medicine_id")
                or metadata.get("ema_id")
                or cache_path.stem
            )
            yield {
                "medicine_id": medicine_id,
                "language": lang,
                "medicine_name": metadata.get("medicine_name", ""),
                "active_substance": metadata.get("active_substance", ""),
                "atc_code": metadata.get("atc_code", ""),
                "authorisation_status": metadata.get(
                    "authorisation_status", "authorised"
                ),
                "title": payload.get("title")
                or metadata.get("title", "")
                if isinstance(payload, dict)
                else "",
                "source_url": metadata.get("sourceURL") or metadata.get("url") or "",
                "content_hash": (
                    f"sha256:{hash(payload.get('markdown', '')) & 0xFFFFFFFFFFFFFFFF:016x}"
                    if isinstance(payload, dict) and payload.get("markdown")
                    else ""
                ),
                "document_type": _EMA_SOURCE.document_type,
                "institution": _EMA_SOURCE.institution_slug,
                "region": "europeanunion",
                "official_status": metadata.get("official_status", "in_force"),
                "extracted_at": _EMA_SOURCE.default_language
                and metadata.get("extracted_at"),
                "source": "ema",
                "source_file": str(cache_path),
            }


@dlt.source(name="ema_medicines_register")
def ema_medicines_register_source(language: str | None = None):
    """DLT source for the EMA medicines register ingestion."""
    return ema_medicines_register(language=language)


__all__ = [
    "EMAMedicinesRegisterSource",
    "ema_medicines_register",
    "ema_medicines_register_source",
]
