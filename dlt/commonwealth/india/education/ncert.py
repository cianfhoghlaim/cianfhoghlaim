"""DLT source for the National Council of Educational Research and Training.

Crawls ``https://ncert.nic.in`` and emits one row per ``(ncert_id, language)`` for
every document available in at least one of the official languages of
India.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/ind/education/ncert.py`` with
``source_id="commonwealth.ind.education.ncert"`` and lands in the
DuckLake table ``oideachais.education.commonwealth.ind``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/ind/education/<lang>/``.

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


class IndiaEducationSource(NationSource):
    """National Council of Educational Research and Training DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="ind",
            domain="education",
            source_slug="ncert",
            supported_languages=('en', 'hi'),
            document_type="education_document",
            extra_metadata={
                "canonical_root": "https://ncert.nic.in",
                "title": "National Council of Educational Research and Training",
            },
        )


_NATION_SOURCE = IndiaEducationSource()


@dlt.resource(
    name="ncert",
    write_disposition="merge",
    primary_key=["ncert_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "ncert_id": {"data_type": "text"},
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
def ncert(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield India education rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "ncert_live_mode_not_implemented",
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
                document_id_key="ncert_id",
                default_status="published",
            )
            if row:
                row["ncert_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="ncert")
def ncert_source(language: str | None = None):
    """DLT source for the National Council of Educational Research and Training ingestion."""
    return ncert(language=language)


__all__ = [
    "IndiaEducationSource",
    "ncert",
    "ncert_source",
]
