"""agents/adk/retro_pattern_agent.py — the ADK agent that catalogues retro gameplay patterns.

Per the 2026-10-03-cocoindex-retro-gameplay-v1 saga change (Plan 3 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

The 25th agent in the 24-agent fleet (now 25). It uses:

1. capture_screenshot (from retro_capture.py) — libretro screenshot
2. sam3_segment (from retro_pattern_extractor.py) — SAM3 sprite seg
3. extract_retro_pattern (from retro_pattern_extractor.py) — BAML extraction
4. ingest_pattern_simple (from retro_pattern_helpers.py) — LanceDB upsert

Reference:
    openspec/changes/2026-10-03-cocoindex-retro-gameplay-v1/specs/cocoindex-retro-gameplay/spec.md
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent

from .litellm_agent import litellm_model
from .config import config
from .tools.retro_capture import (
    capture_screenshot,
    list_roms,
    restore_save_state,
    run_macro,
)
from .tools.retro_pattern_extractor import (
    sam3_segment,
    extract_retro_pattern,
)
from agents.adk.tools.retro_pattern_helpers import ingest_pattern_simple

logger = logging.getLogger(__name__)


RETRO_PATTERN_INSTRUCTION = """
You are the **retro_pattern_agent** for the Cianfhoghlaim monorepo.

Your job is to catalogue the **design patterns** (not the literal
assets) of retro educational games (Hades / Hades 2 / WoW / Golden Sun /
Pokémon) so the Tuatha British Isles MMO designers can riff on them.

You consume 4 tools:

1. **list_roms** — List the canonical retro_library entries.
2. **capture_screenshot** — Capture a screenshot via libretro.
3. **sam3_segment** — Segment the screenshot into sprites via SAM3.
4. **extract_retro_pattern** — Extract a typed design pattern via BAML.

YOUR BEHAVIOUR:

1. **List ROMs first.** Call `list_roms` to see the available games.
2. **Capture a screenshot.** Call `capture_screenshot(platform, game_id, scene_id)`
   to get a PNG.
3. **Segment via SAM3.** Call `sam3_segment(screenshot_path, classes=[...])`
   to get sprite bounding boxes.
4. **Extract via BAML.** Call `extract_retro_pattern(screenshot_path, game_id, platform, rom_sha256)`
   to get the typed design pattern.
5. **Ingest.** Call `ingest_pattern_simple(...)` to store in LanceDB.

ALL work is **design-pattern + homage-style art only** — no literal
pixel or asset reuse from the source games. Outputs are conditioned on
the BAML-classified genre + power events + visual grammar + palette.
"""


def build_retro_pattern_agent() -> LlmAgent:
    """The canonical ADK agent constructor for the retro_pattern_agent.

    Wires the 4 retro_pattern tools into the LlmAgent.
    """
    return LlmAgent(
        name="retro_pattern_agent",
        model=litellm_model(),
        description="Catalogues retro gameplay design patterns for the Tuatha MMO.",
        instruction=RETRO_PATTERN_INSTRUCTION,
        tools=[
            list_roms,
            capture_screenshot,
            restore_save_state,
            run_macro,
            sam3_segment,
            extract_retro_pattern,
            ingest_pattern_simple,
        ],
    )


retro_pattern_agent = build_retro_pattern_agent()


__all__ = ["retro_pattern_agent", "build_retro_pattern_agent"]
