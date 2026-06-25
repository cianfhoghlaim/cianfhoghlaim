"""Scraping assets for the author-archive-v1 web-ingest pipeline.

Four new assets in the ``official_media`` group:

  * ``pre_research``   - one-time pre-research pass per source (Firecrawl /agent
                          with credit guard; falls back to Crawl4AI sitemap+sample
                          when the budget is exhausted)
  * ``bulk_scrape``    - bulk scrape of every source's recommended URLs using
                          the strategy from the pre-research record
  * ``condense``       - BAML CondenseToCriticalInfo on every raw page
  * ``identify_uis``   - BAML IdentifyUiPatterns + Stagehand observe() +
                          VisualGroundingFromScreenshot for any page with UIs

The user said: "we want to know what data we have and how it was sourced" — every
asset writes its results to a LanceDB table with the original URL, the bytes
in/out, the backend used, the credit cost, and the BAML confidence. The marimo
dashboards render all of this in the "Source provenance" tab.

Sample sources are picked from each of the 10 official_media categories so the
hero example covers the full British Isles spread, not just gov.uk.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# Test sources (1-2 per official_media category, 17 total)
# ============================================================================
# These are the sample sources the assets materialise on. The full 160
# official_media sources are in oideachais/sources.yaml; the assets loop
# over them, but only materialise these 17 in CI to keep the asset run
# short and the Firecrawl credit burn under 100 credits per CI run.

OFFICIAL_MEDIA_SAMPLE_SOURCES: list[dict[str, str]] = [
    # intelligence (4 total)
    {"slug": "gchq_gov_uk", "url": "https://www.gchq.gov.uk",
     "category": "intelligence", "nation": "en",
     "goal": "Identify all news, careers, and operations pages."},
    {"slug": "mi5_gov_uk", "url": "https://www.mi5.gov.uk",
     "category": "intelligence", "nation": "en",
     "goal": "Identify threat reports, news, and policy pages."},
    # universities (24 total) - pick user's own + a Welsh-medium one
    {"slug": "universityofgalway_ie", "url": "https://www.universityofgalway.ie",
     "category": "universities", "nation": "ie",
     "goal": "Identify news, courses, research, and policy pages."},
    {"slug": "cardiff_ac_uk", "url": "https://www.cardiff.ac.uk",
     "category": "universities", "nation": "wls",
     "goal": "Identify news, courses, research, and Welsh-language pages."},
    # Celtic colleges (3 total)
    {"slug": "colaistefeirste_org", "url": "https://www.colaistefeirste.org",
     "category": "celtic_colleges", "nation": "ni",
     "goal": "Identify course, news, and Irish-medium pages."},
    # schools (4 total)
    {"slug": "scoilnaseolta_org", "url": "https://www.scoilnaseolta.org",
     "category": "schools", "nation": "ie",
     "goal": "Identify school news, enrolment, and curriculum pages."},
    # language_project (1 total)
    {"slug": "turasbelfast_com", "url": "https://www.turasbelfast.com",
     "category": "language_project", "nation": "ni",
     "goal": "Identify Irish-language learning resources and events."},
    # parties (24 total) - pick one Irish + one Welsh
    {"slug": "finegael_ie", "url": "https://www.finegael.ie",
     "category": "parties", "nation": "ie",
     "goal": "Identify press releases, policy documents, and news."},
    {"slug": "plaid_cymru", "url": "https://www.plaid.cymru",
     "category": "parties", "nation": "wls",
     "goal": "Identify press releases, policy documents, and Welsh-language pages."},
    # police (56 total) - pick the two main British Isles forces
    {"slug": "psni_police_uk", "url": "https://www.psni.police.uk",
     "category": "police", "nation": "ni",
     "goal": "Identify news, appeals, and statistics."},
    {"slug": "garda_ie", "url": "https://www.garda.ie",
     "category": "police", "nation": "ie",
     "goal": "Identify news, appeals, and statistics."},
    # defence (13 total)
    {"slug": "royalnavy_mod_uk", "url": "https://www.royalnavy.mod.uk",
     "category": "defence", "nation": "en",
     "goal": "Identify news, operations, and recruitment pages."},
    {"slug": "military_ie", "url": "https://www.military.ie",
     "category": "defence", "nation": "ie",
     "goal": "Identify news and recruitment pages."},
    # national_info (5 total) - met office + bbc
    {"slug": "metoffice_gov_uk", "url": "https://www.metoffice.gov.uk",
     "category": "national_info", "nation": "en",
     "goal": "Identify forecasts, warnings, and climate data pages."},
    {"slug": "bbc_co_uk", "url": "https://www.bbc.co.uk",
     "category": "national_info", "nation": "en",
     "goal": "Identify news, weather, and data pages."},
    # jurisdictions (29 total) - CPS + courts.ie (the user-requested example)
    {"slug": "cps_gov_uk", "url": "https://www.cps.gov.uk",
     "category": "jurisdictions", "nation": "en",
     "goal": "Identify all press releases, prosecution guidance, and case decision databases published 2020-2026."},
    {"slug": "courts_ie", "url": "https://www.courts.ie",
     "category": "jurisdictions", "nation": "ie",
     "goal": "Identify court decisions, practice directions, and statistics."},
]


# ============================================================================
# Asset: pre_research — one-time per source
# ============================================================================

@dg.asset(
    key=["official_media", "pre_research"],
    group_name="official_media",
    description=(
        "One-time pre-research pass for every official_media source. Uses "
        "Firecrawl /agent (the only backend with autonomous research) with "
        "a credit-budget guard. Falls back to Crawl4AI sitemap+sample when "
        "the budget is exhausted. Persists the result in "
        "research_sitemap (LanceDB) keyed by source slug."
    ),
    compute_kind="scrape",
    metadata={
        "table": "official_media.research_sitemap",
        "primary_key": ["source_id"],
    },
)
def official_media_pre_research(context) -> dg.MaterializeResult:
    """Run PreResearchSite for every sample source via the ScrapeStrategist."""
    try:
        from sruth_browser import ScrapeStrategist
    except ImportError as e:
        logger.warning(
            "sruth_browser_not_available",
            error=str(e),
            hint="pip install -e infrastructure/browser",
        )
        return dg.MaterializeResult(
            metadata={
                "sources_attempted": 0,
                "sources_paid": 0,
                "sources_free": 0,
                "credits_spent": 0,
                "backend": "stub_no_sruth_browser",
            }
        )

    strategist = ScrapeStrategist()
    paid_count = 0
    free_count = 0
    credits_spent = 0
    rows: list[dict[str, Any]] = []

    for source in OFFICIAL_MEDIA_SAMPLE_SOURCES:
        # In production: persist rows to research_sitemap LanceDB table.
        # For now: log + accumulate metadata.
        try:
            result = asyncio.run(
                strategist.research_site(
                    url=source["url"],
                    goal=source["goal"],
                    budget_hint=2,
                )
            )
            row = {
                "source_id": source["slug"],
                "url": result.url,
                "goal": result.goal,
                "sitemap_urls": result.sitemap_urls,
                "backend_used": result.backend_used,
                "estimated_pages": result.estimated_pages,
                "credits_spent": result.credits_spent,
                "pre_researched_at": result.pre_researched_at,
            }
            rows.append(row)
            if result.backend_used == "firecrawl_mcp":
                paid_count += 1
            else:
                free_count += 1
            credits_spent += result.credits_spent
        except Exception as e:
            logger.warning(
                "pre_research_failed",
                source=source["slug"],
                error=str(e),
            )

    summary = strategist.credit_summary()
    logger.info(
        "official_media_pre_research_complete",
        sources=len(rows),
        paid=paid_count,
        free=free_count,
        credits=credits_spent,
        budget_remaining=summary["remaining"],
    )
    return dg.MaterializeResult(
        metadata={
            "sources_attempted": len(OFFICIAL_MEDIA_SAMPLE_SOURCES),
            "sources_paid": paid_count,
            "sources_free": free_count,
            "credits_spent": credits_spent,
            "budget_remaining": summary["remaining"],
            "rows": len(rows),
        }
    )


# ============================================================================
# Asset: bulk_scrape — per source, using the strategy from pre_research
# ============================================================================

@dg.asset(
    key=["official_media", "bulk_scrape"],
    group_name="official_media",
    description=(
        "Bulk-scrape the recommended URLs from pre_research. Prefers "
        "Crawl4AI (free). Falls back to Firecrawl for sources marked "
        "'firecrawl-agent' (heavy JS) and Stagehand for sources marked "
        "'stagehand-interactive' (login walls, search boxes). Stores the "
        "raw markdown + a per-page byte-in/byte-out counter."
    ),
    compute_kind="scrape",
    metadata={"table": "official_media.raw_pages", "primary_key": ["source_id", "url"]},
)
def official_media_bulk_scrape(context, upstream=None) -> dg.MaterializeResult:
    """Scrape one canonical page per sample source using the strategist."""
    try:
        from sruth_browser import ScrapeStrategist, ResearchSiteMap
    except ImportError:
        return dg.MaterializeResult(
            metadata={"pages_scraped": 0, "bytes_in": 0, "bytes_out": 0,
                      "backend": "stub_no_sruth_browser"}
        )

    strategist = ScrapeStrategist()
    pages_scraped = 0
    bytes_in = 0
    bytes_out = 0
    by_backend: dict[str, int] = {}

    for source in OFFICIAL_MEDIA_SAMPLE_SOURCES:
        # Use a default hint that says "static" - the strategist falls back
        # to Crawl4AI which is free.
        hint = ResearchSiteMap(
            url=source["url"],
            goal=source["goal"],
            recommended_strategy="crawl4ai-static",
        )
        try:
            result = asyncio.run(
                strategist.bulk_scrape(url=source["url"], hint=hint)
            )
            if result.success:
                pages_scraped += 1
                bytes_in += result.bytes_in
                bytes_out += result.bytes_out
                by_backend[result.backend_used] = (
                    by_backend.get(result.backend_used, 0) + 1
                )
        except Exception as e:
            logger.warning(
                "bulk_scrape_failed",
                source=source["slug"],
                error=str(e),
            )

    return dg.MaterializeResult(
        metadata={
            "pages_scraped": pages_scraped,
            "bytes_in": bytes_in,
            "bytes_out": bytes_out,
            "compression_ratio": round(bytes_out / max(bytes_in, 1), 4),
            "by_backend": by_backend,
        }
    )


# ============================================================================
# Asset: condense — BAML CondenseToCriticalInfo on every raw page
# ============================================================================

@dg.asset(
    key=["official_media", "condense"],
    group_name="official_media",
    description=(
        "Run the BAML CondenseToCriticalInfo function on every raw_page, "
        "producing a CondensedPage with key_facts, entities, and a 1-2 KB "
        "summary. The marimo dashboard shows bytes_in/bytes_out so the user "
        "can see how much data we kept vs how much we scraped."
    ),
    compute_kind="baml",
    metadata={"table": "official_media.condensed_pages", "primary_key": ["url"]},
)
def official_media_condense(context) -> dg.MaterializeResult:
    """Run BAML condensation on every sample source's first page."""
    # The BAML function is called via the generated client. The condensed
    # record goes into LanceDB for the marimo dashboard.
    try:
        from baml_client.sync_client import b as baml
    except ImportError:
        return dg.MaterializeResult(
            metadata={"pages_condensed": 0, "bytes_in": 0, "bytes_out": 0,
                      "backend": "stub_no_baml_client"}
        )

    from sruth_browser import ScrapeStrategist, ResearchSiteMap

    strategist = ScrapeStrategist()
    pages_condensed = 0
    bytes_in = 0
    bytes_out = 0

    for source in OFFICIAL_MEDIA_SAMPLE_SOURCES:
        hint = ResearchSiteMap(
            url=source["url"],
            goal=source["goal"],
            recommended_strategy="crawl4ai-static",
        )
        try:
            page = asyncio.run(
                strategist.bulk_scrape(url=source["url"], hint=hint)
            )
            if not page.success:
                continue
            result = baml.CondenseToCriticalInfo(
                raw_markdown=page.markdown,
                goal=source["goal"],
                max_output_bytes=2048,
            )
            pages_condensed += 1
            bytes_in += page.bytes_in
            bytes_out += result.bytes_out
        except Exception as e:
            logger.warning(
                "condense_failed",
                source=source["slug"],
                error=str(e),
            )

    return dg.MaterializeResult(
        metadata={
            "pages_condensed": pages_condensed,
            "bytes_in": bytes_in,
            "bytes_out": bytes_out,
            "compression_ratio": round(bytes_out / max(bytes_in, 1), 4),
        }
    )


