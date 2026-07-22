"""Per-subject DLT source for Austria (mathematics).

Per-subject DLT source for the EU nations full-depth expansion change
(`2026-07-13-eu-nations-full-depth-expansion-v1`).

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/aut/education/subjects/mathematics/<lang>/``.

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


class AUTMathematicsEducationSource(NationSource):
    """Austria mathematics curriculum DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="aut",
            domain="education",
            source_slug="mathematics",
            supported_languages=('de',),
            document_type="mathematics_document",
            extra_metadata={
                "canonical_root": "https://www.bmbwf.gv.at",
                "title": "Austria mathematics curriculum (de)",
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
            / "mathematics"
            / lang
        )


_NATION_SOURCE = AUTMathematicsEducationSource()


@dlt.resource(
    name="aut_mathematics",
    write_disposition="merge",
    primary_key=["mathematics_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "mathematics_id": {"data_type": "text"},
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
def aut_mathematics(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Austria mathematics rows from the canonical per-subject cache."""
    if not use_local_scrapes():
        logger.warning(
            "aut_mathematics_live_mode_not_implemented",
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
                document_id_key="mathematics_id",
                default_status="published",
            )
            if row:
                row["mathematics_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["subject"] = "mathematics"
                yield row


@dlt.source(name="aut_mathematics")
def aut_mathematics_source(language: str | None = None):
    """DLT source for the Austria mathematics ingestion."""
    return aut_mathematics(language=language)


__all__ = [
    "AUTMathematicsEducationSource",
    "aut_mathematics",
    "aut_mathematics_source",
]
