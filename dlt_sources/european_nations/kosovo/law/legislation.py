"""DLT source for the Legislation of Kosovo.

Crawls ``https://kuvendikosoves.org`` and emits one row per ``(legislation_id, language)``
for every document available in at least one of the official
languages of Kosovo.

Per the canonical
[`cross-region-pipeline`](../../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/xkx/law/legislation.py`` with
``source_id="european_nations.xkx.law.legislation"`` and lands in
the DuckLake table ``oideachais.law.european_nations.xkx``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/xkx/law/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
import structlog

from dlt_sources.european_nations._shared import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class XKXLegislationSource(NationSource):
    """Legislation of Kosovo DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="xkx",
            domain="law",
            source_slug="legislation",
            supported_languages=('sq', 'sr'),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://kuvendikosoves.org",
                "title": "Legislation of Kosovo",
            },
        )


_NATION_SOURCE = XKXLegislationSource()


@dlt.resource(
    name="legislation",
    write_disposition="merge",
    primary_key=["legislation_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "legislation_id": {"data_type": "text"},
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
def legislation(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Kosovo Legislation rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "legislation_live_mode_not_implemented",
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
                document_id_key="legislation_id",
                default_status="published",
            )
            if row:
                row["legislation_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="legislation")
def legislation_source(language: str | None = None):
    """DLT source for the Legislation of Kosovo ingestion."""
    return legislation(language=language)


__all__ = [
    "XKXLegislationSource",
    "legislation",
    "legislation_source",
]
