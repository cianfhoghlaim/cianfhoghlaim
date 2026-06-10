"""
spaces/cianfhoghlaim/record_demo.py
Record a demo sequence for Space 3 (Cianfhoghlaim).

Usage:
    python -m spaces.cianfhoghlaim.record_demo

Produces:
  - storyboard.png    16:9 storyboard PNG
  - voiceover_script.txt   human-narrated voiceover script
  - demo_sequence.json     the full sequence
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as a script from the monorepo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from spaces._common.demo_recorder import (
    DemoSequence,
    export_voiceover_script,
    render_storyboard,
)
from spaces.cianfhoghlaim.npcs import NPCS


def build_sequence() -> DemoSequence:
    """Build a 5-turn demo sequence that touches 3 of the 6 NPCs."""
    seq = DemoSequence(
        title="Cianfhoghlaim - Tuatha RPG",
        element="anam",
    )
    seq.add_voiceover(
        "Welcome to Tuatha, the navigable British Isles. "
        "You are the wanderer, the cian-fhoghlaim. "
        "Six champions stand in the wind, each in their own corner."
    )
    seq.add("map_render", "1000x700 SVG, 6 zones, 6 NPC markers", "intro")

    # Turn 1: Manannan
    seq.add("npc_select", "manannan_mac_lir", "player picks Manannan")
    seq.add_voiceover(
        "Choose a champion. The first to greet you is Manannan mac Lir, "
        "the sea-god of the Otherworld, at Port Erin."
    )
    seq.add("player_input", "What do the tides bring you this morning?", "turn 1")
    seq.add("npc_response", "Hush, cian-fhoghlaim. The tide brings me a debt long owed.", "npc")
    seq.add_voiceover(
        "Manannan speaks. His answer is grounded in the cached Wikipedia "
        "article, his voice in the cultural memory of the Isle of Man."
    )

    # Turn 2: Rhiannon
    seq.add("npc_select", "rhiannon", "player moves to Dyfed")
    seq.add("player_input", "Lady of the birds, will you ride with me?", "turn 1")
    seq.add("npc_response", "I have not unsaddled since the Mabinogi. Why would I now?", "npc")

    # Turn 3: Cian
    seq.add("npc_select", "cian", "player moves to Cualann")
    seq.add("player_input", "Cian, do you know what became of Lugh?", "turn 1")
    seq.add("npc_response", "I knew him only as a name in a song. The rest is his to answer.", "npc")

    return seq


def main() -> None:
    out_dir = Path(__file__).parent
    seq = build_sequence()
    render_storyboard(seq, str(out_dir / "storyboard.png"))
    export_voiceover_script(seq, str(out_dir / "voiceover_script.txt"))
    seq.save_json(str(out_dir / "demo_sequence.json"))
    print(f"Demo recorded: {len(seq.steps)} steps, {seq.total_duration:.0f}s")
    print(f"  -> {out_dir / 'storyboard.png'}")
    print(f"  -> {out_dir / 'voiceover_script.txt'}")
    print(f"  -> {out_dir / 'demo_sequence.json'}")


if __name__ == "__main__":
    main()
