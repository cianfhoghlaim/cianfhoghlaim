"""
oideachais.dlt_sources.site_analysis.site_analysis — DLT source over the
`site_analysis` package output.

Phase 8 of the openspec change. Iterates every public source in
`oideachais/sources.yaml`, calls `oideachais.site_analysis.extractor.extract_source`,
and yields one row per `SiteAnalysis` to DLT.

The destination is DuckLake (writes to
`oideachais.site_analysis.site_analyses` in the unified lakehouse).
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import dlt
import structlog
from dlt_utils.source_factory import get_default_factory
from site_analysis.extractor import extract_source

logger = structlog.get_logger(__name__)


def _iter_sources() -> Iterator[dict[str, Any]]:
    """Iterate every source in `sources.yaml` and yield a `SiteAnalysis`
    row for it. In test mode (`USE_LOCAL_SCRAPES=true`) the extractor
    uses the stub fixture so no live network is touched."""
    factory = get_default_factory()
    for entry in factory.spec.sources:
        try:
            analysis = extract_source(
                source_id=entry.id,
                base_url=entry.urls[0] if entry.urls else "https://example.com",
            )
        except Exception as exc:
            logger.warning("site_analysis_extraction_failed", source_id=entry.id, error=str(exc))
            continue
        row = analysis.to_dlt_row()
        row["__source_id"] = entry.id
        yield row


@dlt.source(name="site_analysis")
def site_analysis_source():
    """DLT source over the entire `sources.yaml` registry."""

    @dlt.resource(
        name="site_analyses",
        write_disposition="merge",
        primary_key=["source_id", "captured_at"],
    )
    def site_analyses():
        yield from _iter_sources()

    return site_analyses
