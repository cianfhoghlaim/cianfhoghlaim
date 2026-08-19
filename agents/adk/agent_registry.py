"""agent_registry — the canonical ADK agent registry (4 stage + 11 baseline).

Per the 2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change +
the 2026-11-25-mega-3c-marimo-and-integration-v1 change.

Provides the canonical registry of the 4 stage agents (the Mega-3a
output) + 11 baseline agents (the original 12 agents at
`agents/adk/*.py` minus `image_generation_agent` which has known
import issues with `agents.adk.image_generation_tools`).

Usage:

    from agents.adk.agent_registry import AGENT_REGISTRY
    print(list(AGENT_REGISTRY.keys()))  # 15 agents

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


def _try_import(name: str, module_path: str, attr: str) -> object | None:
    """Try to import a baseline agent. Returns None on failure."""
    try:
        module = __import__(module_path, fromlist=[attr])
        return getattr(module, attr, None)
    except Exception:
        return None


def _build_registry() -> dict[str, AgentWiring]:
    """Build the canonical 15-agent registry (4 stage + 11 baseline).

    The 4 stage agents are the canonical Mega-3a output. The 11 baseline
    agents are the original agents.adk/*.py that have consistent
    `<name> = LlmAgent(...)` export patterns.

    `image_generation_agent` is excluded (the original file has known
    import issues with `agents.adk.image_generation_tools`; it lands
    in a separate follow-up).
    """
    from .lc_subject_agent import lc_subject_agent, LC_SUBJECT_TOOLS
    from .jc_subject_agent import jc_subject_agent, JC_SUBJECT_TOOLS
    from .alevel_subject_agent import alevel_subject_agent, ALEVEL_FUNCTIONS
    from .gcse_subject_agent import gcse_subject_agent, GCSE_FUNCTIONS

    from agents.integrations.baml_function_tool import BAMLFunctionTool

    registry: dict[str, AgentWiring] = {
        # === 4 stage agents (per the 4-stage plane architecture) ===
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

    # === 11 baseline agents (lazy-imported with try/except for resilience) ===

    baseline_agents = [
        (
            "agui_curriculum_agent",
            "agents.adk.agui_curriculum_agent",
            "agui_curriculum_agent",
            "Curriculum agent exposed via the AG-UI Protocol.",
        ),
        (
            "celtic_tutor_agent",
            "agents.adk.celtic_tutor_agent",
            "celtic_tutor_agent",
            "Celtic language tutor agent (6 Celtic languages).",
        ),
        (
            "curriculum_comparison_agent",
            "agents.adk.curriculum_comparison_agent",
            "curriculum_comparison_agent",
            "Cross-nation curriculum mapping (IE ↔ EN ↔ SCT).",
        ),
        (
            "education_research_agent",
            "agents.adk.education_research_agent",
            "education_research_agent",
            "Cross-nation education policy research.",
        ),
        (
            "email_triage_agent",
            "agents.adk.email_triage_agent",
            "email_triage_agent",
            "Email triage (4 accounts: DKIT + 2 Gmail + Hotmail).",
        ),
        (
            "geospatial_agent",
            "agents.adk.geospatial_agent",
            "geospatial_agent",
            "LSOA / Data Zone spatial analysis.",
        ),
        (
            "mythology_narrator_agent",
            "agents.adk.mythology_narrator_agent",
            "mythology_narrator_agent",
            "Celtic mythology narrator.",
        ),
        (
            "quest_guide_agent",
            "agents.adk.quest_guide_agent",
            "quest_guide_agent",
            "Túatha quest guide for the 8 NCCA LC subjects.",
        ),
        (
            "research_agent",
            "agents.adk.research_agent",
            "research_agent",
            "Deep research with citations (Celtic focus).",
        ),
        (
            "research_assistant_agent",
            "agents.adk.research_assistant_agent",
            "research_assistant_agent",
            "Research assistant with citation tracking.",
        ),
        (
            "statistics_agent",
            "agents.adk.statistics_agent",
            "statistics_agent",
            "Education metrics + benchmarking.",
        ),
    ]

    for name, module_path, attr, description in baseline_agents:
        agent = _try_import(name, module_path, attr)
        if agent is not None:
            registry[name] = AgentWiring(
                name=name,
                agent=agent,
                description=description,
                stage=None,
                tools=[],
            )

    return registry


AGENT_REGISTRY: dict[str, AgentWiring] = _build_registry()


__all__ = [
    "AgentWiring",
    "AGENT_REGISTRY",
]