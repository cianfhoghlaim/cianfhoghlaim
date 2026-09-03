"""Agent fleet wiring layer.

Production-ises the 12-agent fleet wiring (root + 8 ADK + 3 Agno)
mirroring the `agents/tuatha/wiring.py:SubjectAgentWiring` pattern.

Each of the 12 main agents gets:

- A **MemoryLayer Protocol** binding via
  ``get_default_memory_layer()`` from ``agents.memory_layer`` (no
  direct Graphiti / FalkorDB / Memgraph imports anywhere in this file).
- A **5-layer observability stack** wired via
  ``attach_observability()`` from ``agents.observability_hooks``
  (Langfuse + Logfire + MLflow + RAGAS + structlog).
- A **Pydantic v2 base model** from ``agents.pydantic_models``
  (consistent request/response/context/trace schemas).
- A **graceful degradation** pattern via ``agents.exceptions``
  (``with_retry`` + ``graceful_degradation``).
- A **canonical agent registry** entry in
  ``agents.agent_registry.AGENT_REGISTRY`` — the single source of
  truth for the 12 main agents.

Every wire-up is graceful — when a runtime dependency is missing
the agent still imports + constructs (back-compat with the 20
existing smoke tests in ``tests/test_subject_router_smoke.py``),
but the lifecycle tests in ``tests/test_agent_fleet_smoke.py``
verify that with real dependencies the wiring is live.

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .pydantic_models import AgentRequest, AgentResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Framework enum: the 5 frameworks supported by the agent fleet.
# ---------------------------------------------------------------------------


class AgentFramework(str, Enum):
    """The 5 frameworks supported by the Cianfhoghlaim agent fleet."""

    CUSTOM = "Custom"
    ADK = "ADK"
    AGNO = "Agno"
    PIPECAT = "Pipecat"
    COPILOTKIT = "CopilotKit"


# ---------------------------------------------------------------------------
# AgentFleetWiring: the per-agent wire-up metadata.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AgentFleetWiring:
    """Per-agent wiring constants for one of the 12 main agents.

    The 12 instances are constructed once at import time and shared
    across the 12 ``<slug>_agent.py`` modules via
    ``AGENT_REGISTRY[agent_name]``.
    """

    # Canonical agent name (``agent_registry.AGENT_REGISTRY`` key).
    agent_name: str
    # File-name slug for the module + the L5 component mount.
    module_slug: str
    # Module path (e.g. ``cianfhoghlaim.agents.adk.curriculum_agent``).
    module_path: str
    # Framework tuple (one of the 5).
    framework: AgentFramework
    # Pretty display name.
    display_name: str
    # BAML function-name prefix (``<prefix>.baml`` exports).
    baml_prefix: str
    # Pretty ``trace_name`` template (``agent.<slug>.<verb>``).
    langfuse_trace_name: str
    # Canonical Cognee dataset name.
    cognee_dataset: str
    # Canonical Letta agent_id.
    letta_agent_id: str
    # LiteLLM routing key (model selection).
    litellm_routing_key: str

    @property
    def is_pipecat(self) -> bool:
        return self.framework == AgentFramework.PIPECAT

    @property
    def is_copilotkit(self) -> bool:
        return self.framework == AgentFramework.COPILOTKIT

    @property
    def is_custom(self) -> bool:
        return self.framework == AgentFramework.CUSTOM

    @property
    def is_adk(self) -> bool:
        return self.framework == AgentFramework.ADK

    @property
    def is_agno(self) -> bool:
        return self.framework == AgentFramework.AGNO


# ---------------------------------------------------------------------------
# WireAgent: the per-agent wire-up state attached to each agent module.
# ---------------------------------------------------------------------------


@dataclass
class WireAgent:
    """Per-agent wire-up state attached to every main agent.

    This is *not* an LlmAgent subclass — it is a separate object
    exposed as ``<slug>_agent.wire`` so the smoke tests can verify
    the wiring without poking private attributes on the LlmAgent.
    """

    agent: AgentFleetWiring
    # Whether the 5-layer observability stack was wired (False means
    # at least one of Langfuse / Logfire / MLflow / RAGAS / structlog
    # was not importable at construction time).
    observability_wired: bool = False
    # Whether the MemoryLayer Protocol binding was wired.
    memory_layer_wired: bool = False
    # The kind of memory layer that was resolved.
    memory_layer_kind: str | None = None
    # Whether the Pydantic v2 base models were wired.
    pydantic_models_wired: bool = False
    # Whether the BAML function-name lookup was bound.
    baml_prefix: str | None = None
    # Per-observability-layer flags (5 layers).
    langfuse_wired: bool = False
    logfire_wired: bool = False
    mlflow_wired: bool = False
    ragas_scorer_wired: bool = False
    structlog_wired: bool = False


# ---------------------------------------------------------------------------
# Eager wire-up: called once per agent at module load time.
# Returns a ``WireAgent`` whose fields report which dependencies
# were successfully wired against the current Python environment.
# ---------------------------------------------------------------------------


def wire_agent(wiring: AgentFleetWiring) -> WireAgent:
    """Construct the wire-up state for one of the 12 main agents.

    Called once at the bottom of each ``<slug>_agent.py`` after the
    ``LlmAgent`` is built.  Returns a :class:`WireAgent` whose fields
    report which dependencies were successfully wired against the
    current Python environment.

    This function never raises — it logs warnings when a dependency
    is missing, then returns a wire with the corresponding
    ``*_wired=False`` flag.
    """
    wire = WireAgent(
        agent=wiring,
        baml_prefix=wiring.baml_prefix,
    )

    # MemoryLayer Protocol — always importable (no external dep).
    try:
        from .memory_layer import (
            MemoryLayer,
            get_default_memory_layer,
        )

        wire.memory_layer_wired = True
        try:
            layer = get_default_memory_layer()
            wire.memory_layer_kind = layer.kind
        except Exception as exc:  # noqa: BLE001
            logger.debug(
                "wire_agent(%s): memory_layer factory fallback: %s",
                wiring.agent_name,
                exc,
            )
            wire.memory_layer_kind = "pending"
        del MemoryLayer, get_default_memory_layer  # noqa: F841
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "wire_agent(%s): MemoryLayer probe failed: %s",
            wiring.agent_name,
            exc,
        )
        wire.memory_layer_wired = False

    # Observability hooks — try the canonical 5-layer wiring.
    try:
        from .observability_hooks import (
            attach_observability,
        )

        attach_observability(wire)
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "wire_agent(%s): observability_hooks probe failed: %s",
            wiring.agent_name,
            exc,
        )
        wire.observability_wired = False

    # Pydantic v2 base models — try the canonical import.
    try:
        from .pydantic_models import (  # noqa: F401
            AgentRequest,
            AgentResponse,
            AgentContext,
            AgentTrace,
        )

        wire.pydantic_models_wired = True
    except Exception as exc:  # noqa: BLE001
        logger.debug(
            "wire_agent(%s): pydantic_models import failed: %s",
            wiring.agent_name,
            exc,
        )
        wire.pydantic_models_wired = False

    return wire


# ---------------------------------------------------------------------------
# Convenience helpers exposed for the 12 agents + tests.
# ---------------------------------------------------------------------------


def get_wiring(agent_name: str) -> AgentFleetWiring:
    """Return the :class:`AgentFleetWiring` for an agent name.

    Raises ``KeyError`` if the agent is unknown — but the canonical
    list is in ``agent_registry.AGENT_REGISTRY``.
    """
    from .agent_registry import AGENT_REGISTRY

    try:
        return AGENT_REGISTRY[agent_name]
    except KeyError as exc:
        raise KeyError(
            f"No wiring for agent {agent_name!r}. "
            f"Known: {sorted(AGENT_REGISTRY)}."
        ) from exc


def wiring_for_module_slug(module_slug: str) -> AgentFleetWiring | None:
    """Return the wiring for a module slug, or None if not found."""
    from .agent_registry import AGENT_REGISTRY

    for wiring in AGENT_REGISTRY.values():
        if wiring.module_slug == module_slug:
            return wiring
    return None


# ---------------------------------------------------------------------------
# Env-var override: CI hermetic mode.
# If CI sets ``AGENT_FLEET_DISABLE_WIRE=1`` then ``wire_agent``
# returns a no-op wire immediately.  Useful for hermetic CI runs
# where a missing Letta / Cognee / Langfuse should be a clean
# no-op.
# ---------------------------------------------------------------------------


def _env_disable_wire() -> bool:
    val = os.getenv("AGENT_FLEET_DISABLE_WIRE", "")
    return val.lower() in {"1", "true", "yes", "on"}


if _env_disable_wire():
    logger.warning(
        "AGENT_FLEET_DISABLE_WIRE=1 — all wire_agent calls "
        "will return a no-op wire"
    )

    def wire_agent(wiring: AgentFleetWiring) -> WireAgent:  # type: ignore[no-redef]  # noqa: F811
        return WireAgent(
            agent=wiring,
            baml_prefix=wiring.baml_prefix,
            observability_wired=False,
            memory_layer_wired=False,
            memory_layer_kind=None,
            pydantic_models_wired=False,
        )


__all__ = [
    "AgentFleetWiring",
    "AgentFramework",
    "WireAgent",
    "get_wiring",
    "wire_agent",
    "wiring_for_module_slug",
]