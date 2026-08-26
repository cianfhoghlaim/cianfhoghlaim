"""DLT source for the Australian Curriculum, Assessment and Reporting Authority.

Crawls ``https://www.acara.edu.au`` and emits one row per ``(acara_id, language)`` for
every document available in at least one of the official languages of
Australia.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/commonwealth/aus/education/acara.py`` with
``source_id="commonwealth.aus.education.acara"`` and lands in the
DuckLake table ``oideachais.education.commonwealth.aus``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/commonwealth/aus/education/<lang>/``.

Reference: ``openspec/changes/2026-07-11-commonwealth-pipeline-v1/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
import structlog

from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import (
    JurisdictionPipelineBase,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class AustraliaEducationSource(JurisdictionPipelineBase):
    """Australian Curriculum, Assessment and Reporting Authority DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="aus",
            domain="education",
            source_slug="acara",
            supported_languages=('en',),
            document_type="education_document",
            extra_metadata={
                "canonical_root": "https://www.acara.edu.au",
                "title": "Australian Curriculum, Assessment and Reporting Authority",
            },
        )


_NATION_SOURCE = AustraliaEducationSource()


@dlt.resource(
    name="acara",
    write_disposition="merge",
    primary_key=["acara_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "acara_id": {"data_type": "text"},
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
def acara(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Australia education rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "acara_live_mode_not_implemented",
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
                document_id_key="acara_id",
                default_status="published",
            )
            if row:
                row["acara_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["region"] = "commonwealth"
                yield row


@dlt.source(name="acara")
def acara_source(language: str | None = None):
    """DLT source for the Australian Curriculum, Assessment and Reporting Authority ingestion."""
    return acara(language=language)


__all__ = [
    "AustraliaEducationSource",
    "acara",
    "acara_source",
]
