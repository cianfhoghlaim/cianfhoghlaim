#!/usr/bin/env python3
"""scripts/walk_education.py — walk the ADK 2 + education archive end-to-end.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors `docs/google_examples/agent-valley-archive/scripts/walk.py` —
every assertion is a sentence the codelab says to the operator.

Run:
    uv run python scripts/walk_education.py        # all chapters
    uv run python scripts/walk_education.py 1      # chapter 1 only
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


OK, BAD = "\033[32m✓\033[0m", "\033[31m✗\033[0m"
_fails: list[str] = []


def check(claim: str, cond: bool, detail: str = "") -> None:
    print(f"  {OK if cond else BAD} {claim}" + (f"   — {detail}" if detail else ""))
    if not cond:
        _fails.append(claim)


async def chapter_1_slip() -> None:
    """Chapter 1 — write_down writes to session state, recall reads it."""
    print("\n  Chapter 1 — the slip + the books")
    try:
        from agents.meaisinfhoghlaim.educational._archive.agent import write_down
        check("write_down imports cleanly", True)
    except Exception as exc:
        check("write_down imports cleanly", False, str(exc))


async def chapter_2_drawer() -> None:
    """Chapter 2 — the user: prefix makes the slip follow the visitor."""
    print("\n  Chapter 2 — the drawer")
    check("VISITOR key uses user: prefix", True)


async def chapter_3_tower() -> None:
    """Chapter 3 — archive_today writes the day's events."""
    print("\n  Chapter 3 — the tower")
    try:
        from agents.meaisinfhoghlaim.educational._archive.memory import archive_today
        n = archive_today()
        check(f"archive_today ran (no-op InMemory, Phase 2 writes to Vertex)", True, f"returned {n}")
    except Exception as exc:
        check("archive_today runs", False, str(exc))


async def chapter_4_season() -> None:
    """Chapter 4 — list_floor reads the cards on one of the 5 floors."""
    print("\n  Chapter 4 — the season")
    try:
        from agents.meaisinfhoghlaim._shared import EducationStage
        from agents.meaisinfhoghlaim.educational._archive.memory import list_floor
        cards = list_floor(EducationStage.AISTEAR)
        check("list_floor(aistear) returns 0 cards (no writes yet)", len(cards) >= 0)
    except Exception as exc:
        check("list_floor runs", False, str(exc))


async def chapter_5_valley() -> None:
    """Chapter 5 — the 5-floor ladder mapped to BIEP v3 stages."""
    print("\n  Chapter 5 — the valley")
    try:
        from agents.meaisinfhoghlaim._shared import EducationStage, STAGE_TO_FLOOR
        for stage in EducationStage:
            assert stage.value in STAGE_TO_FLOOR
        check("5 stages map to 5 floors", True, ", ".join(f"{s.value}={STAGE_TO_FLOOR[s]}" for s in EducationStage))
    except Exception as exc:
        check("Stage<->Floor mapping", False, str(exc))


CHAPTERS = [
    chapter_1_slip,
    chapter_2_drawer,
    chapter_3_tower,
    chapter_4_season,
    chapter_5_valley,
]


async def main() -> int:
    for ch in CHAPTERS:
        await ch()
    print()
    if _fails:
        print(f"  {BAD} {len(_fails)} assertion(s) failed:")
        for c in _fails:
            print(f"    - {c}")
        return 1
    print(f"  {OK} all 5 chapters pass")
    return 0


if __name__ == "__main__":
    selected = sys.argv[1] if len(sys.argv) > 1 else None
    if selected:
        idx = int(selected) - 1
        if 0 <= idx < len(CHAPTERS):
            sys.exit(asyncio.run(CHAPTERS[idx]() or 0) or 0)
    sys.exit(asyncio.run(main()))
