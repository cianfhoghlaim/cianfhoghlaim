"""Dagster L2 — Heritage BAML extraction assets.

Added 2026-07-17. Calls `b.ExtractHeritageSite` (added in this change)
over the heritage DuckLake rows. Routes via `gemma-4-26B-A4B`.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    from cianfhoghlaim.meaisinfhoghlaim.models.routing import (  # type: ignore[import-not-found]
        get_baml_client,
    )
    _ROUTING_AVAILABLE = True
except Exception:
    _ROUTING_AVAILABLE = False
    get_baml_client = None  # type: ignore[assignment]


try:
    from baml_client import b  # type: ignore[import-not-found]
    _BAML_AVAILABLE = True
except Exception:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]


def extract_heritage_sites(
    site_rows: list[dict[str, Any]],
    language: str = "ga",
) -> list[dict[str, Any]]:
    """Extract BAML-typed records for heritage sites.

    Uses `b.ExtractHeritageSite` (added in `baml/celtic/gaois/duchas.baml`).
    """
    if not _BAML_AVAILABLE or b is None:
        logger.warning("baml_unavailable: extract_heritage_sites")
        return []

    client_name = get_baml_client("heritage", language) if _ROUTING_AVAILABLE else "LlamaSwapReasoningClient"
    logger.info("extract_heritage_sites routing=%s n=%d", client_name, len(site_rows))

    results = []
    for row in site_rows:
        try:
            extracted = b.ExtractHeritageSite(
                site_text=row.get("description", ""),
                site_name=row.get("site_name", ""),
                site_name_ga=row.get("site_name_ga", ""),
                site_type=row.get("site_type", ""),
                county=row.get("county", ""),
            )
            results.append({**row, "extracted": extracted, "routing_client": client_name})
        except Exception as exc:
            logger.warning("heritage_extract_failed: %s", exc)
            continue
    return results


__all__ = ["extract_heritage_sites"]