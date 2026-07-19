"""DLT source for CJEU case law (EU institutional pipeline).

Sibling of :mod:`cianfhoghlaim.dlt.europeanunion.eur_lex.regulations`
emitting one row per ``(case_id, language)`` for every CJEU decision
available on curia.europa.eu.
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

from dlt_sources.european_union._shared import (
    EUInstitutionalSource,
    use_local_scrapes,
)
from dlt_sources.european_union._shared.registries import EU_LANGUAGES

logger = structlog.get_logger(__name__)


class CJEUCaseLawSource(EUInstitutionalSource):
    institution_slug = "cjeu"
    document_type = "case_law"
    default_language = "fr"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://curia.europa.eu",
                "primary_key": ["case_id", "language"],
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


_CJEU_SOURCE = CJEUCaseLawSource()


@dlt.resource(
    name="cjeu_case_law",
    write_disposition="merge",
    primary_key=["case_id", "language"],
    columns={
        "case_id": {"data_type": "text"},
        "language": {"data_type": "text"},
        "title": {"data_type": "text"},
        "judgment_date": {"data_type": "text"},
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
def cjeu_case_law(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield CJEU case-law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "cjeu_case_law_live_mode_not_implemented",
            hint=(
                "This v1 scaffold reads from the local cache. "
                "Live Firecrawl crawl lands in a follow-on change."
            ),
        )
    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        if lang not in _CJEU_SOURCE.supported_languages:
            continue
        for cache_path in _CJEU_SOURCE.iter_local_cache(lang):
            try:
                payload = json.loads(cache_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                logger.warning(
                    "cjeu_cache_parse_failed",
                    path=str(cache_path),
                    error=str(exc),
                )
                continue
            metadata = (
                payload.get("metadata", {})
                if isinstance(payload, dict)
                else {}
            )
            markdown = payload.get("markdown") if isinstance(payload, dict) else ""
            case_id = (
                metadata.get("case_id")
                or metadata.get("celex_id")
                or cache_path.stem
            )
            yield {
                "case_id": case_id,
                "language": lang,
                "title": payload.get("title")
                or metadata.get("title", "")
                if isinstance(payload, dict)
                else "",
                "judgment_date": metadata.get("judgment_date")
                or metadata.get("date"),
                "source_url": metadata.get("sourceURL") or metadata.get("url") or "",
                "content_hash": (
                    f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}"
                    if markdown
                    else ""
                ),
                "document_type": _CJEU_SOURCE.document_type,
                "institution": _CJEU_SOURCE.institution_slug,
                "region": "europeanunion",
                "official_status": metadata.get("official_status", "in_force"),
                "extracted_at": datetime.now(UTC).isoformat(),
                "source": "cjeu",
                "source_file": str(cache_path),
            }


@dlt.source(name="cjeu_case_law")
def cjeu_case_law_source(language: str | None = None):
    """DLT source for the CJEU case-law ingestion."""
    return cjeu_case_law(language=language)


__all__ = ["CJEUCaseLawSource", "cjeu_case_law", "cjeu_case_law_source"]
