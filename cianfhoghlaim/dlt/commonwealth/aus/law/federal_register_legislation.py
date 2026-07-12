"""DLT source for the Federal Register of Legislation.

Crawls ``https://www.legislation.gov.au`` and emits one row per ``(federal_register_legislation_id, language)`` for
every document available in at least one of the official languages of
Australia.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/aus/law/federal_register_legislation.py`` with
``source_id="commonwealth.aus.law.federal_register_legislation"`` and lands in the
DuckLake table ``oideachais.law.commonwealth.aus``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/aus/law/<lang>/``.

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


class AustraliaLawSource(NationSource):
    """Federal Register of Legislation DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="aus",
            domain="law",
            source_slug="federal_register_legislation",
            supported_languages=('en',),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://www.legislation.gov.au",
                "title": "Federal Register of Legislation",
            },
        )


_NATION_SOURCE = AustraliaLawSource()


@dlt.resource(
    name="federal_register_legislation",
    write_disposition="merge",
    primary_key=["federal_register_legislation_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "federal_register_legislation_id": {"data_type": "text"},
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
def federal_register_legislation(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Australia law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "federal_register_legislation_live_mode_not_implemented",
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
                document_id_key="federal_register_legislation_id",
                default_status="published",
            )
            if row:
                row["federal_register_legislation_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="federal_register_legislation")
def federal_register_legislation_source(language: str | None = None):
    """DLT source for the Federal Register of Legislation ingestion."""
    return federal_register_legislation(language=language)


__all__ = [
    "AustraliaLawSource",
    "federal_register_legislation",
    "federal_register_legislation_source",
]
