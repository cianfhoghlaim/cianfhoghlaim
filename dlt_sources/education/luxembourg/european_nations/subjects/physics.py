"""Per-subject DLT source for Luxembourg (physics).

Per-subject DLT source for the EU nations full-depth expansion change
(`2026-07-13-eu-nations-full-depth-expansion-v1`).

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/lux/education/subjects/physics/<lang>/``.

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


class LuxembourgPhysicsEducationSource(NationSource):
    """Luxembourg physics curriculum DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="lux",
            domain="education",
            source_slug="physics",
            supported_languages=("lb", "fr", "de"),
            document_type="physics_document",
            extra_metadata={
                "canonical_root": "https://men.public.lu",
                "title": "Luxembourg physics curriculum (lb,fr,de)",
            },
        )

    def cache_path(self, language: str | None = None) -> Path:
        """Per-subject cache directory: <root>/<country>/education/subjects/<subject>/<lang>/."""
        lang = language or self.default_language
        return (
            EU_NATIONS_CACHE_ROOT / self.country_code / "education" / "subjects" / "physics" / lang
        )


_NATION_SOURCE = LuxembourgPhysicsEducationSource()


@dlt.resource(
    name="lux_physics",
    write_disposition="merge",
    primary_key=["physics_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "subject": {"data_type": "text"},
        "physics_id": {"data_type": "text"},
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
def lux_physics(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Luxembourg physics rows from the canonical per-subject cache."""
    if not use_local_scrapes():
        logger.warning(
            "lux_physics_live_mode_not_implemented",
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
                document_id_key="physics_id",
                default_status="published",
            )
            if row:
                row["physics_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                row["subject"] = "physics"
                yield row


@dlt.source(name="lux_physics")
def lux_physics_source(language: str | None = None):
    """DLT source for the Luxembourg physics ingestion."""
    return lux_physics(language=language)


__all__ = [
    "LuxembourgPhysicsEducationSource",
    "lux_physics",
    "lux_physics_source",
]
