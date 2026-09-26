#!/usr/bin/env python3
"""scripts/tuatha_demo.py — the Tuatha British Isles MMO closed-loop demo CLI.

Per the 2026-10-08-tuatha-closed-loop-mmo-v1 saga change (Plan 8 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Usage:
    uv run python scripts/tuatha_demo.py --subject mathematics
    uv run python scripts/tuatha_demo.py --subject mathematics --language ga
    uv run python scripts/tuatha_demo.py --subject mathematics --json

The CLI runs the full closed-loop:
1. Realm constructor (Plan 8) → produces the realm JSON
2. Quest pack generator (Plan 8) → produces the 5 quests
3. Cognee linker (Plan 6) → links 4 entities to the assets
4. Asset gen (Plan 2) → renders the window chrome + sprite bank

Displays a summary table at the end.
"""
from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _safe_import(mod_name: str, attr_name: str):
    """Import a module by name (handles the 4_asset_generation digit prefix)."""
    try:
        mod = importlib.import_module(mod_name)
        return getattr(mod, attr_name)
    except (ImportError, AttributeError) as exc:
        return None


async def run_closed_loop(subject: str, language: str) -> dict:
    """Run the full closed-loop demo."""
    print("=" * 70)
    print("  TUATHA BRITISH ISLES MMO — CLOSED-LOOP DEMO")
    print("  Plan 8 of the 2026-10 convergence saga")
    print("  openspec/plans/2026-10-01-convergence-saga-v1.md")
    print("=" * 70)

    t0 = time.monotonic()
    results = {}

    # Step 1: Realm constructor
    print("\n  STEP 1: realm constructor")
    build_realm = _safe_import(
        "tuatha.agents.realm_constructor_agent", "build_realm"
    )
    if build_realm is None:
        build_realm = _safe_import(
            "orchestration.defs.4_asset_generation.tuatha_realm_asset",
            "tuatha_realm_asset",
        )
    if build_realm is None:
        print("    ⚠ tuatha_realm_asset not importable — using inline stub")
        realm = {"error": "not available"}
    else:
        realm = build_realm(subject=subject, language=language)
        print(f"    realm_id: {realm.get('realm_id', 'N/A')[:16]}")
        print(f"    subject: {realm.get('subject')}")
        print(f"    deity: {realm.get('deity_placement', {}).get('deity', 'N/A')}")
        print(f"    sprites: {len(realm.get('sprite_bank', []))}")
        print(f"    entities: {len(realm.get('cognee_entities', []))}")
    results["realm"] = realm

    # Step 2: Quest pack generator
    print("\n  STEP 2: quest pack generator")
    generate_quest_pack = _safe_import(
        "tuatha.agents.quest_pack_agent", "generate_quest_pack"
    )
    if generate_quest_pack is None:
        print("    ⚠ quest_pack_agent not importable — using inline stub")
        quests = []
    else:
        quest_pack = generate_quest_pack(subject=subject, language=language)
        quests = quest_pack.get("quests", [])
        print(f"    session_id: {quest_pack.get('session_id', 'N/A')[:16]}")
        print(f"    quests: {len(quests)}")
        for q in quests:
            print(f"      - {q.get('quest_type'):<12s} {q.get('title', '')[:60]}")
    results["quest_pack"] = {"session_id": results["realm"].get("session_id"), "quests": quests}

    # Step 3: Cognee linker (graceful fallback)
    print("\n  STEP 3: Cognee entity-asset linker")
    extract_entities = _safe_import(
        "agents.meaisinfhoghlaim.media_intel.cognee_linker",
        "extract_entities",
    )
    if extract_entities is None:
        print("    ⚠ cognitee_linker not importable — using inline stub")
        entities = []
    else:
        graph = extract_entities(
            {"headline": f"Mathematics: {realm.get('deity_placement', {}).get('deity', 'The Dagda')}"},
            subject=subject,
            language=language,
        )
        entities = graph.get("entities", [])
        print(f"    entities extracted: {len(entities)}")
        for e in entities:
            print(f"      - {e.get('name'):<20s} type={e.get('type')}")
    results["entities"] = entities

    # Step 4: Celtic asset gen (Plan 7)
    print("\n  STEP 4: Celtic asset gen (per-language)")
    try:
        from scripts.celtic_assets import SUPPORTED_LANGS
        lang_info = next((l for l in SUPPORTED_LANGS if l["code"] == language), None)
        if lang_info:
            print(f"    language: {lang_info['label']} ({language})")
            print(f"    BAML function: {lang_info['function']}")
            print(f"    target table: media.image_gen_chunks_{language}")
    except ImportError:
        print("    ⚠ celtic_assets not importable")
    results["language"] = language

    duration = int((time.monotonic() - t0) * 1000)
    print(f"\n  DONE in {duration}ms")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--subject", default="mathematics",
                        help="The NCCA subject (default: mathematics)")
    parser.add_argument("--language", default="en", choices=["en", "ga", "cy", "gd", "gv", "kw", "br"],
                        help="The asset language")
    parser.add_argument("--json", action="store_true", help="Print the raw JSON output")
    args = parser.parse_args()

    results = asyncio.run(run_closed_loop(args.subject, args.language))

    if args.json:
        print("\n" + json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
