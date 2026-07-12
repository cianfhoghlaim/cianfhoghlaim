"""DLT source for the Boletín Oficial del Estado.

Crawls ``https://www.boe.es`` and emits one row per ``(boe_id, language)`` for
every document available in at least one of the official languages of
Spain.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/esp/law/boe.py`` with
``source_id="european_nations.esp.law.boe"`` and lands in
the DuckLake table ``oideachais.law.european_nations.esp``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/esp/law/<lang>/``.

Reference: ``openspec/changes/2026-07-11-european-nations-ukraine-pipeline-v1/``.
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


class SpainLawSource(NationSource):
    """Boletín Oficial del Estado DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="esp",
            domain="law",
            source_slug="boe",
            supported_languages=('es', 'ca', 'gl', 'eu'),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://www.boe.es",
                "title": "Boletín Oficial del Estado",
            },
        )


_NATION_SOURCE = SpainLawSource()


@dlt.resource(
    name="boe",
    write_disposition="merge",
    primary_key=["boe_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "boe_id": {"data_type": "text"},
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
def boe(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Spain law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "boe_live_mode_not_implemented",
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
                document_id_key="boe_id",
                default_status="published",
            )
            if row:
                row["boe_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="boe")
def boe_source(language: str | None = None):
    """DLT source for the Boletín Oficial del Estado ingestion."""
    return boe(language=language)


__all__ = [
    "SpainLawSource",
    "boe",
    "boe_source",
]
