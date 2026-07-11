"""DLT source for the Seimas of the Republic of Lithuania (law, LTU).

Crawls ``https://www.e-seimas.lrs.lt`` and emits one row per ``(statute_book_id, language)`` for
every document available in at least one of the official languages of
Lithuania.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/ltu/law/statute_book.py`` with
``source_id="european_nations.ltu.law.statute_book"`` and lands in
the DuckLake table ``oideachais.law.european_nations.ltu``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/ltu/law/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_nations._shared import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class LTULawSource(NationSource):
    """Seimas of the Republic of Lithuania DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="ltu",
            domain="law",
            source_slug="statute_book",
            supported_languages=("lt",),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://www.e-seimas.lrs.lt",
                "title": "Seimas of the Republic of Lithuania",
            },
        )


_NATION_SOURCE = LTULawSource()


@dlt.resource(
    name="statute_book",
    write_disposition="merge",
    primary_key=["statute_book_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "statute_book_id": {"data_type": "text"},
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
def statute_book(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Lithuania law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "statute_book_live_mode_not_implemented",
            hint="This v1 scaffold reads from the local cache.",
        )
    languages = (language,) if language else _NATION_SOURCE.supported_languages
    for lang in languages:
        if lang not in _NATION_SOURCE.supported_languages:
            continue
        for cache_path in _NATION_SOURCE.iter_local_cache(lang):
            row = row_from_cache(
                cache_path=cache_path,
                nation=_NATION_SOURCE,
                document_id_key="statute_book_id",
                default_status="in_force",
            )
            if row:
                row["statute_book_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="statute_book")
def statute_book_source(language: str | None = None):
    """DLT source for the Seimas of the Republic of Lithuania ingestion."""
    return statute_book(language=language)


__all__ = [
    "LTULawSource",
    "statute_book",
    "statute_book_source",
]
