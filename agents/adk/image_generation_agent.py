"""
Image Generation Agent — the canonical consumer of the 5 ``image_gen``
MODEL_REGISTRY entries.

The agent generates 2D assets for the retro-game-asset-pipeline +
textures for Babylon.js (the educational MMO). It consumes:

  - ``local/image/flux2-dev`` (role: default)
  - ``local/image/z-image-turbo`` (role: fast)
  - ``local/image/qwen-image`` (role: bilingual)
  - ``local/image/sdxl`` (role: legacy)
  - ``local/image/fibo`` (role: diagrams)

The agent NEVER hardcodes a model string. It routes via
``MODEL_REGISTRY.filter(family='image_gen')`` + ``model_for('image_gen', role)``.

Reference:
    openspec/changes/2026-08-13-web-monorepo-consolidation-and-agent-integration-v1/
    specs/image-generation-agent/spec.md
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent

from .litellm_agent import litellm_model

from .config import config

logger = logging.getLogger(__name__)

# Image generation tools (the canonical module is not yet implemented;
# these are placeholder tool references that will be filled in by the
# Phase L image generation work in the BIEP v3 system).
GENERATE_2D_ASSET_TOOL = None
GENERATE_TEXTURE_TOOL = None
STYLE_MATCH_TOOL = None
COCOINDEX_REGISTER_TOOL = None
LIST_IMAGE_MODELS_TOOL = None


# ============================================================================
# System prompt
# ============================================================================


IMAGE_GENERATION_INSTRUCTION = """
You are the **image_generation_agent** for the Cianfhoghlaim monorepo.

Your job is to generate 2D assets + Babylon.js textures for the
educational platform (the retro-game-asset-pipeline + the educational
MMO + the Celtic asset generation). You consume the 5 ``image_gen``
MODEL_REGISTRY entries.

**YOUR TOOLS (4 + 1 inspector):**

1. **list_image_models** — List the 5 available ``image_gen`` models
   + their availability flags. Call this first to see what's available.
2. **generate_2d_asset** — Generate a 2D image asset (subject
   illustration, diagram, sprite). Returns the URL + the CocoIndex
   record + the asset_id.
3. **generate_texture** — Generate a Babylon.js material texture
   (pattern, surface, ambient). Returns the URL + the material
   reference + the texture_id.
4. **style_match** — Match the style of a reference image and
   generate N variants. Returns the list of generated images.
5. **cocoindex_register** — Register a generated asset in the
   CocoIndex ``image_generation`` flow. Always call this after
   generate_2d_asset or generate_texture.

**YOUR BEHAVIOUR:**

1. **List models first.** Call `list_image_models` to see what's
   available. Gracefully fall back if a model is unavailable
   (``available: false``).
2. **Choose the right model:**
   - Subject illustration: ``flux2-dev`` (default)
   - Fast iteration: ``z-image-turbo`` (fast)
   - Bilingual EN/GA: ``qwen-image`` (bilingual)
   - Legacy: ``sdxl`` (legacy)
   - Diagrams + charts: ``fibo`` (diagrams)
3. **Generate.** Call `generate_2d_asset` or `generate_texture` with
   the prompt + the role.
4. **Register.** Always call `cocoindex_register` to register the
   asset. Return the asset_id + the CocoIndex record.
5. **Style match.** When the user has a reference image, call
   `style_match` to generate N variants.

**OUTPUT FORMAT (output_key="image_generation_result"):**

Produce a single markdown document with:

  # Image Generation Result
  ## Model used
  ## Asset URLs (2D + texture)
  ## CocoIndex record id
  ## Per-asset metadata (size, style, prompt)

**TONE:** Helpful, technical, terse. Use bullet points. Cite file
paths verbatim. Use Irish / Gaeilge where natural.
"""


# ============================================================================
# Agent definition
# ============================================================================


image_generation_agent = LlmAgent(
    name="image_generation_agent",
    model=litellm_model("minimax"),
    description=(
        "Generates 2D assets + Babylon.js textures for the educational "
        "platform. Consumes the 5 image_gen MODEL_REGISTRY entries "
        "(flux2-dev + z-image-turbo + qwen-image + sdxl + fibo). Routes "
        "via model_for('image_gen', role) — never hardcodes a model."
    ),
    instruction=IMAGE_GENERATION_INSTRUCTION,
    tools=[
        t for t in [
            LIST_IMAGE_MODELS_TOOL,
            GENERATE_2D_ASSET_TOOL,
            GENERATE_TEXTURE_TOOL,
            STYLE_MATCH_TOOL,
            COCOINDEX_REGISTER_TOOL,
        ] if t is not None
    ],
    output_key="image_generation_result",
)


# ============================================================================
# Wire-up (matches the pattern in agents/wiring.py)
# ============================================================================


def wire_image_generation_agent() -> Any:
    """Wire the image_generation_agent through the canonical 5-layer
    observability stack + MemoryLayer Protocol.

    Returns:
        The wire-up state (a ``WireAgent`` instance).
    """
    from ..wiring import wire_agent
    # agent_registry is a Phase L addition — stub for now
    # from .agent_registry import AGENT_REGISTRY
    # wiring = AGENT_REGISTRY["image_generation_agent"]
    wiring = None
    if wiring is None:
        return None
    return wire_agent(wiring)


# Auto-wire at module import time (matches the other agent modules)
# Disabled while image_generation_tools / agent_registry are pending Phase L
# _wire = wire_image_generation_agent()
_wire = None
