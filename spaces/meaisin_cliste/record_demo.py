"""
spaces/meaisin_cliste/record_demo.py
Record a demo sequence for Space 2 (Meaisin Cliste).

Usage:
    python -m spaces.meaisin_cliste.record_demo
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
        title="Meaisin Cliste - Celtic AI Tools",
        element="aer",
    )
    seq.add_voiceover(
        "Welcome to Meaisin Cliste, Space 2 of 4. The element is Aer, "
        "the language-carrier, with Uisce for the water theme."
    )
    seq.add("tab_select", "Focloir na Se Naisiun", "user opens Tab 1")
    seq.add_voiceover(
        "Three themes. The first is Focloir na Se Naisiun - a 6-nation "
        "Celtic cognate dictionary. Thirty hand-picked cognates, all "
        "grounded in the same proto-Celtic roots."
    )
    seq.add("cognate_search", "sea", "user searches for 'sea'")
    seq.add("cognate_results", "*mori-", "match found")

    seq.add("tab_select", "Scoil ar an Learscail", "user opens Tab 2")
    seq.add_voiceover(
        "The second theme is Scoil ar an Learscail - school on the map. "
        "Twenty-six counties, sixteen hundred and twenty-nine schools, "
        "coloured by the Pobal HP Deprivation Index 2022."
    )

    seq.add("tab_select", "Curaclam Trasteorann", "user opens Tab 3")
    seq.add_voiceover(
        "The third theme is Curaclam Trasteorann - cross-border "
        "curriculum. The BAML chain compares how a topic is taught "
        "across five Celtic-nation curricula."
    )
    seq.add("curaclam_query", "atomic structure", "user queries")
    seq.add("curaclam_result", "5 nations (IE/NI/WLS/IM/SCT)", "result")
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
