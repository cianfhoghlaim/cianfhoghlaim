"""DLT source for the National Medical Commission.

Crawls ``https://www.nmc.org.in`` and emits one row per ``(nmc_id, language)`` for
every document available in at least one of the official languages of
India.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/ind/medicine/nmc.py`` with
``source_id="commonwealth.ind.medicine.nmc"`` and lands in the
DuckLake table ``oideachais.medicine.commonwealth.ind``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/ind/medicine/<lang>/``.

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


class IndiaMedicineSource(NationSource):
    """National Medical Commission DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="ind",
            domain="medicine",
            source_slug="nmc",
            supported_languages=('en', 'hi'),
            document_type="medicine_document",
            extra_metadata={
                "canonical_root": "https://www.nmc.org.in",
                "title": "National Medical Commission",
            },
        )


_NATION_SOURCE = IndiaMedicineSource()


@dlt.resource(
    name="nmc",
    write_disposition="merge",
    primary_key=["nmc_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "nmc_id": {"data_type": "text"},
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
def nmc(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield India medicine rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "nmc_live_mode_not_implemented",
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
                document_id_key="nmc_id",
                default_status="published",
            )
            if row:
                row["nmc_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="nmc")
def nmc_source(language: str | None = None):
    """DLT source for the National Medical Commission ingestion."""
    return nmc(language=language)


__all__ = [
    "IndiaMedicineSource",
    "nmc",
    "nmc_source",
]
