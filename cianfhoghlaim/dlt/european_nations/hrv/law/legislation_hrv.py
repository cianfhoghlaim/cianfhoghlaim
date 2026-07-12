"""DLT source for the Narodne novine (Official Gazette of Croatia) (law, HRV).

Crawls ``https://www.nn.hr`` and emits one row per ``(legislation_hrv_id, language)`` for
every document available in at least one of the official languages of
Croatia.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/hrv/law/legislation_hrv.py`` with
``source_id="european_nations.hrv.law.legislation_hrv"`` and lands in
the DuckLake table ``oideachais.law.european_nations.hrv``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/hrv/law/<lang>/``.

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


class HRVLawSource(NationSource):
    """Narodne novine (Official Gazette of Croatia) DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="hrv",
            domain="law",
            source_slug="legislation_hrv",
            supported_languages=("hr",),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://www.nn.hr",
                "title": "Narodne novine (Official Gazette of Croatia)",
            },
        )


_NATION_SOURCE = HRVLawSource()


@dlt.resource(
    name="legislation_hrv",
    write_disposition="merge",
    primary_key=["legislation_hrv_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "legislation_hrv_id": {"data_type": "text"},
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
def legislation_hrv(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Croatia law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "legislation_hrv_live_mode_not_implemented",
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
                document_id_key="legislation_hrv_id",
                default_status="in_force",
            )
            if row:
                row["legislation_hrv_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="legislation_hrv")
def legislation_hrv_source(language: str | None = None):
    """DLT source for the Narodne novine (Official Gazette of Croatia) ingestion."""
    return legislation_hrv(language=language)


__all__ = [
    "HRVLawSource",
    "legislation_hrv",
    "legislation_hrv_source",
]
