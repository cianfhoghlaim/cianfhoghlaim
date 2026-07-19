"""DLT source for the National Printing House of Greece (et.gr) (law, Greece).

Crawls ``https://www.et.gr`` and emits one row per ``(legislation_grc_id, language)`` for
every document available in at least one of the official languages of
Greece.

Per the canonical
[`cross-region-pipeline`](../../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/grc/law/legislation_grc.py`` with
``source_id="european_nations.grc.law.legislation_grc"`` and lands in
the DuckLake table ``oideachais.law.european_nations.grc``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/grc/law/<lang>/``.

Reference: ``openspec/changes/2026-07-13-eu-nations-full-depth-expansion-v1/``.
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


class GreeceLawSource(NationSource):
    """National Printing House of Greece (et.gr) DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="grc",
            domain="law",
            source_slug="legislation_grc",
            supported_languages=("el",),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://www.et.gr",
                "title": "National Printing House of Greece (et.gr)",
            },
        )


_NATION_SOURCE = GreeceLawSource()


@dlt.resource(
    name="legislation_grc",
    write_disposition="merge",
    primary_key=["legislation_grc_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "legislation_grc_id": {"data_type": "text"},
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
def legislation_grc(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Greece law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "legislation_grc_live_mode_not_implemented",
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
                document_id_key="legislation_grc_id",
                default_status="in_force",
            )
            if row:
                row["legislation_grc_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="legislation_grc")
def legislation_grc_source(language: str | None = None):
    """DLT source for the National Printing House of Greece (et.gr) ingestion."""
    return legislation_grc(language=language)


__all__ = [
    "GreeceLawSource",
    "legislation_grc",
    "legislation_grc_source",
]
