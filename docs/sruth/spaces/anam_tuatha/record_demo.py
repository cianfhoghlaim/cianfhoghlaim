"""
spaces/anam_tuatha/record_demo.py
Record a demo sequence for Space 4 (Anam Tuatha).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from spaces._common.demo_recorder import (
    DemoSequence,
    export_voiceover_script,
    render_storyboard,
)


def build_sequence() -> DemoSequence:
    seq = DemoSequence(
        title="Anam - Tuatha na nGaelscoil",
        element="anam",
    )
    seq.add_voiceover(
        "Welcome to Anam, Space 4 of 4. The integration Space. "
        "Five elements, seven features, one soulbound wallet."
    )
    seq.add("tab_select", "Talamh", "user opens Talamh")
    seq.add_voiceover(
        "Panel 1: Talamh, Earth - the curriculum map. Lifted from "
        "Space 1, summarised here for the integration demo."
    )
    seq.add("tab_select", "Uisce", "user opens Uisce")
    seq.add_voiceover(
        "Panel 2: Uisce, Water - the chemistry visual. Eight molecules, "
        "CPK colours, hand-drawn SVG."
    )
    seq.add("tab_select", "Tine", "user opens Tine")
    seq.add_voiceover(
        "Panel 3: Tine, Fire - the OCR forge. The Gaelscribhneoir "
        "checks fada, eclipsis, and punctum on a sample Irish text."
    )
    seq.add("tab_select", "Anam", "user opens Anam")
    seq.add_voiceover(
        "Panel 5: Anam, Spirit - the soulbound token. Three stages, "
        "five elements, one wallet. Click an element to record a feat."
    )
    seq.add("feat_click", "talamh", "user clicks Talamh")
    seq.add("feat_click", "uisce", "user clicks Uisce")
    seq.add("feat_click", "tine", "user clicks Tine")
    seq.add("stage_progression", "setanta -> cuchulainn", "stage up!")
    seq.add_voiceover(
        "Two feats and the Setanta stage advances to Cuchulainn. "
        "Five feats unlock the Riastrad, the warp spasm."
    )
    return seq


def main() -> None:
    out_dir = Path(__file__).parent
    seq = build_sequence()
    render_storyboard(seq, str(out_dir / "storyboard.png"))
    export_voiceover_script(seq, str(out_dir / "voiceover_script.txt"))
    seq.save_json(str(out_dir / "demo_sequence.json"))
    print(f"Demo recorded: {len(seq.steps)} steps, {seq.total_duration:.0f}s")


if __name__ == "__main__":
    main()
