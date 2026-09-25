#!/usr/bin/env python3
"""scripts/asset_bench.py — the canonical asset-generation benchmark CLI.

Per the 2026-10-02-adk-asset-generation-pillar3-v1 saga change
(Plan 1 of openspec/plans/2026-10-01-convergence-saga-v1.md).

Usage:
    uv run python scripts/asset_bench.py "An Irish round tower at sunset"
    uv run python scripts/asset_bench.py "Roman colosseum" --role bilingual
    uv run python python scripts/asset_bench.py --pipeline aistear_deep_research --query "How do the 4 themes support wellbeing?"

The bench:
1. Resolves the image_gen MODEL_REGISTRY entries (flux2-dev + z-image-turbo +
   qwen-image + sdxl + fibo)
2. Generates 5 variants (one per role, cycling through the 5 image_gen entries)
3. Calls the LiteLLM gateway for real inference (via the new _generate_image)
4. Writes a timing report + a summary table to stdout
5. Gracefully degrades to placeholder PNGs if the gateway is unreachable
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

# Allow `uv run python scripts/asset_bench.py` from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.adk.tools.image_generation import (
    generate_2d_asset,
    generate_texture,
    list_image_models,
)


# The 5 image_gen roles from MODEL_REGISTRY
ROLES = ["qwen", "flux", "z_image", "fibo", "sdxl"]


def _print_models_table() -> None:
    """Print a table of the 5 available image_gen models."""
    print("\n  IMAGE_GEN MODELS (from MODEL_REGISTRY):")
    print("  " + "-" * 70)
    print(f"  {'role':<12s} {'key':<40s} {'alias':<25s} {'avail':<5s}")
    print("  " + "-" * 70)
    models_response = asyncio.run(list_image_models())
    for m in models_response.get("models", []):
        avail = "yes" if m.get("available", True) else "NO"
        print(f"  {m.get('role','?'):<12s} {m.get('key','?'):<40s} {m.get('litellm_alias','?'):<25s} {avail:<5s}")


async def _bench_single_prompt(prompt: str, role: str = None) -> dict:
    """Generate one asset and return the timing + result."""
    role = role or "default"
    t0 = time.monotonic()
    result = await generate_2d_asset(prompt=prompt, role=role)
    duration_ms = int((time.monotonic() - t0) * 1000)
    return {
        "prompt": prompt,
        "role": role,
        "duration_ms": duration_ms,
        "result": result,
    }


async def bench_one_prompt(prompt: str, role: str = None) -> dict:
    """Benchmark a single prompt across all 5 image_gen roles."""
    print(f"\n  PROMPT: {prompt!r}")
    if role:
        print(f"  ROLE: {role} (single role)")
        results = [await _bench_single_prompt(prompt, role)]
    else:
        print(f"  ROLES: cycling through {ROLES}")
        tasks = [_bench_single_prompt(prompt, r) for r in ROLES]
        results = await asyncio.gather(*tasks)

    ok = [r for r in results if r["result"].get("asset_id")]
    err = [r for r in results if r["result"].get("error")]
    stub = [r for r in results if r["result"].get("stub")]

    print(f"\n  RESULTS ({len(ok)}/{len(results)} OK, {len(stub)} stub, {len(err)} err):")
    print("  " + "-" * 70)
    print(f"  {'role':<12s} {'duration':<12s} {'asset_id':<40s} {'stub':<5s}")
    print("  " + "-" * 70)
    for r in results:
        dur = f"{r['duration_ms']}ms"
        asset_id = r["result"].get("asset_id", "ERR")
        is_stub = r["result"].get("stub", False)
        is_err = "error" in r["result"]
        status = "stub" if is_stub else ("err" if is_err else "ok")
        print(f"  {r['role']:<12s} {dur:<12s} {str(asset_id)[:38]:<40s} {status:<5s}")

    if stub:
        print(f"\n  ⚠ {len(stub)}/{len(results)} assets fell back to stub (litellm gateway unreachable)")
        print("    The assets are still queryable in lance://media.image_gen_chunks — they're just placeholder PNGs.")
    if err:
        print(f"\n  ✗ {len(err)}/{len(results)} assets errored:")
        for r in err:
            print(f"    - {r['role']}: {r['result'].get('error')}")

    return {"prompt": prompt, "results": results}


async def bench_pipeline(pipeline: str, query: str) -> dict:
    """Benchmark a full Pillar 3 pipeline (decompose → research → synthesise → render)."""
    print(f"\n  PIPELINE: {pipeline}")
    print(f"  QUERY: {query!r}")

    # Import the pipeline dynamically
    mod_name = f"agents.workflows.{pipeline}"
    try:
        mod = __import__(mod_name, fromlist=["run", "aistear_deep_research"])
    except ImportError as exc:
        print(f"  ✗ Could not import {mod_name}: {exc}")
        return {"error": str(exc)}

    # Build a synthetic briefing (in real use, the pipeline would generate it)
    synthetic_briefing = {
        "headline": f"Research on: {query}",
        "sections": [
            f"Section 1: {query} — first perspective",
            f"Section 2: {query} — second perspective",
            f"Section 3: {query} — third perspective",
        ],
    }

    # Derive prompts and call render_assets
    from agents.workflows._render_assets_node import render_assets, derive_asset_prompts
    prompts = derive_asset_prompts(synthetic_briefing, pipeline)
    print(f"  Derived {len(prompts)} prompts from the synthetic briefing")

    t0 = time.monotonic()
    tasks = [generate_2d_asset(prompt=p, role=ROLES[i % len(ROLES)]) for i, p in enumerate(prompts)]
    results = await asyncio.gather(*tasks)
    duration = int((time.monotonic() - t0) * 1000)

    ok = [r for r in results if r.get("asset_id")]
    stub = [r for r in results if r.get("stub")]

    print(f"\n  RENDERED {len(ok)}/{len(prompts)} assets in {duration}ms")
    print("  " + "-" * 70)
    for i, (prompt, result) in enumerate(zip(prompts, results)):
        role = ROLES[i % len(ROLES)]
        asset_id = str(result.get("asset_id", "ERR"))[:38]
        is_stub = result.get("stub", False)
        status = "stub" if is_stub else ("err" if "error" in result else "ok")
        print(f"  [{role:<10s}] {status:<5s} {asset_id:<40s} {prompt[:50]}")

    return {
        "pipeline": pipeline,
        "query": query,
        "prompts": prompts,
        "results": results,
        "duration_ms": duration,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("prompt", nargs="?", default="An Irish round tower at sunset",
                        help="The asset-generation prompt (or --pipeline for full Pillar 3)")
    parser.add_argument("--role", choices=ROLES, default=None,
                        help="If set, generate one variant for this role; otherwise cycle through all 5")
    parser.add_argument("--pipeline", choices=["aistear_deep_research", "primary_deep_research",
                                                "jc_deep_research", "sc_deep_research",
                                                "tertiary_deep_research"],
                        help="If set, run a full Pillar 3 pipeline instead of a single prompt")
    parser.add_argument("--query", default=None,
                        help="The query for the Pillar 3 pipeline (when --pipeline is set)")
    parser.add_argument("--list-models", action="store_true", help="Just list the 5 image_gen models and exit")
    args = parser.parse_args()

    print("=" * 70)
    print("  ASSET GENERATION BENCHMARK")
    print("  Plan 1 of the 2026-10 convergence saga")
    print("  openspec/plans/2026-10-01-convergence-saga-v1.md")
    print("=" * 70)

    _print_models_table()

    if args.list_models:
        return 0

    if args.pipeline:
        query = args.query or args.prompt
        result = asyncio.run(bench_pipeline(args.pipeline, query))
        return 0 if not result.get("error") else 1

    result = asyncio.run(bench_one_prompt(args.prompt, args.role))
    return 0


if __name__ == "__main__":
    sys.exit(main())
