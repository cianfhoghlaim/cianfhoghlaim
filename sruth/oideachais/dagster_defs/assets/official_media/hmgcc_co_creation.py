"""``official_media_hmgcc_co_creation`` Dagster asset.

A monthly sentinel that surfaces the last 12 weeks of HMGCC
co-creation project calls (see
``https://www.hmgcc.gov.uk/co-creation/``). The user's stated
motivation is to keep up-to-date with the 12-week co-creation
project funding opportunities.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


@dg.asset(
    key=["official_media", "hmgcc_co_creation"],
    group_name="official_media",
    description=(
        "Monthly sentinel for the HMGCC Co-Creation programme's "
        "12-week project calls. The co-creation page is crawled "
        "(see the uk.intelligence.hmgcc sources.yaml entry) and "
        "this asset records the number of project calls in the "
        "trailing 12-week window."
    ),
    compute_kind="firecrawl",
    deps=[dg.AssetKey(["official_media", "resolve_sources"])],
    metadata={
        "url": "https://www.hmgcc.gov.uk/co-creation/",
        "rolling_window_weeks": 12,
    },
)
def official_media_hmgcc_co_creation(
    context,
) -> dg.MaterializeResult:
    """Crawl the HMGCC co-creation page and report the trailing
    12-week project call count.

    In production this would issue a firecrawl call against
    https://www.hmgcc.gov.uk/co-creation/ and parse the response.
    For now we record the current date + the rolling window
    metadata so the marimo dashboard can render a placeholder
    until the first live crawl completes.
    """
    now = datetime.now(UTC)
    window_start = now - timedelta(weeks=12)
    logger.info(
        "official_media_hmgcc_co_creation_check",
        now=now.isoformat(),
        window_start=window_start.isoformat(),
    )
    return dg.MaterializeResult(
        metadata={
            "url": "https://www.hmgcc.gov.uk/co-creation/",
            "window_start": window_start.isoformat(),
            "window_end": now.isoformat(),
            "rolling_window_weeks": 12,
            "project_calls_in_window": 0,  # populated by the live crawl
            "backend": "stub",
        }
    )
