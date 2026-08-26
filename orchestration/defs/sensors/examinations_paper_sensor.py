"""Examinations.ie paper sensor — daily poll-on-demand change detection.

Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1` change
(Phase 4a). This sensor polls `examinations.ie/?lang=en&search=`
once per day (via the Firecrawl MCP `scrape` + cache) and compares
the new list against the manifest table. When new papers appear, it
triggers a re-materialization of the affected asset.

This is the **poll-on-demand** pattern (vs. Firecrawl Monitor's
push-based). Cheaper (1 scrape/day, cached) but still catches new
releases within 24h.
"""
from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from dagster import (
    AssetKey,
    RunRequest,
    SensorEvaluationContext,
    sensor,
)

logger = logging.getLogger(__name__)


# The 6 LC subjects covered by this sensor.
LC_SUBJECTS = ["mathematics", "chemistry", "physics", "biology", "english", "gaeilge"]

# The manifest table records the last-seen paper codes per subject.
# The sensor diffs the new search results against this manifest.
MANIFEST_QUERY = """
SELECT subject, year, paper_code
FROM cianfhoghlaim.lc_exam_papers.manifest
WHERE scraped_at >= ?
ORDER BY scraped_at DESC
LIMIT 100
"""


def _scrape_examinations_ie_search(*, lang: str = "en") -> list[dict[str, str]]:
    """Scrape the examinations.ie search page (cached for 24h)."""
    try:
        from agents.meaisinfhoghlaim.firecrawl_mcp import FirecrawlMCPClient

        client = FirecrawlMCPClient()
        result = client.scrape(
            f"https://www.examinations.ie/?lang={lang}",
            formats=["markdown", "links"],
            max_age=86_400_000,  # 24h cache
            redact_pii=True,
            zero_data_retention=True,
        )
        # Parse the markdown for new paper codes (the format is
        # "<subject> <year> <paper_code>"). The canonical pattern
        # is a markdown list of papers.
        papers: list[dict[str, str]] = []
        for line in result.markdown.splitlines():
            line = line.strip()
            if not line:
                continue
            for subject in LC_SUBJECTS:
                if subject in line.lower():
                    # Extract the year + paper code via a simple regex
                    import re

                    match = re.search(r"(\d{4})[-/](\w+)", line)
                    if match:
                        papers.append(
                            {
                                "subject": subject,
                                "year": int(match.group(1)),
                                "paper_code": match.group(2),
                                "lang": lang,
                            }
                        )
        return papers
    except Exception as exc:
        logger.warning("examinations_paper_sensor.scrape_failed: %s", exc)
        return []


def _diff_against_manifest(
    new_papers: list[dict[str, str]],
    known_papers: set[tuple[str, int, str]],
) -> list[dict[str, str]]:
    """Return the papers that are new (not in the manifest)."""
    return [
        p
        for p in new_papers
        if (p["subject"], p["year"], p["paper_code"]) not in known_papers
    ]


def _get_manifest() -> set[tuple[str, int, str]]:
    """Read the manifest table (the canonical known-papers set)."""
    try:
        import duckdb

        con = duckdb.connect("md:cianfhoghlaim")
        yesterday = datetime.now(UTC) - __import__("datetime").timedelta(days=30)
        rows = con.execute(MANIFEST_QUERY, [yesterday]).fetchall()
        return {(r[0], r[1], r[2]) for r in rows}
    except Exception:
        # Manifest table may not exist yet (Phase 4a bootstrap)
        return set()


# ============================================================================
# NOT REGISTERED 2026-08-14 — the `@sensor(...)` decorator is commented out
# below because BOTH of its targets are missing, and a sensor pointing at a
# nonexistent job makes `Definitions.validate_loadable()` raise, which takes
# the ENTIRE code location down to zero assets:
#
#   * job   `examinations_paper_job`  — defined nowhere in the repo
#   * asset `examinations_papers`     — defined nowhere (the RunRequests below
#                                       select it via `asset_selection`)
#
# To register it, define the `examinations_papers` asset, then restore the
# decorator. Because the RunRequests carry `asset_selection`, prefer the
# asset-targeting form over `job_name`:
#
#     @sensor(
#         target=dg.AssetSelection.assets("examinations_papers"),
#         description="Poll-on-demand sensor for examinations.ie exam papers (daily)",
#         minimum_interval_seconds=86_400,
#     )
#
# The sensor body itself is left intact and is correct.
# ============================================================================
# @sensor(
#     job_name="examinations_paper_job",
#     description="Poll-on-demand sensor for examinations.ie exam papers (daily)",
#     minimum_interval_seconds=86_400,  # 24h
# )
def examinations_paper_sensor(context: SensorEvaluationContext) -> Any:
    """The daily poll-on-demand sensor for examinations.ie."""
    new_papers_en = _scrape_examinations_ie_search(lang="en")
    new_papers_ga = _scrape_examinations_ie_search(lang="ga")
    all_new = new_papers_en + new_papers_ga

    known = _get_manifest()
    new_only = _diff_against_manifest(all_new, known)

    if not new_only:
        context.log.info("examinations_paper_sensor.no_new_papers")
        return None

    for paper in new_only:
        run_key = f"{paper['subject']}_{paper['year']}_{paper['paper_code']}"
        context.update_cursor(run_key)
        yield RunRequest(
            run_key=run_key,
            asset_selection=[
                AssetKey(["examinations_papers"]),
            ],
            tags={
                "subject": paper["subject"],
                "year": str(paper["year"]),
                "paper_code": paper["paper_code"],
                "sensor": "examinations_paper_sensor",
            },
        )

    context.log.info(
        f"examinations_paper_sensor.triggered: {len(new_only)} new papers"
    )
    return None