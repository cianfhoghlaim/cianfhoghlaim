#!/usr/bin/env python3
"""scripts/retro_capture.py — the canonical retro-gameplay capture CLI.

Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Usage:
    uv run python scripts/retro_capture.py --list-roms
    uv run python scripts/retro_capture.py hades               # default: capture title screen + extract pattern
    uv run python scripts/retro_capture.py number_munchers --platform nes --scene menu
    uv run python scripts/retro_capture.py hades --scene gameplay --save-state /stedding/ingest_queue/retro/switch/hades/save.sav

The CLI runs the full chain:
1. capture_screenshot(platform, game_id, scene_id) → PNG
2. sam3_segment(screenshot_path) → sprite bboxes
3. extract_retro_pattern(screenshot_path, ...) → typed RetroGameplayPattern
4. ingest_pattern_simple(...) → record for LanceDB upsert

All steps gracefully fall back to stub mode when their downstream
service (libretro + SAM3 + BAML) isn't running.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# Allow `uv run python scripts/retro_capture.py` from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.adk.tools.retro_capture import (
    RETRO_LIBRARY,
    capture_screenshot,
    list_roms,
)
from agents.adk.tools.retro_pattern_extractor import (
    extract_retro_pattern,
    sam3_segment,
)
from agents.adk.tools.retro_pattern_helpers import (
    build_embedding_text,
    ingest_pattern_simple,
)


# Lookup by game_id (find the matching retro_library entry)
def _find_rom(game_id: str) -> dict | None:
    for rom in RETRO_LIBRARY:
        if rom["game_id"] == game_id:
            return rom
    return None


def _print_roms_table() -> None:
    """Print a table of the canonical retro_library entries."""
    print()
    print("  CANONICAL RETRO LIBRARY (6 games, 5 platforms)")
    print("  " + "-" * 80)
    print(f"  {'platform':<10s} {'game_id':<30s} {'title':<40s}")
    print("  " + "-" * 80)
    for rom in RETRO_LIBRARY:
        print(f"  {rom['platform']:<10s} {rom['game_id']:<30s} {rom['title']:<40s}")
    print()
    print(f"  Total: {len(RETRO_LIBRARY)} games across 5 platforms")
    print()


async def capture_one(
    game_id: str,
    platform: str | None = None,
    scene_id: str = "title",
    save_state_path: str | None = None,
) -> dict:
    """Capture + segment + extract + ingest for one game."""
    rom = _find_rom(game_id)
    if rom is None:
        print(f"  ✗ game_id={game_id!r} not in retro_library. Use --list-roms.")
        return {"error": "not_found", "game_id": game_id}

    platform = platform or rom["platform"]
    print(f"  GAME:    {rom['title']} ({rom['platform']}, {rom['year']})")
    print(f"  ROM SHA: {rom['rom_sha256']}")

    t0 = time.monotonic()
    print("\n  STEP 1: capture screenshot")
    ss = await capture_screenshot(platform, game_id, scene_id, save_state_path=save_state_path)
    print(f"    → {ss.path}")
    print(f"    → sha256={ss.sha256[:24]}...")
    print(f"    → stub={ss.stub}, dur={ss.duration_ms}ms")

    print("\n  STEP 2: SAM3 sprite segmentation")
    segs = await sam3_segment(ss.path, classes=["character_portrait", "ui_button", "boon_icon"])
    print(f"    → {len(segs)} segments: classes={[s.get('class') for s in segs]}")

    print("\n  STEP 3: BAML ExtractGameplayPattern")
    pat = await extract_retro_pattern(
        screenshot_path=ss.path,
        game_id=game_id,
        platform=platform,
        rom_sha256=rom["rom_sha256"],
        scene_id=scene_id,
    )
    print(f"    → pattern_id={pat['pattern_id']}")
    print(f"    → title={pat['title'][:60]}")
    print(f"    → design_notes={pat['design_notes'][:80]}")

    print("\n  STEP 4: ingest into LanceDB")
    row = ingest_pattern_simple(
        platform=pat["platform"],
        game_id=pat["game_id"],
        scene_id=pat["scene_id"],
        title=pat["title"],
        genre=next(iter([k for k, v in pat["genre"].items() if v]), "other") if isinstance(pat["genre"], dict) else pat["genre"],
        design_notes=pat["design_notes"],
        palette_dominant_hex=pat["palette"].get("dominant_hex", []),
        palette_accent_hex=pat["palette"].get("accent_hex", []),
        palette_emissive_hex=pat["palette"].get("emissive_hex", []),
        power_events_json=json.dumps(pat["power_events"]),
        visual_grammar_json=json.dumps(pat["visual_grammar"]),
        source_rom_sha256=pat["source"]["rom_sha256"],
        source_screenshot_sha256=pat["source"]["screenshot_sha256"],
        source_save_state_path=pat["source"].get("save_state_path", ""),
        source_macro_script=pat["source"].get("macro_script", ""),
        source_captured_at=pat["source"].get("captured_at", ""),
    )
    print(f"    → pattern_id={row['pattern_id']}")
    print(f"    → ingested_at={row['ingested_at']}")

    print("\n  STEP 5: embedding text (for BGE-M3 LanceDB index)")
    et = build_embedding_text(row)
    print(f"    → {et[:120]}")

    duration = int((time.monotonic() - t0) * 1000)
    print(f"\n  DONE in {duration}ms")
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("game_id", nargs="?", default=None,
                        help="The retro_library game_id to capture (e.g. 'hades', 'number_munchers')")
    parser.add_argument("--platform", default=None,
                        help="Override the platform (default: from retro_library)")
    parser.add_argument("--scene", default="title",
                        help="Scene id (default: title)")
    parser.add_argument("--save-state", default=None, help="Optional save state path")
    parser.add_argument("--list-roms", action="store_true", help="List the canonical retro_library and exit")
    args = parser.parse_args()

    print("=" * 80)
    print("  RETRO GAMEPLAY CAPTURE CLI")
    print("  Plan 3 of the 2026-10 convergence saga")
    print("  openspec/plans/2026-10-01-convergence-saga-v1.md")
    print("=" * 80)

    if args.list_roms:
        _print_roms_table()
        return 0

    if not args.game_id:
        parser.print_help()
        print()
        _print_roms_table()
        return 1

    print(f"\n  Capturing: game_id={args.game_id}, scene={args.scene}")
    row = asyncio.run(capture_one(args.game_id, args.platform, args.scene, args.save_state))
    if "error" in row:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
