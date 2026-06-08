"""
scripts/render_social_cards.py
Render the 4 social cards (1200x630 PNG) for the HF Spaces.

Run once at build time; the resulting social_card.png is committed
to each Space's repo alongside app.py so HF can display it.

Usage:
    python scripts/render_social_cards.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from the monorepo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# Direct import (bypass gradio __init__)
import importlib.util
_baml_path = Path(__file__).parent / ".." / "spaces" / "_common" / "social_card.py"
_baml_path = _baml_path.resolve()
spec = importlib.util.spec_from_file_location("_social_card", _baml_path)
mod = importlib.util.module_from_spec(spec)
sys.modules["_social_card"] = mod
spec.loader.exec_module(mod)


SPACES: list[dict[str, str]] = [
    {
        "name_en": "An Scrudu",
        "name_ga": "An Scriodu",
        "tagline": "BAML extracts marking schemes from Irish Leaving Cert past papers. Talamh.",
        "model": "Qwen2.5-7B-Instruct",
        "out": "spaces/an_scrudu/social_card.png",
    },
    {
        "name_en": "Meaisin Cliste",
        "name_ga": "Meaisin Cliste",
        "tagline": "3 Celtic AI tools: 6-nation cognates, school map, cross-nation curriculum.",
        "model": "Qwen2.5-7B-Instruct",
        "out": "spaces/meaisin_cliste/social_card.png",
    },
    {
        "name_en": "Cianfhoghlaim",
        "name_ga": "Cianfhoghlaim",
        "tagline": "Hades-style dialogue with 6 Celtic NPCs on a British Isles map. Anam.",
        "model": "Qwen2.5-7B-Instruct",
        "out": "spaces/cianfhoghlaim/social_card.png",
    },
    {
        "name_en": "Anam Tuatha",
        "name_ga": "Anam: Tuatha na nGaelscoil",
        "tagline": "5 elements, 7 features, 1 soulbound wallet. The integration Space.",
        "model": "Qwen2.5-7B-Instruct",
        "out": "spaces/anam_tuatha/social_card.png",
    },
]


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    for space in SPACES:
        out = repo_root / space["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        result = mod.render_social_card(
            space_name_en=space["name_en"],
            space_name_ga=space["name_ga"],
            tagline=space["tagline"],
            model_alias=space["model"],
            output_path=str(out),
        )
        if result:
            print(f"  -> {out} ({out.stat().st_size:,} bytes)")
        else:
            print(f"  -> {out}: PIL not available, skipping PNG render")


if __name__ == "__main__":
    main()
