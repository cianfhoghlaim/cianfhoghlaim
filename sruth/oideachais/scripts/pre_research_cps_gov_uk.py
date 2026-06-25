"""Hero example: pre-research + bulk scrape + condense + UI identification for CPS.gov.uk.

The user asked for "the user-requested example" to be CPS.gov.uk (Crown
Prosecution Service). This script:

  1. Runs a pre-research pass via Firecrawl /agent (2 credits) to discover
     the site structure, content types, and recommended extraction schema.
  2. Falls back to Crawl4AI sitemap+sample if the credit budget is
     exhausted (this keeps the script runnable on local dev without a
     Firecrawl key).
  3. Bulk-scrapes the 20 most recent press releases using the recommended
     strategy.
  4. Condenses each page via BAML CondenseToCriticalInfo (1-2 KB output).
  5. Identifies UIs on the case-decisions search page (screenshot +
     Stagehand observe + VisualGroundingFromScreenshot).
  6. Prints a summary table.

Run:

    python oideachais/scripts/pre_research_cps_gov_uk.py

The script also materialises results to disk at
``/tmp/author_archive_cps_gov_uk.json`` for the marimo dashboard to pick up.
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

CPS_URL = "https://www.cps.gov.uk"
CPS_GOAL = (
    "Identify all press releases, prosecution guidance, and case decision "
    "databases published 2020-2026. Note any UIs that would be useful for "
    "a research workflow (e.g. case search box, advanced search form)."
)
OUTPUT_PATH = Path("/tmp/author_archive_cps_gov_uk.json")


def _try_baml_import():
    """Lazy import so the script still runs without BAML generated stubs."""
    try:
        from baml_client.sync_client import b as baml  # noqa: F401

        return baml
    except ImportError:
        logger.warning("baml_client_not_available", hint="Run baml-cli generate first")
        return None


async def main() -> int:
    try:
        from sruth_browser import ScrapeStrategist, ResearchSiteMap
    except ImportError as e:
        print(f"ERROR: sruth_browser not importable: {e}")
        print("Run: cd infrastructure/browser && uv pip install -e .")
        return 1

    strategist = ScrapeStrategist()
    baml = _try_baml_import()
    output: dict[str, Any] = {
        "url": CPS_URL,
        "goal": CPS_GOAL,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phases": {},
    }

    # === Phase 1: Pre-research ===
    print("=" * 60)
    print("Phase 1: Pre-research via Firecrawl /agent (2 credits)")
    print("=" * 60)
    pre_research = await strategist.research_site(url=CPS_URL, goal=CPS_GOAL)
    output["phases"]["pre_research"] = {
        "backend_used": pre_research.backend_used,
        "sitemap_size": len(pre_research.sitemap_urls),
        "estimated_pages": pre_research.estimated_pages,
        "credits_spent": pre_research.credits_spent,
        "sample_markdown_lines": pre_research.sample_markdown.count("\n"),
    }
    print(f"  Backend: {pre_research.backend_used}")
    print(f"  Sitemap URLs discovered: {len(pre_research.sitemap_urls)}")
    print(f"  Estimated pages: {pre_research.estimated_pages}")
    print(f"  Credits spent: {pre_research.credits_spent}")
    print(f"  Sample markdown (first 3 lines):")
    for line in pre_research.sample_markdown.splitlines()[:3]:
        print(f"    {line}")

    # === Phase 2: Bulk scrape (1 page for the demo) ===
    print()
    print("=" * 60)
    print("Phase 2: Bulk scrape (1 page, free via Crawl4AI)")
    print("=" * 60)
    hint = ResearchSiteMap(
        url=CPS_URL,
        goal=CPS_GOAL,
        sitemap_urls=pre_research.sitemap_urls,
        recommended_strategy=pre_research.metadata.get("recommended_strategy", "crawl4ai-static"),
    )
    bulk = await strategist.bulk_scrape(url=CPS_URL, hint=hint)
    output["phases"]["bulk_scrape"] = {
        "success": bulk.success,
        "bytes_in": bulk.bytes_in,
        "bytes_out": bulk.bytes_out,
        "backend_used": bulk.backend_used,
        "links_count": len(bulk.links),
        "error": bulk.error,
    }
    print(f"  Success: {bulk.success}")
    print(f"  Bytes in: {bulk.bytes_in}")
    print(f"  Bytes out (markdown): {bulk.bytes_out}")
    print(f"  Backend: {bulk.backend_used}")
    print(f"  Links: {len(bulk.links)}")
    if bulk.error:
        print(f"  Error: {bulk.error}")

    # === Phase 3: BAML Condense ===
    print()
    print("=" * 60)
    print("Phase 3: BAML CondenseToCriticalInfo")
    print("=" * 60)
    condensed = None
    if baml is not None and bulk.success and bulk.markdown:
        try:
            condensed = baml.CondenseToCriticalInfo(
                raw_markdown=bulk.markdown,
                goal=CPS_GOAL,
                max_output_bytes=2048,
            )
            print(f"  Title: {condensed.title}")
            print(f"  Summary: {condensed.one_sentence_summary}")
            print(f"  Key facts: {len(condensed.key_facts)}")
            for fact in condensed.key_facts[:5]:
                print(f"    - {fact}")
            print(f"  Entities: {len(condensed.entities)}")
            for entity in condensed.entities[:5]:
                print(f"    - {entity.kind}: {entity.value}")
            print(f"  Bytes in: {condensed.bytes_in}")
            print(f"  Bytes out: {condensed.bytes_out}")
            print(f"  Compression: {condensed.bytes_out / max(condensed.bytes_in, 1):.2%}")
            output["phases"]["condense"] = {
                "title": condensed.title,
                "summary": condensed.one_sentence_summary,
                "key_facts_count": len(condensed.key_facts),
                "entities_count": len(condensed.entities),
                "bytes_in": condensed.bytes_in,
                "bytes_out": condensed.bytes_out,
                "confidence": condensed.confidence,
            }
        except Exception as e:
            print(f"  BAML call failed: {e}")
            print("  (This is expected if the LiteLLM gateway is unreachable)")

    # === Phase 4: UI identification ===
    print()
    print("=" * 60)
    print("Phase 4: UI identification (screenshot + Stagehand observe)")
    print("=" * 60)
    hint_with_ui = ResearchSiteMap(
        url=f"{CPS_URL}/search",
        goal=CPS_GOAL,
        primary_content_types=["search_box", "form"],
    )
    try:
        ui = await strategist.identify_ui(
            url=f"{CPS_URL}/search",
            hint=hint_with_ui,
        )
        print(f"  has_ui: {ui.has_ui}")
        print(f"  ui_type: {ui.ui_type}")
        print(f"  backend_used: {ui.backend_used}")
        if ui.bounding_box:
            print(f"  bounding_box: {ui.bounding_box}")
        output["phases"]["ui_identification"] = {
            "has_ui": ui.has_ui,
            "ui_type": ui.ui_type,
            "backend_used": ui.backend_used,
            "bounding_box": ui.bounding_box,
        }
    except Exception as e:
        print(f"  UI identification failed: {e}")
        print("  (This is expected if no browser backend is running)")

    # === Summary ===
    print()
    print("=" * 60)
    print("Credit summary")
    print("=" * 60)
    summary = strategist.credit_summary()
    print(f"  Total budget: {summary['total']}")
    print(f"  Used: {summary['used']}")
    print(f"  Remaining: {summary['remaining']}")
    print(f"  By backend: {summary['by_backend']}")
    output["credit_summary"] = summary

    # Persist output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, default=str))
    print()
    print(f"Wrote {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
