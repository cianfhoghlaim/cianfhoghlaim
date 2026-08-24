"""Per-subject DLT source for Liechtenstein (chemistry).

Per-subject DLT source for the EU nations full-depth expansion change
(`2026-07-13-eu-nations-full-depth-expansion-v1`).

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/lie/education/subjects/chemistry/<lang>/``.

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


class LiechtensteinChemistryEducationSource(NationSource):
    """Liechtenstein chemistry curriculum DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="lie",
            domain="education",
            source_slug="chemistry",
            supported_languages=('de',),
            document_type="chemistry_document",
            extra_metadata={
                "canonical_root": "https://www.llv.li",
                "title": "Liechtenstein chemistry curriculum (de)",
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
            / "chemistry"
            / lang
        )


_NATION_SOURCE = LiechtensteinChemistryEducationSource()


@dlt.resource(
    name="lie_chemistry",
    write_disposition="merge",
    primary_key=["chemistry_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "chemistry_id": {"data_type": "text"},
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
def lie_chemistry(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Liechtenstein chemistry rows from the canonical per-subject cache."""
    if not use_local_scrapes():
        logger.warning(
            "lie_chemistry_live_mode_not_implemented",
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
                document_id_key="chemistry_id",
                default_status="published",
            )
            if row:
                row["chemistry_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["subject"] = "chemistry"
                yield row


@dlt.source(name="lie_chemistry")
def lie_chemistry_source(language: str | None = None):
    """DLT source for the Liechtenstein chemistry ingestion."""
    return lie_chemistry(language=language)


__all__ = [
    "LiechtensteinChemistryEducationSource",
    "lie_chemistry",
    "lie_chemistry_source",
]
