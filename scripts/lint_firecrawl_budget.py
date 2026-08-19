"""Lint the Firecrawl budget.

Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1` change
(Phase 4a). Reads `cianfhoghlaim.firecrawl_meta.budget` (the rolling
budget tracker populated by the `firecrawl_budget_asset`) and exits
1 if any pipeline exceeds 150% of its monthly allocation.

Usage:
    uv run python scripts/lint_firecrawl_budget.py
    mise run lint:firecrawl-budget
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


BUDGET_QUERY = """
SELECT day, credits_used, scrapes_count, pipelines, top_urls, over_budget
FROM cianfhoghlaim.firecrawl_meta.budget
ORDER BY day DESC
LIMIT 1
"""


def main() -> int:
    try:
        import duckdb
    except ImportError:
        print("ERROR: duckdb is required. Install with: uv add duckdb", file=sys.stderr)
        return 2

    con = duckdb.connect("md:cianfhoghlaim")
    try:
        rows = con.execute(BUDGET_QUERY).fetchall()
    except Exception as exc:
        print(f"ERROR: could not read firecrawl_meta.budget: {exc}", file=sys.stderr)
        return 1

    if not rows:
        print("ERROR: no budget rows found. Run `mise run dagster:dev` first to materialise firecrawl_budget_asset.", file=sys.stderr)
        return 1

    day, credits_used, scrapes_count, pipelines_json, top_urls_json, over_budget = rows[0]

    print(f"Firecrawl budget for {day}:")
    print(f"  Total scrapes: {scrapes_count}")
    print(f"  Total credits: {credits_used}")
    print(f"  Over budget: {over_budget}")
    print()

    try:
        pipelines = json.loads(pipelines_json) if pipelines_json else {}
    except Exception:
        pipelines = {}

    over_budget_pipelines = []
    for pipeline, stats in sorted(pipelines.items()):
        marker = "❌" if stats.get("over_budget") else "  "
        print(
            f"  {marker} {pipeline:<50s} "
            f"{stats.get('used', 0):>6d}/{stats.get('allocation', 0):>5d} "
            f"({stats.get('ratio', 0):.1%})"
        )
        if stats.get("over_budget"):
            over_budget_pipelines.append(pipeline)

    if over_budget_pipelines:
        print()
        print(f"FAIL: {len(over_budget_pipelines)} pipeline(s) over budget (>150%):")
        for p in over_budget_pipelines:
            print(f"  - {p}")
        return 1

    print()
    print("OK: all pipelines within budget")
    return 0


if __name__ == "__main__":
    sys.exit(main())