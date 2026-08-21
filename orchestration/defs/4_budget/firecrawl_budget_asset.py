"""Firecrawl budget asset — nightly cost tracker.

Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1` change
(Phase 4a). Reads `cianfhoghlaim.firecrawl_meta.scrapes` (the
append-only scrape log populated by FirecrawlMCPClient) + writes
`cianfhoghlaim.firecrawl_meta.budget` (the rolling budget tracker).

The budget flags any pipeline that exceeds 150% of its monthly
allocation (defined in `deployment-choice.yaml` per the
centralized-registry contract). The `mise run lint:firecrawl-budget`
task reads the same table to surface the violations in the dev
terminal.
"""
# Deliberately NOT `from __future__ import annotations`. Dagster 1.13 detects
# the `context` parameter from its REAL annotation object; with postponed
# annotations it sees the string "AssetExecutionContext" and raises
# "Cannot annotate `context` parameter with type AssetExecutionContext",
# which aborts `dg.load_defs()` for the ENTIRE code location (not just this
# asset) and silently drops everything to the `_defs_walker` fallback.
# Same constraint as the layer*.py Components.
import json
import os
from datetime import UTC, datetime, timedelta
from typing import Any

from dagster import AssetExecutionContext, asset


# The canonical per-pipeline monthly allocations (credits).
# In production, these read from deployment-choice.yaml per the
# centralized-registry contract. The hardcoded defaults below are
# the per-pipeline estimates from the plan's detailed cost model.
DEFAULT_PIPELINE_ALLOCATIONS: dict[str, int] = {
    # Education sub-total (~960 credits/mo)
    "dlt:ncca_mathematics": 35,
    "dlt:ncca_chemistry": 35,
    "dlt:ncca_physics": 35,
    "dlt:ncca_biology": 35,
    "dlt:ncca_english": 35,
    "dlt:ncca_gaeilge": 35,
    "dlt:sqa_education": 240,
    "dlt:educationscotland": 30,
    "dlt:gov_scot_education": 8,
    "dlt:gov_uk_dfe": 12,
    "dlt:ofsted": 40,
    "dlt:pearson_edexcel": 60,
    "dlt:cambridge_international": 100,
    "dlt:wjec_wales": 50,
    "dlt:qualifications_wales": 30,
    "dlt:gov_wales_education": 5,
    "dlt:iom_education": 15,
    "dlt:gov_ie_education": 25,
    "dlt:oide_ie": 50,
    "dlt:scoilnet_ie": 60,
    "dlt:pdst_ie": 25,
    "dlt:examinations_ie_papers": 80,
    "dlt:examinations_ie_marking": 80,
    # Software corpus + agentic sub-total (~1,017 credits/mo)
    "corpus:build:cocoindex": 10,
    "corpus:build:dagster": 17,
    "corpus:build:dlt": 8,
    "corpus:build:baml": 4,
    "corpus:build:motherduck": 5,
    "corpus:build:duckdb": 15,
    "corpus:build:lancedb": 4,
    "corpus:build:pydantic_ai": 6,
    "corpus:build:fastapi": 7,
    "corpus:build:hono": 3,
    "corpus:build:tanstack_start": 4,
    "corpus:build:copilotkit": 9,
    "corpus:build:opencode": 2,
    "corpus:build:infisical": 11,
    "corpus:build:litellm": 7,
    "corpus:build:langfuse": 5,
    "corpus:build:firecrawl": 13,
    "agent:research": 500,
    "agent:research_papers": 100,
    "agent:developer_search": 50,
    "agent:frequent_search": 40,
    "agent:map_requests": 20,
    "agent:batch_scrape_lc": 60,
}


def _get_con() -> Any:
    """Open the MotherDuck / DuckLake connection."""
    import duckdb

    return duckdb.connect("md:cianfhoghlaim")


