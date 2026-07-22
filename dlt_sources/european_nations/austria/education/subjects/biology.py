"""Per-subject DLT source for Austria (biology).

Per-subject DLT source for the EU nations full-depth expansion change
(`2026-07-13-eu-nations-full-depth-expansion-v1`).

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/aut/education/subjects/biology/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt_sources
import structlog

from dlt_sources.european_nations._shared import (
    EU_NATIONS_CACHE_ROOT,
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class AUTBiologyEducationSource(NationSource):
    """Austria biology curriculum DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="aut",
            domain="education",
            source_slug="biology",
            supported_languages=('de',),
            document_type="biology_document",
            extra_metadata={
                "canonical_root": "https://www.bmbwf.gv.at",
                "title": "Austria biology curriculum (de)",
            },
        )

    def cache_path(self, language: str | None = None) -> Path:
        """Per-subject cache directory: <root>/<country>/education/subjects/<subject>/<lang>/."""
        lang = language or self.default_language
        return (
            EU_NATIONS_CACHE_ROOT
            / self.country_code
            / "education"
            / "subjects"
            / "biology"
            / lang
        )


_NATION_SOURCE = AUTBiologyEducationSource()


@dlt.resource(
    name="aut_biology",
    write_disposition="merge",
    primary_key=["biology_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "biology_id": {"data_type": "text"},
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
def aut_biology(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Austria biology rows from the canonical per-subject cache."""
    if not use_local_scrapes():
        logger.warning(
            "aut_biology_live_mode_not_implemented",
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
                document_id_key="biology_id",
                default_status="published",
            )
            if row:
                row["biology_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["subject"] = "biology"
                yield row


@dlt.source(name="aut_biology")
def aut_biology_source(language: str | None = None):
    """DLT source for the Austria biology ingestion."""
    return aut_biology(language=language)


__all__ = [
    "AUTBiologyEducationSource",
    "aut_biology",
    "aut_biology_source",
]
