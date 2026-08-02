"""
spaces/an_scrudu/record_demo.py
Record a demo sequence for Space 1 (An Scrudu).

Usage:
    python -m spaces.an_scrudu.record_demo
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
        title="An Scrudu - Past Paper Heatmap",
        element="talamh",
    )
    seq.add_voiceover(
        "Welcome to An Scrudu, Space 1 of the Cianfhoghlaim Build Small "
        "2026 submission. The element is Talamh - Earth - the curriculum "
        "map itself."
    )
    seq.add("sample_select", "LC Chemistry 2024", "user picks the sample")
    seq.add_voiceover(
        "We use the built-in sample paper: Leaving Certificate Chemistry, "
        "Higher Level, 2024. The BAML chain extracts the marking scheme."
    )
    seq.add("extract_btn.click", None, "user clicks Extract")
    seq.add("baml_call", "Qwen 7B -> Llama 8B -> Gemma 9b (3-tier)", "BAML")
    seq.add_voiceover(
        "Three models in the fallback chain. If all fail, an offline "
        "regex fallback engages. The heatmap always renders."
    )
    seq.add("heatmap_render", "6 topics, 300 marks", "result")
    seq.add_voiceover(
        "The heatmap shows six topic codes, CH3 through CH8, each worth "
        "fifty marks. The Talamh-to-Anam gradient signals intensity."
    )
    seq.add("pclm_download", "PCLM XML + PDF", "export")
    seq.add_voiceover(
        "Download the PCLM-XML or a minimal PDF. Both are valid for the "
        "oideachais document factory round-trip."
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
