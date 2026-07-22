"""Scotland (Scottish Parliament) official-media sub-asset.

Per the 2026-08-05-official-media-biiep-v3-coverage-v1 change
(closes GitHub issue #47 — add SCT jurisdiction to official-media).
"""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


# Scottish Parliament press releases + committee reports + member questions
SCOTLAND_SOURCES = [
    {
        "name": "Scottish Parliament Press Releases",
        "url": "https://www.parliament.scot/news-and-media/news",
        "type": "press_release",
        "cadence": "daily",
    },
    {
        "name": "Scottish Government News",
        "url": "https://www.gov.scot/news/",
        "type": "press_release",
        "cadence": "daily",
    },
    {
        "name": "Education Scotland Updates",
        "url": "https://education.gov.scot/news-and-events/",
        "type": "policy_update",
        "cadence": "weekly",
    },
]


async def fetch_scotland_sources() -> list[dict[str, Any]]:
    """Fetch the latest Scotland official-media sources.

    Per the BIEP v3 generic pipeline pattern, this is a stub that
    returns the configured sources. The real implementation would
    scrape each URL and classify via the existing classifier.
    """
    logger.info("fetching Scotland official-media sources (count=%d)", len(SCOTLAND_SOURCES))
    return [
        {**src, "fetched_at": datetime.now(UTC).isoformat(), "jurisdiction": "scotland"}
        for src in SCOTLAND_SOURCES
    ]


__all__ = ["SCOTLAND_SOURCES", "fetch_scotland_sources"]