@asset(
    group_name="firecrawl_budget",
    description="Nightly Firecrawl budget tracker — reads scrapes + writes firecrawl_meta.budget",
)
def firecrawl_budget_asset(context: AssetExecutionContext) -> dict[str, Any]:
    """The nightly budget tracker.

    1. Read `cianfhoghlaim.firecrawl_meta.scrapes` for the past 24h
    2. Group by `pipeline` and `tool`
    3. Compute the trailing 30-day total per pipeline
    4. Compare to the per-pipeline monthly allocation
    5. Flag any pipeline > 150% of allocation
    6. Write the row to `cianfhoghlaim.firecrawl_meta.budget`
    """
    con = _get_con()
    now = datetime.now(UTC)
    yesterday = now - timedelta(days=1)
    thirty_days_ago = now - timedelta(days=30)

    # Read the past 24h of scrapes
    try:
        rows = con.execute(
            """
            SELECT pipeline, tool, credits_used, status
            FROM cianfhoghlaim.firecrawl_meta.scrapes
            WHERE started_at >= ?
            """,
            [yesterday],
        ).fetchall()
    except Exception as exc:
        context.log.warning(f"firecrawl_meta.scrapes table not yet populated: {exc}")
        rows = []

    # Aggregate by pipeline
    credit_by_pipeline: dict[str, int] = {}
    scrapes_by_pipeline: dict[str, int] = {}
    for pipeline, _tool, credits, _status in rows:
        credit_by_pipeline[pipeline] = credit_by_pipeline.get(pipeline, 0) + int(credits)
        scrapes_by_pipeline[pipeline] = scrapes_by_pipeline.get(pipeline, 0) + 1

    # Read the 30-day rolling totals
    try:
        rows_30d = con.execute(
            """
            SELECT pipeline, SUM(credits_used) as total_credits, COUNT(*) as scrapes
            FROM cianfhoghlaim.firecrawl_meta.scrapes
            WHERE started_at >= ?
            GROUP BY pipeline
            """,
            [thirty_days_ago],
        ).fetchall()
    except Exception:
        rows_30d = []

    rolling_30d: dict[str, dict[str, int]] = {}
    for pipeline, total_credits, scrapes in rows_30d:
        rolling_30d[pipeline] = {
            "credits_used": int(total_credits),
            "scrapes_count": int(scrapes),
        }

    # Compare to allocations + flag over-budget
    over_budget = False
    pipeline_allocations: dict[str, dict[str, Any]] = {}
    for pipeline, allocation in DEFAULT_PIPELINE_ALLOCATIONS.items():
        used = rolling_30d.get(pipeline, {}).get("credits_used", 0)
        ratio = (used / allocation) if allocation > 0 else 0
        pipeline_allocations[pipeline] = {
            "allocation": allocation,
            "used": used,
            "ratio": round(ratio, 3),
            "over_budget": ratio > 1.5,
        }
        if ratio > 1.5:
            over_budget = True
            context.log.warning(
                f"firecrawl_budget.over_budget: {pipeline} used {used}/{allocation} credits ({ratio:.1%})"
            )

    # Get the top 20 URLs by credits
    try:
        top_urls_rows = con.execute(
            """
            SELECT url, SUM(credits_used) as total_credits
            FROM cianfhoghlaim.firecrawl_meta.scrapes
            WHERE started_at >= ?
            GROUP BY url
            ORDER BY total_credits DESC
            LIMIT 20
            """,
            [thirty_days_ago],
        ).fetchall()
        top_urls = [{"url": r[0], "credits_used": int(r[1])} for r in top_urls_rows]
    except Exception:
        top_urls = []

    total_credits = sum(credit_by_pipeline.values())
    total_scrapes = sum(scrapes_by_pipeline.values())

    # Write the budget row
    try:
        con.execute(
            """
            INSERT OR REPLACE INTO cianfhoghlaim.firecrawl_meta.budget
            (day, credits_used, credits_estimated, scrapes_count, pipelines, top_urls, over_budget)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                now.date(),
                total_credits,
                total_credits,  # credits_estimated = credits_used on the daily summary
                total_scrapes,
                json.dumps(pipeline_allocations),
                json.dumps(top_urls),
                over_budget,
            ],
        )
    except Exception as exc:
        context.log.warning(f"Could not write firecrawl_meta.budget: {exc}")

    context.log.info(
        f"firecrawl_budget: {total_scrapes} scrapes, {total_credits} credits in past 24h; "
        f"over_budget={over_budget}"
    )

    return {
        "day": now.date().isoformat(),
        "credits_used": total_credits,
        "scrapes_count": total_scrapes,
        "over_budget": over_budget,
        "pipeline_allocations": pipeline_allocations,
        "top_urls": top_urls,
    }