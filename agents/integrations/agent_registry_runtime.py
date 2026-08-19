"""agent_registry_runtime — the canonical runtime for wiring the 15-agent
fleet to the CopilotKit runtime + AG-UI protocol.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change (Phase 5).

The runtime module exposes the 3 canonical helpers that the
CopilotKit runtime uses to:

1. Register every agent in `AGENT_REGISTRY` with the CopilotKit runtime
   via `register_adk_agent(agent, name=name)`.
2. Collect every `emit_agui_registration_event(agent)` for the
   AG-UI protocol's registration handshake.
3. Build the canonical CopilotKit runtime configuration (agents +
   tools + metadata).

All 3 helpers are no-ops when the optional dependencies (ag-ui-adk,
copilotkit, google-adk) are not installed.

Usage:

    # In the canonical CopilotKit runtime:
    from agents.integrations.agent_registry_runtime import (
        register_all_agents_with_copilotkit,
        collect_all_agui_events,
        build_copilotkit_runtime_config,
    )

    registered = register_all_agents_with_copilotkit()
    events = collect_all_agui_events()
    config = build_copilotkit_runtime_config()
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


# Lazy imports — Google ADK + ag-ui-adk are optional at type-check time
try:
    from google.adk.agents import LlmAgent  # noqa: F401
    _HAS_ADK = True
except ImportError:
    _HAS_ADK = False
    LlmAgent = None  # type: ignore

try:
    from ag_ui_adk import ADKAgent  # noqa: F401
    _HAS_AGUI = True
except ImportError:
    _HAS_AGUI = False
    ADKAgent = None  # type: ignore

try:
    from copilotkit.runtime import CopilotKitRuntime  # noqa: F401
    _HAS_COPILOTKIT = True
except ImportError:
    _HAS_COPILOTKIT = False
    CopilotKitRuntime = None  # type: ignore


def _load_agent_registry() -> dict[str, Any] | None:
    """Try to load the AGENT_REGISTRY. Returns None on any failure.

    The lazy load pattern is necessary because the agents.adk package
    has various pre-existing import issues (per the test_4_stage_plane
    pattern).
    """
    try:
        from agents.adk.agent_registry import AGENT_REGISTRY
        return AGENT_REGISTRY
    except ImportError:
        return None
    except Exception as e:
        logger.debug("agent_registry_runtime: failed to load AGENT_REGISTRY: %s", e)
        return None


def register_all_agents_with_copilotkit() -> dict[str, Any]:
    """Register every agent in AGENT_REGISTRY with the CopilotKit runtime.

    Iterates over `AGENT_REGISTRY` and calls
    `register_adk_agent(agent, name=name)` for each agent.

    Returns:
        A dict mapping agent name → ADKAgent wrapper (or None if the
        agent could not be registered, e.g., because ag-ui-adk is
        not installed).

    The function is a no-op when ag-ui-adk or CopilotKit is not
    installed — it returns an empty dict.
    """
    if not _HAS_AGUI or not _HAS_COPILOTKIT:
        logger.debug(
            "agent_registry_runtime: skipping register_all_agents — "
            "ag-ui-adk or copilotkit not installed."
        )
        return {}

    try:
        from agents.integrations.agent_ui_bridge import register_adk_agent
    except ImportError:
        logger.debug("agent_registry_runtime: agent_ui_bridge not importable")
        return {}

    registry = _load_agent_registry()
    if not registry:
        logger.debug("agent_registry_runtime: AGENT_REGISTRY is empty or unavailable")
        return {}

    registered: dict[str, Any] = {}
    for name, wiring in registry.items():
        agent = getattr(wiring, "agent", None)
        if agent is None:
            continue
        try:
            wrapper = register_adk_agent(agent, name=name)
            registered[name] = wrapper
        except Exception as e:
            logger.debug(
                "agent_registry_runtime: failed to register %s: %s",
                name, e,
            )
            registered[name] = None
    return registered


def collect_all_agui_events() -> list[dict[str, Any]]:
    """Collect the AG-UI registration event for every agent in AGENT_REGISTRY.

    For each agent, calls `emit_agui_registration_event(agent)` and
    appends the resulting dict to the returned list.

    Returns:
        A list of event dicts, one per registered agent. Each event
        has the keys: type, name, description, model, tools.
    """
    try:
        from agents.integrations.agent_ui_bridge import emit_agui_registration_event
    except ImportError:
        return []

    registry = _load_agent_registry()
    if not registry:
        return []

    events: list[dict[str, Any]] = []
    for name, wiring in registry.items():
        agent = getattr(wiring, "agent", None)
        if agent is None:
            continue
        try:
            event = emit_agui_registration_event(agent, name=name)
            events.append(event)
        except Exception as e:
            logger.debug(
                "agent_registry_runtime: failed to emit event for %s: %s",
                name, e,
            )
    return events


def build_copilotkit_runtime_config() -> dict[str, Any]:
    """Build the canonical CopilotKit runtime configuration.

    The configuration includes:
    - agents: the list of AG-UI registration events
    - tools: the list of registered BAMLFunctionTool-wrapped tools
    - metadata: the runtime metadata (version, deployment, etc.)

    Returns:
        A dict suitable for passing to CopilotKitRuntime(**config).

    The function is a no-op when AGENT_REGISTRY is unavailable — it
    returns a minimal config with an empty agents list.
    """
    events = collect_all_agui_events()
    registry = _load_agent_registry()

    # Collect all unique tools across the agents
    all_tools: list[Any] = []
    if registry:
        for wiring in registry.values():
            for tool in getattr(wiring, "tools", []) or []:
                all_tools.append(tool)

    # Build the metadata
    metadata = {
        "runtime": "agent_registry_runtime",
        "agent_count": len(events),
        "tool_count": len(all_tools),
        "has_agui": _HAS_AGUI,
        "has_copilotkit": _HAS_COPILOTKIT,
        "has_adk": _HAS_ADK,
        "deployment": "cianfhoghlaim",
    }

    return {
        "agents": events,
        "tools": all_tools,
        "metadata": metadata,
    }


__all__ = [
    "register_all_agents_with_copilotkit",
    "collect_all_agui_events",
    "build_copilotkit_runtime_config",
]
