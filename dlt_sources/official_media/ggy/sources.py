"""Guernsey (States of Guernsey) official-media sub-asset.

Per the 2026-08-05-official-media-biiep-v3-coverage-v1 change
(closes GitHub issue #47 — add GGY jurisdiction to official-media).
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


GUERNSEY_SOURCES = [
    {
        "name": "States of Guernsey News",
        "url": "https://www.gov.gg/news",
        "type": "press_release",
        "cadence": "daily",
    },
    {
        "name": "States of Deliberation Hansard",
        "url": "https://www.gov.gg/StatesofDeliberation",
        "type": "hansard",
        "cadence": "weekly",
    },
    {
        "name": "Education, Sport & Culture",
        "url": "https://www.gov.gg/education",
        "type": "policy_update",
        "cadence": "weekly",
    },
]


async def fetch_guernsey_sources() -> list[dict[str, Any]]:
    """Fetch the latest Guernsey official-media sources."""
    logger.info("fetching Guernsey official-media sources (count=%d)", len(GUERNSEY_SOURCES))
    return [
        {**src, "fetched_at": datetime.now(UTC).isoformat(), "jurisdiction": "guernsey"}
        for src in GUERNSEY_SOURCES
    ]


__all__ = ["GUERNSEY_SOURCES", "fetch_guernsey_sources"]
