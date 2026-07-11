"""DLT source for the Cyprus Legislation (cyprus.gov.cy) (law, CYP).

Crawls ``https://www.cyprus.gov.cy`` and emits one row per ``(legislation_cyp_id, language)`` for
every document available in at least one of the official languages of
Cyprus.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/cyp/law/legislation_cyp.py`` with
``source_id="european_nations.cyp.law.legislation_cyp"`` and lands in
the DuckLake table ``oideachais.law.european_nations.cyp``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/cyp/law/<lang>/``.

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


class CYPLawSource(NationSource):
    """Cyprus Legislation (cyprus.gov.cy) DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="cyp",
            domain="law",
            source_slug="legislation_cyp",
            supported_languages=("el", "tr",),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://www.cyprus.gov.cy",
                "title": "Cyprus Legislation (cyprus.gov.cy)",
            },
        )


_NATION_SOURCE = CYPLawSource()


@dlt.resource(
    name="legislation_cyp",
    write_disposition="merge",
    primary_key=["legislation_cyp_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "legislation_cyp_id": {"data_type": "text"},
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
def legislation_cyp(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Cyprus law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "legislation_cyp_live_mode_not_implemented",
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
                document_id_key="legislation_cyp_id",
                default_status="in_force",
            )
            if row:
                row["legislation_cyp_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="legislation_cyp")
def legislation_cyp_source(language: str | None = None):
    """DLT source for the Cyprus Legislation (cyprus.gov.cy) ingestion."""
    return legislation_cyp(language=language)


__all__ = [
    "CYPLawSource",
    "legislation_cyp",
    "legislation_cyp_source",
]
