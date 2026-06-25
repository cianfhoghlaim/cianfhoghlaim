"""
oideachais.cognee_integration.official_media_cognify — Cognee cognify
helper for the official-media pipeline.

Phase 6 of the official-media-pipeline openspec change. The dataset
name is ``oideachais_official_media``; edge types are the 4 defined
in the spec:

  * ig_profile → official_website
  * ig_profile → fediverse_account
  * ig_profile → companies_house_entity
  * official_website → wikipedia_article (bi-directional)

The function is a no-op in stub mode (``USE_LOCAL_SCRAPES=true``,
the CI default) and a real ``cognee.add`` + ``cognee.cognify()``
call in production.
"""
from __future__ import annotations

import os
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

DATASET_NAME = "oideachais_official_media"
EDGE_TYPES = [
    "ig_profile->official_website",
    "ig_profile->fediverse_account",
    "ig_profile->companies_house_entity",
    "official_website->wikipedia_article",
]


async def cognify_official_media_rows(
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Cognify a batch of resolved official-media rows into the Cognee graph."""
    if os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true":
        logger.info(
            "official_media_cognify_skipped_stub_mode",
            rows=len(rows),
        )
        return {
            "dataset": DATASET_NAME,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    try:
        import cognee  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("cognee_not_available_skipping_cognify")
        return {
            "dataset": DATASET_NAME,
            "rows": len(rows),
            "edges": 0,
            "stub": True,
        }

    for row in rows:
        await cognee.add(row, dataset_name=DATASET_NAME)
    await cognee.cognify()
    return {
        "dataset": DATASET_NAME,
        "rows": len(rows),
        "edges": len(rows) * len(EDGE_TYPES),
    }


__all__ = ["cognify_official_media_rows", "DATASET_NAME", "EDGE_TYPES"]
