#!/usr/bin/env python3
"""scripts/fibo_render.py — the canonical FIBO 2D diagram CLI.

Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

Usage:
    # Render a single concept (uses sample concept)
    uv run python scripts/fibo_render.py --subject mathematics

    # List the canonical 8 NCCA subjects
    uv run python scripts/fibo_render.py --list-subjects

    # Show the full BAML prompt for one subject
    uv run python scripts/fibo_render.py --subject chemistry --show-prompt

    # Render all 8 subjects in EN + GA (16 assets)
    uv run python scripts/fibo_render.py --render-all

The CLI:
1. Looks up the canonical FIBO prompt template (per education_fibo.py)
2. Builds a typed FiboConfig record (per schemas.py)
3. Writes the JSON config to stedding/fibo/<subject>/<lang>/<config_id>.fibo.json
4. Calls FiboResource.render() (per resources.py) → PNG + sidecar manifest
5. Calls ValidationResource.validate() (per resources.py) → VLM score

When the litellm gateway / VLM is unreachable, both steps gracefully
fall back to stub behaviour (placeholder PNG + null score).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tuatha.asset_generation.fibo import (
    EDUCATION_FIBO_PROMPTS,
    get_fibo_prompt,
    list_subjects,
)
from tuatha.asset_generation.fibo.assets import (
    
    
    fibo_configs_from_syllabus_diagrams,
    fibo_json_configs,
    generated_images,
)
from tuatha.asset_generation.fibo.resources import (
    FiboResource,
    ValidationResource,
)


def _print_subjects() -> None:
    print("\n  CANONICAL 8 NCCA SUBJECTS (per the FIBO 2D diagram pipeline)")
    print("  " + "-" * 70)
    for i, subject in enumerate(list_subjects(), 1):
        prompt = get_fibo_prompt(subject, "en")
        print(f"  {i}. {subject:<25s} deity={prompt['tuatha_de_deity']}")
    print()


async def _render_one(subject: str, language: str = "en") -> dict:
    """Render one FIBO config + asset for one subject."""
    prompt_data = get_fibo_prompt(subject, language)
    print(f"\n  Subject: {subject} ({language})")
    print(f"  Deity:   {prompt_data['tuatha_de_deity']}")
    print(f"  Prompt:  {prompt_data['prompt'][:80]}...")

    # Step 1: Build a FiboConfig + write the JSON
    config_id = f"fibo-{subject}-{language}-cli"
    prompt = prompt_data["prompt"]
    palette_hex = ["#1a0e1a", "#d4af37", "#f0e6d2", "#3a4f8c"]
    out_dir = Path("stedding/fibo") / subject / language
    out_dir.mkdir(parents=True, exist_ok=True)
    config_path = out_dir / f"{config_id}.fibo.json"
    config_path.write_text(json.dumps({
        "config_id": config_id,
        "subject": subject,
        "language": language,
        "prompt": prompt,
        "palette_hex": palette_hex,
        "iconography": [prompt_data["tuatha_de_deity"], prompt_data["tuatha_de_treasure"]],
        "width": 1024,
        "height": 1024,
        "validation_criteria": ["uses the palette correctly", f"subject = {subject}"],
        "max_refinement_iterations": 3,
    }, indent=2))
    print(f"  Config written: {config_path}")

    # Step 2: Render via FiboResource
    fr = FiboResource(model_name="local/image/qwen-image", api_base="http://192.168.148.5:8889/v1", api_key="sk-unsloth-dev-noop-key")
    out_path = out_dir / f"{config_id}.png"
    render_result = fr.render(
        prompt=f"FIBO educational diagram: {prompt}",
        palette_hex=palette_hex,
        out_path=str(out_path),
    )
    print(f"  Rendered:  {render_result['path']}")
    print(f"  SHA256:    {render_result['sha256'][:24]}...")
    print(f"  Stub:      {render_result['stub']}")

    # Step 3: Validate via VLM
    vr = ValidationResource(score_threshold=0.7)
    val = vr.validate(
        asset_path=render_result["path"],
        criteria=["uses the palette correctly", f"subject = {subject}"],
    )
    print(f"  Validation: score={val.get('score', 0)}, pass={val.get('pass', False)}, stub={val.get('stub', False)}")

    return {
        "subject": subject,
        "language": language,
        "config_path": str(config_path),
        "asset_path": render_result["path"],
        "sha256": render_result["sha256"],
        "stub": render_result["stub"] or val.get("stub", False),
        "validation_score": val.get("score", 0),
    }


async def _render_all() -> list[dict]:
    """Render all 8 subjects × 2 languages = 16 assets."""
    results = []
    for subject in list_subjects():
        for language in ("en", "ga"):
            r = await _render_one(subject, language)
            results.append(r)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--subject", help="Render one subject (e.g. mathematics, chemistry)")
    parser.add_argument("--language", default="en", choices=["en", "ga"])
    parser.add_argument("--list-subjects", action="store_true", help="List the 8 canonical subjects + deities + exit")
    parser.add_argument("--show-prompt", action="store_true", help="With --subject: show the full BAML prompt + exit")
    parser.add_argument("--render-all", action="store_true", help="Render all 8 subjects × 2 languages = 16 assets")
    args = parser.parse_args()

    print("=" * 70)
    print("  FIBO 2D DIAGRAM CLI")
    print("  Plan 4 of the 2026-10 convergence saga")
    print("  openspec/plans/2026-10-01-convergence-saga-v1.md")
    print("=" * 70)

    if args.list_subjects:
        _print_subjects()
        return 0

    if args.subject and args.show_prompt:
        prompt = get_fibo_prompt(args.subject, args.language)
        print(f"\n  Subject: {args.subject} ({args.language})")
        for k, v in prompt.items():
            print(f"  {k}: {v}")
        return 0

    if args.render_all:
        results = asyncio.run(_render_all())
        print(f"\n  DONE: {len(results)} assets rendered")
        return 0

    if args.subject:
        r = asyncio.run(_render_one(args.subject, args.language))
        print(f"\n  DONE: {r['subject']} asset at {r['asset_path']}")
        return 0

    parser.print_help()
    _print_subjects()
    return 1


if __name__ == "__main__":
    sys.exit(main())
