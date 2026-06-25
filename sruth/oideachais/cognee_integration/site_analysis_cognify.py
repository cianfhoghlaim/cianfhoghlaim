"""
oideachais.cognee_integration.site_analysis_cognify — Cognee cognify
helper for SiteAnalysis records.

Phase 8 of the openspec change. The dataset name is
`oideachais_site_analysis`; edge types are `uses_cms`, `hosts_pdf`,
`requires_captcha`, `has_robots_txt`.
"""
from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

DATASET_NAME = "oideachais_site_analysis"
EDGE_TYPES = ["uses_cms", "hosts_pdf", "requires_captcha", "has_robots_txt"]


async def cognify_site_analysis_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Cognify a batch of `SiteAnalysis` rows into the Cognee graph.

    The function is a no-op in test mode (`USE_LOCAL_SCRAPES=true`)
    and a `cognee.add` + `cognee.cognify` call in production.
    """
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info("site_analysis_cognify_skipped_stub_mode", rows=len(rows))
        return {"dataset": DATASET_NAME, "rows": len(rows), "edges": 0, "stub": True}

    try:
        import cognee  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("cognee_not_available_skipping_cognify")
        return {"dataset": DATASET_NAME, "rows": len(rows), "edges": 0, "stub": True}

    for row in rows:
        await cognee.add(row, dataset_name=DATASET_NAME)
    await cognee.cognify()
    return {"dataset": DATASET_NAME, "rows": len(rows), "edges": len(rows) * len(EDGE_TYPES)}


__all__ = ["cognify_site_analysis_rows", "DATASET_NAME", "EDGE_TYPES"]
