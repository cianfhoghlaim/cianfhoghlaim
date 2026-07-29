"""Smoke tests for the AGENT_REGISTRY contract.

Verifies the 4 canonical scenarios for the canonical
``AGENT_REGISTRY`` dict (introduced by the
``2026-08-14-agents-fleet-wiring-parity-v1`` change):

1. AGENT_REGISTRY has 12 entries (or 20 if the 8 NCCA subjects
   are registered)
2. Each AgentFleetWiring has a valid ``framework`` attribute
3. Cognee dataset names match the canonical pattern
   ``oideachais_lc_<subject>`` (or ``oideachais_<subject>``)
4. Langfuse trace names match the canonical pattern
   ``agent.<slug>.<verb>``
"""
from __future__ import annotations

import re

import pytest


def test_agent_registry_size():
    """``AGENT_REGISTRY`` has at least 12 entries (the 12 main agents).

    The 8 NCCA subject agents may be additionally registered via
    ``agents/tuatha/wiring.py:register_ncca_subjects_in_agent_registry``.
    """
    from cianfhoghlaim.agents.agent_registry import AGENT_REGISTRY

    assert len(AGENT_REGISTRY) >= 12, (
        f"Expected ≥ 12 entries in AGENT_REGISTRY, got {len(AGENT_REGISTRY)}"
    )


def test_agent_registry_frameworks_are_valid():
    """Each agent's ``framework`` attribute is one of the 5 valid frameworks.

    The 5 frameworks are: ``Custom``, ``ADK``, ``Agno``, ``Pipecat``,
    ``CopilotKit``. Pipecat + CopilotKit are stubs (not yet live).
    """
    from cianfhoghlaim.agents.agent_registry import AGENT_REGISTRY

    valid_frameworks = {"Custom", "ADK", "Agno", "Pipecat", "CopilotKit"}
    for agent_name, wiring in AGENT_REGISTRY.items():
        framework = wiring.framework.value
        assert framework in valid_frameworks, (
            f"{agent_name}: framework={framework} not in {valid_frameworks}"
        )


def test_agent_registry_cognee_dataset_names():
    """Each agent's ``cognee_dataset`` matches ``oideachais[_lc]_?_*``.

    The canonical pattern is ``oideachais_lc_<subject>`` for NCCA
    subject agents, ``oideachais_<subject>`` for the 12 main agents.
    """
    from cianfhoghlaim.agents.agent_registry import AGENT_REGISTRY

    pattern = re.compile(r"^oideachais(_lc)?_[a-z_]+$")
    for agent_name, wiring in AGENT_REGISTRY.items():
        dataset = wiring.cognee_dataset
        assert pattern.match(dataset), (
            f"{agent_name}: cognee_dataset='{dataset}' does not match "
            f"pattern 'oideachais[_lc]_<subject>'"
        )


def test_agent_registry_langfuse_trace_names():
    """Each agent's ``langfuse_trace_name`` matches ``agent.<slug>.<verb>``.

    The canonical pattern is the per-agent Langfuse trace name.
    """
    from cianfhoghlaim.agents.agent_registry import AGENT_REGISTRY

    pattern = re.compile(r"^agent\.[a-z_]+\.[a-z_]+$")
    for agent_name, wiring in AGENT_REGISTRY.items():
        trace_name = wiring.langfuse_trace_name
        assert pattern.match(trace_name), (
            f"{agent_name}: langfuse_trace_name='{trace_name}' does not "
            f"match pattern 'agent.<slug>.<verb>'"
        )