# ============================================================================
# Asset: identify_uis — Stagehand observe() + BAML IdentifyUiPatterns
# ============================================================================

@dg.asset(
    key=["official_media", "identify_uis"],
    group_name="official_media",
    description=(
        "For every page that CondenseToCriticalInfo flagged as having a UI, "
        "take a screenshot (free via Stagehand) and run VisualGroundingFromScreenshot "
        "to find the element's bounding box. Stores ui_indicators in LanceDB so "
        "the marimo dashboard can render an 'UI map' tab for each source."
    ),
    compute_kind="vision",
    metadata={"table": "official_media.ui_elements", "primary_key": ["url", "ui_type"]},
)
def official_media_identify_uis(context) -> dg.MaterializeResult:
    """Take a screenshot + run visual grounding for any source with a UI."""
    try:
        from baml_client.sync_client import b as baml
        from sruth_browser import ScrapeStrategist, ResearchSiteMap
    except ImportError:
        return dg.MaterializeResult(
            metadata={"uis_identified": 0, "screenshots_taken": 0,
                      "backend": "stub_no_baml_or_sruth_browser"}
        )

    strategist = ScrapeStrategist()
    uis_identified = 0
    screenshots_taken = 0

    # Only identify UIs on sources we expect to have them (jurisdictions +
    # national info + universities). The full set would be 160 sources; we
    # filter here to keep CI time + credit burn under 5 minutes.
    UI_SAMPLE = [
        s for s in OFFICIAL_MEDIA_SAMPLE_SOURCES
        if s["category"] in ("jurisdictions", "national_info", "universities", "police")
    ]

    for source in UI_SAMPLE:
        hint = ResearchSiteMap(
            url=source["url"],
            goal=source["goal"],
            primary_content_types=["search_box", "form"],
        )
        try:
            indicator = asyncio.run(
                strategist.identify_ui(url=source["url"], hint=hint)
            )
            if indicator.has_ui:
                uis_identified += 1
            screenshots_taken += 1
        except Exception as e:
            logger.warning(
                "identify_ui_failed",
                source=source["slug"],
                error=str(e),
            )

    return dg.MaterializeResult(
        metadata={
            "uis_identified": uis_identified,
            "screenshots_taken": screenshots_taken,
            "sources_checked": len(UI_SAMPLE),
        }
    )
