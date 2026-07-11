"""DLT source for the Council of Ministers of Education, Canada.

Crawls ``https://www.cmec.ca`` and emits one row per ``(cmec_id, language)`` for
every document available in at least one of the official languages of
Canada.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/can/education/cmec.py`` with
``source_id="commonwealth.can.education.cmec"`` and lands in the
DuckLake table ``oideachais.education.commonwealth.can``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/can/education/<lang>/``.

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


class CANEducationSource(NationSource):
    """Council of Ministers of Education, Canada DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="can",
            domain="education",
            source_slug="cmec",
            supported_languages=('en', 'fr'),
            document_type="education_document",
            extra_metadata={
                "canonical_root": "https://www.cmec.ca",
                "title": "Council of Ministers of Education, Canada",
            },
        )


_NATION_SOURCE = CANEducationSource()


@dlt.resource(
    name="cmec",
    write_disposition="merge",
    primary_key=["cmec_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "cmec_id": {"data_type": "text"},
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
def cmec(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Canada education rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "cmec_live_mode_not_implemented",
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
                document_id_key="cmec_id",
                default_status="published",
            )
            if row:
                row["cmec_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="cmec")
def cmec_source(language: str | None = None):
    """DLT source for the Council of Ministers of Education, Canada ingestion."""
    return cmec(language=language)


__all__ = [
    "CANEducationSource",
    "cmec",
    "cmec_source",
]
