"""DLT source for the South African Health Products Regulatory Authority.

Crawls ``https://www.sahpra.org.za`` and emits one row per ``(sahpra_id, language)`` for
every document available in at least one of the official languages of
South Africa.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/zaf/medicine/sahpra.py`` with
``source_id="commonwealth.zaf.medicine.sahpra"`` and lands in the
DuckLake table ``oideachais.medicine.commonwealth.zaf``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/zaf/medicine/<lang>/``.

Reference: ``openspec/changes/2026-07-11-commonwealth-pipeline-v1/``.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_nations._shared.nation_source import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class SouthAfricaMedicineSource(NationSource):
    """South African Health Products Regulatory Authority DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="zaf",
            domain="medicine",
            source_slug="sahpra",
            supported_languages=('en', 'af', 'zu', 'xh', 'nso', 'tn', 'st', 'ts', 'ss', 've', 'nr'),
            document_type="medicine_document",
            extra_metadata={
                "canonical_root": "https://www.sahpra.org.za",
                "title": "South African Health Products Regulatory Authority",
            },
        )


_NATION_SOURCE = SouthAfricaMedicineSource()


@dlt.resource(
    name="sahpra",
    write_disposition="merge",
    primary_key=["sahpra_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "sahpra_id": {"data_type": "text"},
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
def sahpra(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield South Africa medicine rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "sahpra_live_mode_not_implemented",
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
                document_id_key="sahpra_id",
                default_status="published",
            )
            if row:
                row["sahpra_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="sahpra")
def sahpra_source(language: str | None = None):
    """DLT source for the South African Health Products Regulatory Authority ingestion."""
    return sahpra(language=language)


__all__ = [
    "SouthAfricaMedicineSource",
    "sahpra",
    "sahpra_source",
]
