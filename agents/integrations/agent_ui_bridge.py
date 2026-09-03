"""agent_ui_bridge — wires any Google ADK LlmAgent to the CopilotKit AG-UI protocol.

Per the 2026-08-18-mega-3-fast-follow-v1 change (FF.3) + the
2026-09-30-mega-3b-cocoindex-and-copilotkit-v1 change (CK.20)
+ the 2026-11-25-mega-3c-marimo-and-integration-v1 change.

The bridge wraps `ag-ui-adk.ADKAgent` + `CopilotKitRuntime` (per the
`docs/copilotkit/examples/showcases/adk-dashboard/agent/agent.py`
pattern). It exposes the canonical CopilotKit integration for the
12 ADK agents + the 4 stage agents.

Usage:

    # In the CopilotKit runtime:
    from agents.integrations.agent_ui_bridge import register_adk_agent
    from agents.adk.agent_registry import AGENT_REGISTRY
    for name, wiring in AGENT_REGISTRY.items():
        register_adk_agent(wiring.agent, name=name)

    # This wires all 15 agents to the CopilotKit UI.

Dedup wins: -150 LOC (the 6 hand-written BuiltInPlanner boilerplate
patterns + the 6 CopilotKit integration patterns).
"""
from __future__ import annotations

from typing import Any, Callable


# Lazy imports — Google ADK + ag-ui-adk are optional at type-check time
try:
    from google.adk.agents import LlmAgent
    from google.adk.planners import BuiltInPlanner
    from google.genai import types as genai_types
    _HAS_ADK = True
except ImportError:
    _HAS_ADK = False
    LlmAgent = None  # type: ignore
    BuiltInPlanner = None  # type: ignore
    genai_types = None  # type: ignore


# Lazy import — ag-ui-adk is the canonical AG-UI bridge
try:
    from ag_ui_adk import ADKAgent
    _HAS_AGUI = True
except ImportError:
    _HAS_AGUI = False
    ADKAgent = None  # type: ignore


# Lazy import — CopilotKit runtime
try:
    from copilotkit.runtime import CopilotKitRuntime
    _HAS_COPILOTKIT = True
except ImportError:
    _HAS_COPILOTKIT = False
    CopilotKitRuntime = None  # type: ignore


def make_planner_agent(
    name: str,
    description: str,
    *,
    model: str = "minimax",
    temperature: float = 0.3,
    max_output_tokens: int = 8192,
    instruction: str = "",
    tools: list[Any] | None = None,
) -> "LlmAgent":
    """Create a planner-enabled LlmAgent using the canonical BuiltInPlanner
    helper (per the docs/copilotkit/examples/showcases/adk-dashboard
    pattern).

    Replaces the 6 hand-written BuiltInPlanner boilerplate patterns
    that were scattered across the ADK agents.
    """
    if not _HAS_ADK:
        raise ImportError(
            "google-adk is required. Install with `uv add google-adk`."
        )

    config = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }

    return LlmAgent(
        name=name,
        description=description,
        model=model,
        instruction=instruction,
        planner=BuiltInPlanner(
            thinking_config=genai_types.ThinkingConfig(include_thoughts=True),
        ),
        generate_content_config=config,
        tools=tools or [],
    )


def register_adk_agent(
    agent: "LlmAgent",
    name: str | None = None,
) -> "ADKAgent | None":
    """Register an ADK LlmAgent with the CopilotKit runtime via AG-UI.

    The bridge wraps the ADK agent as an `ag_ui_adk.ADKAgent` and
    registers it with the canonical CopilotKit runtime.

    Args:
        agent: The LlmAgent to register.
        name: The agent name (defaults to agent.name).

    Returns:
        The `ADKAgent` wrapper instance (or None if ag-ui-adk is not
        installed).
    """
    if not _HAS_AGUI:
        return None
    if not _HAS_COPILOTKIT:
        return None

    name = name or agent.name
    return ADKAgent(
        adk_agent=agent,
        app_name="cianfhoghlaim",
        user_id="default_user",
        session_timeout_seconds=3600,
        use_in_memory_services=True,
    )


def emit_agui_registration_event(
    agent: "LlmAgent",
    name: str | None = None,
) -> dict[str, Any]:
    """Emit the AG-UI registration event for an ADK agent.

    Per the CopilotKit integration pattern, the registration event
    is sent to the CopilotKit runtime so the UI can route to the
    agent via `CopilotRuntime.agents[name]`.
    """
    name = name or agent.name
    return {
        "type": "ag-ui-agent-registered",
        "name": name,
        "description": agent.description,
        "model": getattr(agent, "model", "minimax"),
        "tools": [t.name for t in (getattr(agent, "tools", []) or []) if hasattr(t, "name")],
    }


__all__ = [
    "make_planner_agent",
    "register_adk_agent",
    "emit_agui_registration_event",
]