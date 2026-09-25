"""agents/workflows/_render_assets_node.py — the shared render_assets_node for all 5 Pillar 3 deep-research pipelines.

Per the 2026-10-02-adk-asset-generation-pillar3-v1 saga change
(Plan 1 of openspec/plans/2026-10-01-convergence-saga-v1.md).

Each Pillar 3 pipeline (aistear + primary + jc + sc + tertiary) gains a
new ``render_assets_node`` after the ``synthesize`` node. The node:

1. Takes the briefing (DeepResearchBriefing) as input
2. Generates N visual assets via the 5 ``image_gen`` MODEL_REGISTRY entries
   (flux2-dev + z-image-turbo + qwen-image + sdxl + fibo)
3. Routes through the LiteLLM gateway (per ``agents/adk/tools/image_generation.py``)
4. Returns the asset URLs + LanceDB record IDs as the final pipeline output
5. Gracefully degrades to placeholder PNGs when the LiteLLM gateway is unreachable

Used by:
- aistear_deep_research.py
- primary_deep_research.py
- jc_deep_research.py
- sc_deep_research.py
- tertiary_deep_research.py

NOT used by:
- student_secondary_workflow.py (Pillar 1, not Pillar 3)
- teacher_daily_workflow.py (Pillar 1, not Pillar 3)
- tertiary_personal_workflow.py (Pillar 1, not Pillar 3)
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from google.adk import Event
from google.adk.workflow import node

from agents.adk.tools.image_generation import (
    generate_2d_asset,
    generate_texture,
)

logger = logging.getLogger(__name__)


# The 5 image_gen roles from MODEL_REGISTRY
DEFAULT_ROLES = ["qwen", "flux", "z_image", "fibo", "sdxl"]


def derive_asset_prompts(briefing: dict[str, Any], pipeline: str) -> list[str]:
    """Derive N visual asset prompts from the deep-research briefing.

    Strategy:
    - 1 prompt per section in the briefing (max 7)
    - Plus 1 cover prompt summarising the headline
    - Plus 1 thematic diagram prompt
    """
    headline = briefing.get("headline", "")
    sections = briefing.get("sections", []) or []

    prompts: list[str] = []
    if headline:
        prompts.append(f"Cover illustration for: {headline}")

    for i, section in enumerate(sections[:7], 1):
        prompts.append(f"Section {i} illustration: {section[:200]}")

    if len(sections) >= 2:
        prompts.append(
            f"Thematic diagram connecting: {', '.join(s[:60] for s in sections[:3])}"
        )

    return prompts


@node(rerun_on_resume=True)
async def render_assets(ctx, node_input: Any) -> Any:
    """The shared render_assets_node for all 5 Pillar 3 pipelines.

    Takes the briefing as node_input (a dict with ``briefing`` key from
    the synthesize node), derives N visual asset prompts, and generates
    them in parallel via the LiteLLM gateway.

    Returns:
        Dict with:
          - ``assets``: list of asset records (one per generated image)
          - ``count``: int (number of assets generated)
          - ``pipeline``: str (the pipeline name)
          - ``pipeline_headline``: str (echo of the briefing headline)
          - ``rendered_at``: str (ISO 8601 timestamp)
    """
    # Extract the briefing from the input (it's the synthesize node's output)
    if isinstance(node_input, dict) and "briefing" in node_input:
        briefing = node_input["briefing"]
        pipeline_name = node_input.get("pipeline", "unknown")
    elif isinstance(node_input, dict):
        briefing = node_input
        pipeline_name = "unknown"
    else:
        briefing = {}
        pipeline_name = "unknown"

    headline = briefing.get("headline", "deep research output")
    prompts = derive_asset_prompts(briefing, pipeline_name)

    logger.info(
        "render_assets_node: %d prompts for pipeline=%s headline=%r",
        len(prompts),
        pipeline_name,
        headline[:80],
    )

    # Generate assets in parallel (one per role, cycling through the 5)
    tasks = []
    for i, prompt in enumerate(prompts):
        role = DEFAULT_ROLES[i % len(DEFAULT_ROLES)]
        tasks.append(generate_2d_asset(prompt=prompt, role=role))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    assets = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning("asset %d failed: %s", i, result)
            continue
        if isinstance(result, dict) and result.get("asset_id"):
            assets.append(
                {
                    "asset_id": result["asset_id"],
                    "url": result.get("url"),
                    "model": result.get("model"),
                    "role": result.get("role"),
                    "prompt": prompts[i],
                    "file_path": result.get("file_path"),
                    "sha256": result.get("sha256"),
                    "stub": result.get("stub", False),
                }
            )

    return {
        "assets": assets,
        "count": len(assets),
        "pipeline": pipeline_name,
        "pipeline_headline": headline,
        "rendered_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
    }


__all__ = ["render_assets", "render_assets_node", "derive_asset_prompts"]
