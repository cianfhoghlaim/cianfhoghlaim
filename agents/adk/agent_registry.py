"""agent_registry — the canonical ADK agent registry (4 stage + 12 baseline).

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change +
the 2026-11-25-mega-3c-marimo-and-integration-v1 change.

Note: This module provides the 4 stage agents as the canonical surface
(Mega-3a). The 12 baseline agents at agents/adk/*.py have various
exposure patterns (some expose `agent`, some expose `root_agent`,
some don't expose at all). The full 16-agent registry lands in a
follow-up commit that aligns the baseline agent exposure patterns.

For now, the registry exposes the 4 stage agents (the canonical
Mega-3a output) + the agents that DO expose themselves cleanly.

Usage:

    from agents.adk.agent_registry import AGENT_REGISTRY
    print(list(AGENT_REGISTRY.keys()))  # 4+ agents

    # In the agent_ui_bridge.py:
    from agents.adk.agent_registry import AGENT_REGISTRY
    for name, wiring in AGENT_REGISTRY.items():
        register_adk_agent(wiring.agent, name=name)
"""
from __future__ import annotations

from typing import NamedTuple


class AgentWiring(NamedTuple):
    """The wiring metadata for a single ADK agent."""

    name: str
    agent: object  # The LlmAgent instance
    description: str
    stage: str | None  # "lc" | "jc" | "alevel" | "gcse" | None
    tools: list[object]  # The BAMLFunctionTool-wrapped tools


def _build_registry() -> dict[str, AgentWiring]:
    """Build the canonical 4 stage-agent registry (the Mega-3a output).

    The 12 baseline agents will be added once the exposure patterns are
    unified (separate follow-up commit).
    """
    from .lc_subject_agent import lc_subject_agent, LC_SUBJECT_TOOLS
    from .jc_subject_agent import jc_subject_agent, JC_SUBJECT_TOOLS
    from .alevel_subject_agent import alevel_subject_agent, ALEVEL_FUNCTIONS
    from .gcse_subject_agent import gcse_subject_agent, GCSE_FUNCTIONS

    from agents.integrations.baml_function_tool import BAMLFunctionTool

    return {
        # 4 stage agents (per the 4-stage plane architecture)
        "lc_subject_agent": AgentWiring(
            name="lc_subject_agent",
            agent=lc_subject_agent,
            description="Expert on Irish Leaving Certificate (LC) subjects (14 subjects).",
            stage="lc",
            tools=LC_SUBJECT_TOOLS,
        ),
        "jc_subject_agent": AgentWiring(
            name="jc_subject_agent",
            agent=jc_subject_agent,
            description="Expert on Irish Junior Cycle (JC) subjects (8 NCCA JC subjects at full scope).",
            stage="jc",
            tools=JC_SUBJECT_TOOLS,
        ),
        "alevel_subject_agent": AgentWiring(
            name="alevel_subject_agent",
            agent=alevel_subject_agent,
            description="Expert on England A-Level subjects (15 × 3 boards).",
            stage="alevel",
            tools=[BAMLFunctionTool(fn) for fn in ALEVEL_FUNCTIONS],
        ),
        "gcse_subject_agent": AgentWiring(
            name="gcse_subject_agent",
            agent=gcse_subject_agent,
            description="Expert on England GCSE subjects (9 × 3 boards).",
            stage="gcse",
            tools=[BAMLFunctionTool(fn) for fn in GCSE_FUNCTIONS],
        ),
    }


AGENT_REGISTRY: dict[str, AgentWiring] = _build_registry()


__all__ = [
    "AgentWiring",
    "AGENT_REGISTRY",
]