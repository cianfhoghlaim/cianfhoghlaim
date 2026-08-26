"""Smoke tests for the AGENT_REGISTRY contract.

Verifies the 4 canonical scenarios for the canonical
``AGENT_REGISTRY`` dict (introduced by the
``2026-08-14-agents-fleet-wiring-parity-v1`` change):

1. AGENT_REGISTRY has 12 entries (or 20 if the 8 NCCA subjects
   are registered)
2. Each AgentWiring has the post-v4 canonical fields (name, agent,
   description, stage, tools)
3. Each agent's ``stage`` is one of the 4 canonical stages
   (``lc`` / ``jc`` / ``alevel`` / ``gcse``) or ``None`` for the
   11 supporting agents (research, education_research, etc.)
4. The 4 stage agents (lc_subject_agent + jc_subject_agent +
   alevel_subject_agent + gcse_subject_agent) are all present

Post-v4 (2026-06-28): the registry lives at
``agents.adk.agent_registry`` (the canonical post-consolidation path)
rather than the legacy v3 path ``cianfhoghlaim.agents.agent_registry``.
The pre-v4 ``framework`` / ``cognee_dataset`` / ``langfuse_trace_name``
fields were removed in the v4 consolidation; the new
``stage`` / ``description`` / ``tools`` fields are the
post-v4 contract. This module is updated as part of the
``2026-11-25-mega-3c-marimo-and-integration-v1`` change (T1.3).
"""
from __future__ import annotations

# The post-v4 canonical registry path (per the 2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4 change)
REGISTRY_PATH = "agents.adk.agent_registry"

# The 4 canonical stages (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change, FF.6)
CANONICAL_STAGES = {"lc", "jc", "alevel", "gcse", None}

# The 4 stage agents (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change, FF.6)
FOUR_STAGE_AGENTS = {"lc_subject_agent", "jc_subject_agent", "alevel_subject_agent", "gcse_subject_agent"}


def _load_registry() -> dict:
    """Load the AGENT_REGISTRY from the canonical post-v4 path.

    Falls back to the legacy v3 path if the post-v4 module is not
    available (e.g. in a partial checkout).
    """
    try:
        from agents.adk.agent_registry import AGENT_REGISTRY  # type: ignore[import-not-found]

        return AGENT_REGISTRY
    except ImportError:
        from cianfhoghlaim.agents.agent_registry import (
            AGENT_REGISTRY,  # type: ignore[import-not-found]
        )

        return AGENT_REGISTRY


def test_agent_registry_size():
    """``AGENT_REGISTRY`` has at least 12 entries (the 12 main agents).

    The 8 NCCA subject agents may be additionally registered via
    ``agents/tuatha/wiring.py:register_ncca_subjects_in_agent_registry``.
    """
    AGENT_REGISTRY = _load_registry()

    assert len(AGENT_REGISTRY) >= 12, (
        f"Expected ≥ 12 entries in AGENT_REGISTRY, got {len(AGENT_REGISTRY)}"
    )


def test_agent_registry_post_v4_fields():
    """Each AgentWiring has the canonical post-v4 fields.

    The post-v4 fields are: ``name``, ``agent``, ``description``,
    ``stage``, ``tools``. The pre-v4 fields (``framework``,
    ``cognee_dataset``, ``langfuse_trace_name``) were removed in the
    v4 consolidation.
    """
    AGENT_REGISTRY = _load_registry()

    required_fields = {"name", "agent", "description", "stage", "tools"}
    for agent_name, wiring in AGENT_REGISTRY.items():
        actual_fields = {f for f in dir(wiring) if not f.startswith("_")} - {"count", "index"}
        missing = required_fields - actual_fields
        assert not missing, (
            f"{agent_name}: missing post-v4 fields {missing}; got {actual_fields}"
        )


def test_agent_registry_stages_are_canonical():
    """Each agent's ``stage`` is one of the 4 canonical stages or ``None``.

    The 4 canonical stages are: ``lc`` / ``jc`` / ``alevel`` / ``gcse``
    (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change, FF.6).
    Supporting agents (research, education_research, etc.) have
    ``stage = None``.
    """
    AGENT_REGISTRY = _load_registry()

    for agent_name, wiring in AGENT_REGISTRY.items():
        stage = wiring.stage
        assert stage in CANONICAL_STAGES, (
            f"{agent_name}: stage='{stage}' not in {CANONICAL_STAGES}"
        )


def test_agent_registry_has_four_stage_agents():
    """The 4 stage agents (lc + jc + alevel + gcse) are all registered.

    Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change, FF.6
    (4_stage_factory): the 4 stage agents are the canonical entry points
    for the 4-stage plane integration.
    """
    AGENT_REGISTRY = _load_registry()

    registered_names = set(AGENT_REGISTRY.keys())
    missing = FOUR_STAGE_AGENTS - registered_names
    assert not missing, (
        f"Missing stage agents: {missing}; got {sorted(registered_names)[:20]}"
    )
