"""DLT source for the Ministère de l'Éducation nationale.

Crawls ``https://www.education.gouv.fr`` and emits one row per ``(ministere_education_nationale_id, language)`` for
every document available in at least one of the official languages of
France.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/fra/education/ministere_education_nationale.py`` with
``source_id="european_nations.fra.education.ministere_education_nationale"`` and lands in
the DuckLake table ``oideachais.education.european_nations.fra``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/fra/education/<lang>/``.

Reference: ``openspec/changes/2026-07-11-european-nations-ukraine-pipeline-v1/``.
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


class FranceEducationSource(NationSource):
    """Ministère de l'Éducation nationale DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="fra",
            domain="education",
            source_slug="ministere_education_nationale",
            supported_languages=('fr',),
            document_type="education_document",
            extra_metadata={
                "canonical_root": "https://www.education.gouv.fr",
                "title": "Ministère de l'Éducation nationale",
            },
        )


_NATION_SOURCE = FranceEducationSource()


@dlt.resource(
    name="ministere_education_nationale",
    write_disposition="merge",
    primary_key=["ministere_education_nationale_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "ministere_education_nationale_id": {"data_type": "text"},
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
def ministere_education_nationale(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield France education rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "ministere_education_nationale_live_mode_not_implemented",
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
                document_id_key="ministere_education_nationale_id",
                default_status="published",
            )
            if row:
                row["ministere_education_nationale_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="ministere_education_nationale")
def ministere_education_nationale_source(language: str | None = None):
    """DLT source for the Ministère de l'Éducation nationale ingestion."""
    return ministere_education_nationale(language=language)


__all__ = [
    "FranceEducationSource",
    "ministere_education_nationale",
    "ministere_education_nationale_source",
]
