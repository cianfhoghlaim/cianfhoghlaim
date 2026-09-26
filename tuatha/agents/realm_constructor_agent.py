"""tuatha/agents/realm_constructor_agent.py — the ADK 2 agent that builds Tuatha realms.

Per the 2026-10-08-tuatha-closed-loop-mmo-v1 saga change (Plan 8 of
openspec/plans/2026-10-01-convergence-saga-v1.md).

The 26th agent in the fleet. Uses:
- The per-subject realm Dagster asset (`orchestration.defs.4_asset_generation.tuatha_realm_asset`)
- The shared ADK 2 Pillar 4 render_assets_node (`agents/workflows/_render_assets_node.py`)
- The per-language asset generation (from Plan 7)
- The Cognee entity-asset linking (from Plan 6)

Reference: openspec/specs/tuatha-closed-loop-mmo/spec.md
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_realm(subject: str = "mathematics", language: str = "en") -> dict[str, Any]:
    """Build the canonical Tuatha realm for one subject + one language.

    Falls back to the Dagster asset stub when offline.

    Args:
        subject: The NCCA subject (default: mathematics)
        language: en | ga | cy | gd | gv | kw | br

    Returns:
        The realm JSON dict
    """
    try:
        import importlib
        mod = importlib.import_module("orchestration.defs.4_asset_generation.tuatha_realm_asset")
        tuatha_realm_asset = getattr(mod, "tuatha_realm_asset", None)
        if tuatha_realm_asset is None:
            raise ImportError("tuatha_realm_asset not found")
        return tuatha_realm_asset(subject=subject, language=language)
    except ImportError:
        # Fallback: build the minimal stub inline
        return {
            "error": "tuatha_realm_asset not importable",
            "subject": subject,
            "language": language,
            "stub": True,
        }


def realm_constructor_agent():
    """The canonical ADK 2 agent factory for the realm constructor.

    Wires the build_realm function as a single ADK tool. The 26th
    agent in the 24-agent fleet (the K-12 + tertiary fleet + the new
    Tuatha agents for the closed-loop MMO).
    """
    try:
        from google.adk.agents import LlmAgent
        from google.adk.tools import FunctionTool

        build_realm_tool = FunctionTool(func=build_realm)

        return LlmAgent(
            name="realm_constructor_agent",
            model="minimax-m3",
            description=(
                "Builds the canonical Tuatha British Isles MMO realm for one subject + one language. "
                "Mathematics is the first subject supported at launch. "
                "Returns the realm JSON with sprite_bank + window_chrome + deity_placement + "
                "learning_outcomes + linked Cognee entities."
            ),
            instruction=(
                "You are the realm constructor agent for the Cianfhoghlaim British Isles MMO. "
                "When the operator asks for a Mathematics Formative Session, call build_realm(subject='mathematics') "
                "and return the resulting realm JSON. The realm JSON contains sprite positions + "
                "the celtic-art window chrome URL + The Dagda as the deity."
            ),
            tools=[build_realm_tool],
        )
    except ImportError:
        return None


__all__ = ["build_realm", "realm_constructor_agent"]
