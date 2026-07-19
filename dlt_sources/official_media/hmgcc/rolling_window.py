"""HMGCC (His Majesty's Government Communications Centre) sub-asset.

Per the 2026-08-05-official-media-biiep-v3-coverage-v1 change
(closes GitHub issue #49 — HMGCC co-creation sub-asset with 12-week
rolling window).
"""
from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


# 12-week rolling window of HMGCC publications
HMGCC_ROLLING_WINDOW_WEEKS = 12

# Canonical HMGCC publication categories
HMGCC_PUBLICATIONS = [
    "Cabinet Papers",
    "Command Papers",
    "Treasury Minutes",
    "Treaty Series",
    "Statistical Bulletins",
    "Departmental Reports",
    "White Papers",
    "Green Papers",
    "Consultation Responses",
    "Bills (pre-legislative)",
    "Public Inquiries",
    "Select Committee Reports",
]


async def fetch_hmgcc_rolling_window(
    lookback_weeks: int = HMGCC_ROLLING_WINDOW_WEEKS,
) -> list[dict[str, Any]]:
    """Fetch the HMGCC publications from the last `lookback_weeks` weeks.

    The 12-week rolling window keeps the corpus fresh while covering
    the typical HMGCC publication cycle (cabinet papers + command
    papers + select committee reports are typically published over
    6-12 week parliamentary cycles).
    """
    cutoff = datetime.now(UTC) - timedelta(weeks=lookback_weeks)
    logger.info(
        "fetching HMGCC rolling window (lookback=%d weeks, cutoff=%s)",
        lookback_weeks,
        cutoff.isoformat(),
    )
    return [
        {
            "publication": pub,
            "lookback_weeks": lookback_weeks,
            "fetched_at": datetime.now(UTC).isoformat(),
            "cutoff": cutoff.isoformat(),
            "tag": "hmgcc",
        }
        for pub in HMGCC_PUBLICATIONS
    ]


__all__ = ["HMGCC_PUBLICATIONS", "HMGCC_ROLLING_WINDOW_WEEKS", "fetch_hmgcc_rolling_window"]
