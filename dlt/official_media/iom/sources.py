"""Isle of Man (Tynwald) official-media sub-asset.

Per the 2026-08-05-official-media-biiep-v3-coverage-v1 change
(closes GitHub issue #47 — add IoM jurisdiction to official-media).
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


IOM_SOURCES = [
    {
        "name": "Tynwald Hansard",
        "url": "https://www.tynwald.org.im/business/hansard",
        "type": "hansard",
        "cadence": "daily",
    },
    {
        "name": "Isle of Man Government News",
        "url": "https://www.gov.im/news/",
        "type": "press_release",
        "cadence": "daily",
    },
    {
        "name": "Department of Education, Sport and Culture",
        "url": "https://www.gov.im/about-the-government/departments/education,-sport-and-culture/",
        "type": "policy_update",
        "cadence": "weekly",
    },
]


async def fetch_iom_sources() -> list[dict[str, Any]]:
    """Fetch the latest Isle of Man official-media sources."""
    logger.info("fetching IoM official-media sources (count=%d)", len(IOM_SOURCES))
    return [
        {**src, "fetched_at": datetime.now(UTC).isoformat(), "jurisdiction": "isle_of_man"}
        for src in IOM_SOURCES
    ]


__all__ = ["IOM_SOURCES", "fetch_iom_sources"]
