#!/usr/bin/env python3
"""scripts/cognee_link.py — the CLI demo for the Pillar 3 → Cognee entity-asset link.

Per the 2026-10-06-adk-cognee-visual-assets-v1 saga change (Plan 6 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Usage:
    # Link a single briefing
    uv run python scripts/cognee_link.py \
        --briefing "Julius Caesar was assassinated by Brutus on the Ides of March" \
        --subject history --language en

    # Run the full Plan 6 demo (the canonical Julius Caesar history briefing)
    uv run python scripts/cognee_link.py --demo

The CLI runs the 3-step chain:
1. link_briefing_to_cognee() — write the briefing as a LearningEpisode
2. extract_entities() — call the BAML ExtractEntities function (falls
   back to stub mode when BAML client isn't generated)
3. link_entities_to_assets() — create the CITED_IN edges in Cognee

When the Cognee endpoint is unreachable (offline dev mode), every step
falls back to a stub that returns deterministic IDs.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.meaisinfhoghlaim.media_intel.cognee_linker import (
    extract_entities,
    link_briefing_to_cognee,
    link_entities_to_assets,
)


CANONICAL_DEMO = {
    "briefing": {
        "headline": "The assassination of Julius Caesar by Brutus on the Ides of March",
        "sections": [
            "Caesar's rise to power as Roman dictator",
            "The conspiracy led by Brutus and Cassius",
            "The assassination in the Theatre of Pompey on the Ides of March, 44 BC",
        ],
    },
    "subject": "history",
    "language": "en",
}


async def run_one(
    briefing: dict, subject: str, language: str, asset_table: str
) -> dict:
    """Run the 3-step chain for one briefing."""
    print("=" * 70)
    print("  COGNEE LINK DEMO")
    print("  Plan 6 of the 2026-10 convergence saga")
    print("  openspec/plans/2026-10-01-convergence-saga-v1.md")
    print("=" * 70)
    print(f"\n  Subject: {subject}")
    print(f"  Language: {language}")
    print(f"  Asset table: {asset_table}")
    print(f"  Briefing headline: {briefing.get('headline', '')[:80]}...")

    print("\n  STEP 1: link_briefing_to_cognee")
    ep = link_briefing_to_cognee(briefing, subject=subject, language=language)
    print(f"    → episode_id: {ep['episode_id']}")
    print(f"    → created: {ep['created']}, stub: {ep['stub']}")

    print("\n  STEP 2: extract_entities")
    graph = extract_entities(briefing, subject=subject, language=language)
    print(f"    → {len(graph['entities'])} entities, {len(graph['relationships'])} relationships")
    for e in graph["entities"]:
        print(f"      - {e['name']:<30s} type={e['type']:<12s} id={e['entity_id'][:12]}")
    for r in graph["relationships"]:
        print(f"      - {r['type']}: {r['source_entity_id'][:12]} -> {r['target_entity_id'][:12]}")

    print("\n  STEP 3: link_entities_to_assets")
    result = link_entities_to_assets(graph["entities"], subject=subject, asset_table=asset_table)
    print(f"    → edges_created: {result['edges_created']}, stub: {result['stub']}")

    return {"episode": ep, "graph": graph, "edges": result}


async def run_demo() -> dict:
    """Run the canonical Julius Caesar history demo."""
    return await run_one(
        CANONICAL_DEMO["briefing"],
        CANONICAL_DEMO["subject"],
        CANONICAL_DEMO["language"],
        asset_table="image_gen_chunks",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--briefing", default=None, help="The briefing headline to extract entities from")
    parser.add_argument("--sections", nargs="*", default=None, help="Optional briefing sections")
    parser.add_argument("--subject", default="history", help="The NCCA subject (default: history)")
    parser.add_argument("--language", default="en", choices=["en", "ga"], help="The language")
    parser.add_argument("--asset-table", default="image_gen_chunks", help="The target asset table")
    parser.add_argument("--demo", action="store_true", help="Run the canonical Julius Caesar history demo")
    args = parser.parse_args()

    if args.demo:
        result = asyncio.run(run_demo())
        return 0

    if not args.briefing:
        parser.print_help()
        print()
        print("  Try: uv run python scripts/cognee_link.py --demo")
        return 1

    briefing = {
        "headline": args.briefing,
        "sections": args.sections or [args.briefing],
    }
    result = asyncio.run(
        run_one(briefing, args.subject, args.language, args.asset_table)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
