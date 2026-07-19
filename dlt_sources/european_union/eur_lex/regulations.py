"""DLT source for EUR-Lex regulations (EU institutional pipeline).

Crawls `eur-lex.europa.eu` for EU regulations and emits one row per
``(celex_id, language)``. The canonical CELEX ID is the primary key
(merged with language to avoid collisions across language editions).

Per the cross-region contract this source lives at
``dlt/european_union/eur_lex/regulations.py`` with
``source_id="europeanunion.law.eur_lex_regulations"`` and lands in the
DuckLake table ``oideachais.law.europeanunion.eur_lex``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/eu/eur_lex/<lang>/``.

Reference: ``openspec/specs/european-union-official-language-pipeline/spec.md``
"""
from __future__ import annotations

import json
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_union._shared import (
    EUInstitutionalSource,
    use_local_scrapes,
)
from cianfhoghlaim.dlt.european_union._shared.registries import (
    EU_LANGUAGES,
)

logger = structlog.get_logger(__name__)


EUR_LEX_REGULATIONS_INSTITUTION_SLUG = "eur_lex"
EUR_LEX_REGULATIONS_DOCUMENT_TYPE = "regulation"


class EURLexRegulationsSource(EUInstitutionalSource):
    """EUR-Lex regulations source (24 EU official languages).

    Subclasses :class:`EUInstitutionalSource` and inherits the
    canonical 24-language partition. The default language is
    English (the EUR-Lex default edition), and every row carries
    ``institution="eur_lex"`` + ``document_type="regulation"`` +
    ``official_status="in_force"``.
    """

    institution_slug = EUR_LEX_REGULATIONS_INSTITUTION_SLUG
    document_type = EUR_LEX_REGULATIONS_DOCUMENT_TYPE
    default_language = "en"

    def __init__(self) -> None:
        super().__init__(
            institution_slug=self.institution_slug,
            supported_languages=EU_LANGUAGES,
            default_language=self.default_language,
            document_type=self.document_type,
            extra_metadata={
                "canonical_root": "https://eur-lex.europa.eu",
                "primary_key": ["celex_id", "language"],
                "language_availability": {"en": "full", "ga": "full"},
            },
        )


# Module-level singleton so the @dlt.source decorator can reference
# the canonical contract.
_EUR_LEX_REGULATIONS_SOURCE = EURLexRegulationsSource()


def _row_from_cache(
    cache_path: Path,
    language: str,
    institution: str,
    document_type: str,
    default_status: str,
) -> dict[str, Any]:
    """Parse a single EUR-Lex cache JSON snapshot into a DLT row.

    Cache files follow the canonical Firecrawl shape
    (``markdown`` + ``metadata`` + ``sourceURL``); the parser falls
    back to filename regex for the ``celex_id`` extraction.
    """
    try:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(
            "eur_lex_regulations_cache_parse_failed",
            path=str(cache_path),
            error=str(exc),
        )
        return {}

    metadata = payload.get("metadata") if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}

    source_url = metadata.get("sourceURL") or metadata.get("url") or ""
    title = payload.get("title") or metadata.get("title") or ""
    markdown = payload.get("markdown") or ""

    # CELEX IDs are 3-letter sector + year + 4-digit ordinal (e.g.
    # 32024R0903 for Regulation (EU) 2024/903). Fall back to the
    # filename stem if the URL doesn't carry one.
    celex_id = metadata.get("celex_id") or metadata.get("celex")
    if not celex_id and source_url:
        for token in source_url.split("?")[0].split("/"):
            if token[:3].isalpha() and token[3:].isdigit() and len(token) >= 8:
                celex_id = token.upper()
                break
    if not celex_id:
        celex_id = cache_path.stem.upper()

    content_hash = (
        f"sha256:{hash(markdown) & 0xFFFFFFFFFFFFFFFF:016x}"
        if markdown
        else ""
    )
    publication_date = metadata.get("publication_date") or metadata.get(
        "oj_publication_date"
    )

    return {
        "celex_id": celex_id,
        "language": language,
        "title": title,
        "publication_date": publication_date,
        "source_url": source_url,
        "content_hash": content_hash,
        "document_type": document_type,
        "institution": institution,
        "region": "european_union",
        "official_status": metadata.get("official_status") or default_status,
        "extracted_at": datetime.now(UTC).isoformat(),
        "source": "eur_lex",
        "source_file": str(cache_path),
    }


@dlt.resource(
    name="eur_lex_regulations",
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
def eur_lex_regulations(
    language: str | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield EUR-Lex regulation rows from the canonical cache.

    Args:
        language: optional filter (one of the 24 EU official language
            codes). Defaults to ``None`` (all languages).
    """
    if not use_local_scrapes():
        logger.warning(
            "eur_lex_regulations_live_mode_not_implemented",
            hint=(
                "This v1 scaffold reads from the local cache. "
                "Live Firecrawl crawl lands in a follow-on change."
            ),
        )

    languages = (language,) if language is not None else EU_LANGUAGES
    for lang in languages:
        if lang not in _EUR_LEX_REGULATIONS_SOURCE.supported_languages:
            continue
        for cache_path in _EUR_LEX_REGULATIONS_SOURCE.iter_local_cache(lang):
            row = _row_from_cache(
                cache_path=cache_path,
                language=lang,
                institution=_EUR_LEX_REGULATIONS_SOURCE.institution_slug,
                document_type=_EUR_LEX_REGULATIONS_SOURCE.document_type,
                default_status="in_force",
            )
            if row:
                yield row


@dlt.source(name="eur_lex_regulations")
def eur_lex_regulations_source(
    language: str | None = None,
):
    """DLT source for the EUR-Lex regulations ingestion.

    Args:
        language: optional filter (one of the 24 EU official language
            codes). Defaults to ``None`` (all languages).
    """
    return eur_lex_regulations(language=language)


__all__ = [
    "EURLexRegulationsSource",
    "EUR_LEX_REGULATIONS_INSTITUTION_SLUG",
    "EUR_LEX_REGULATIONS_DOCUMENT_TYPE",
    "eur_lex_regulations",
    "eur_lex_regulations_source",
]
