"""Dagster asset wiring for the 5 new BIEP v3 official-media sub-assets.

Per the 2026-08-05-official-media-biiep-v3-coverage-v1 change
(closes GitHub issue #47 — add SCT + WLS + IoM + JEY + GGY jurisdictions).
"""
from __future__ import annotations

import logging
from typing import Any

from dagster import asset, AssetExecutionContext

logger = logging.getLogger(__name__)


@asset(
    group_name="official_media_jurisdictions",
    description="Scotland (Scottish Parliament) official-media cohorts",
)
def scotland_official_media_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.official_media.sct.sources import fetch_scotland_sources
    import asyncio
    rows = asyncio.run(fetch_scotland_sources())
    context.add_output_metadata({"row_count": len(rows), "jurisdiction": "scotland"})
    return {"rows": rows, "jurisdiction": "scotland"}


@asset(
    group_name="official_media_jurisdictions",
    description="Wales (Senedd Cymru) official-media cohorts",
)
def wales_official_media_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.official_media.wls.sources import fetch_wales_sources
    import asyncio
    rows = asyncio.run(fetch_wales_sources())
    context.add_output_metadata({"row_count": len(rows), "jurisdiction": "wales"})
    return {"rows": rows, "jurisdiction": "wales"}


@asset(
    group_name="official_media_jurisdictions",
    description="Isle of Man (Tynwald) official-media cohorts",
)
def isle_of_man_official_media_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.official_media.iom.sources import fetch_iom_sources
    import asyncio
    rows = asyncio.run(fetch_iom_sources())
    context.add_output_metadata({"row_count": len(rows), "jurisdiction": "isle_of_man"})
    return {"rows": rows, "jurisdiction": "isle_of_man"}


@asset(
    group_name="official_media_jurisdictions",
    description="Jersey (States of Jersey) official-media cohorts",
)
def jersey_official_media_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.official_media.jsy.sources import fetch_jersey_sources
    import asyncio
    rows = asyncio.run(fetch_jersey_sources())
    context.add_output_metadata({"row_count": len(rows), "jurisdiction": "jersey"})
    return {"rows": rows, "jurisdiction": "jersey"}


@asset(
    group_name="official_media_jurisdictions",
    description="Guernsey (States of Guernsey) official-media cohorts",
)
def guernsey_official_media_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.official_media.ggy.sources import fetch_guernsey_sources
    import asyncio
    rows = asyncio.run(fetch_guernsey_sources())
    context.add_output_metadata({"row_count": len(rows), "jurisdiction": "guernsey"})
    return {"rows": rows, "jurisdiction": "guernsey"}


@asset(
    group_name="official_media_hmgcc",
    description="HMGCC 12-week rolling window",
)
def hmgcc_rolling_window_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.official_media.hmgcc.rolling_window import fetch_hmgcc_rolling_window
    import asyncio
    rows = asyncio.run(fetch_hmgcc_rolling_window(lookback_weeks=12))
    context.add_output_metadata({"row_count": len(rows), "lookback_weeks": 12})
    return {"rows": rows, "lookback_weeks": 12}


@asset(
    group_name="official_media_companies_house",
    description="Companies House Crown body filter (re-identification)",
)
def companies_house_crown_filter_ingested(context: AssetExecutionContext) -> dict[str, Any]:
    from dlt_sources.official_media.companies_house.crown_filter import (
        CANONICAL_CROWN_BODIES, filter_crown_bodies,
    )
    # Stub: a real impl would fetch from Companies House API
    companies = [cb for cb in CANONICAL_CROWN_BODIES if cb["companies_house_number"]]
    filtered = filter_crown_bodies(companies)
    context.add_output_metadata({"row_count": len(filtered)})
    return {"rows": filtered}


__all__ = [
    "scotland_official_media_ingested",
    "wales_official_media_ingested",
    "isle_of_man_official_media_ingested",
    "jersey_official_media_ingested",
    "guernsey_official_media_ingested",
    "hmgcc_rolling_window_ingested",
    "companies_house_crown_filter_ingested",
]
