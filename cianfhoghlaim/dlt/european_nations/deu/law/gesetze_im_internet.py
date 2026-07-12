"""DLT source for the Bundesministerium der Justiz — Gesetze im Internet.

Crawls ``https://www.gesetze-im-internet.de`` and emits one row per ``(gesetze_im_internet_id, language)`` for
every document available in at least one of the official languages of
Germany.

Per the canonical
[`cross-region-pipeline`](../../../openspec/specs/cross-region-pipeline/spec.md)
contract this source lives at
``dlt/european_nations/deu/law/gesetze_im_internet.py`` with
``source_id="european_nations.deu.law.gesetze_im_internet"`` and lands in
the DuckLake table ``oideachais.law.european_nations.deu``.

Honours ``USE_LOCAL_SCRAPES=true`` by reading from
``stedding/ingest_queue/european_nations/deu/law/<lang>/``.

Reference: ``openspec/changes/2026-07-11-european-nations-ukraine-pipeline-v1/``.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog

from cianfhoghlaim.dlt.european_nations._shared import (
    NationSource,
    row_from_cache,
    use_local_scrapes,
)

logger = structlog.get_logger(__name__)


class GermanyLawSource(NationSource):
    """Bundesministerium der Justiz — Gesetze im Internet DLT source."""

    def __init__(self) -> None:
        super().__init__(
            country_code="deu",
            domain="law",
            source_slug="gesetze_im_internet",
            supported_languages=('de',),
            document_type="law_document",
            extra_metadata={
                "canonical_root": "https://www.gesetze-im-internet.de",
                "title": "Bundesministerium der Justiz — Gesetze im Internet",
            },
        )


_NATION_SOURCE = GermanyLawSource()


@dlt.resource(
    name="gesetze_im_internet",
    write_disposition="merge",
    primary_key=["gesetze_im_internet_id", "language"],
    columns={
        "country_code": {"data_type": "text"},
        "language": {"data_type": "text"},
        "domain": {"data_type": "text"},
        "gesetze_im_internet_id": {"data_type": "text"},
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
def gesetze_im_internet(language: str | None = None) -> Iterator[dict[str, Any]]:
    """Yield Germany law rows from the canonical cache."""
    if not use_local_scrapes():
        logger.warning(
            "gesetze_im_internet_live_mode_not_implemented",
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
                document_id_key="gesetze_im_internet_id",
                default_status="published",
            )
            if row:
                row["gesetze_im_internet_id"] = row.pop("document_id", cache_path.stem)
                row["institution"] = _NATION_SOURCE.source_slug
                yield row


@dlt.source(name="gesetze_im_internet")
def gesetze_im_internet_source(language: str | None = None):
    """DLT source for the Bundesministerium der Justiz — Gesetze im Internet ingestion."""
    return gesetze_im_internet(language=language)


__all__ = [
    "GermanyLawSource",
    "gesetze_im_internet",
    "gesetze_im_internet_source",
]
