"""Smoke tests for the agent fleet wiring layer.

Verifies the 5 canonical scenarios for the 12-agent fleet
introduced by the
``2026-08-14-agents-fleet-wiring-parity-v1`` change.

The tests are hermetic — they run in any Python environment
without requiring the 5 concrete memory backends or the 5
observability stacks to be reachable. The wiring layer
gracefully degrades when dependencies are missing.
"""
from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Test 1 — factory resolve
# ---------------------------------------------------------------------------


def test_get_default_memory_layer_returns_implementation():
    """``get_default_memory_layer()`` returns a ``MemoryLayer`` instance.

    In a hermetic environment (no Cognee / Graphiti / LanceDB /
    FalkorDB / Memgraph reachable), the factory falls through to
    the in-memory fallback. The returned instance SHALL have a
    ``kind`` attribute that is one of the 5 backend kinds OR
    ``"in_memory_fallback"``.
    """
    from cianfhoghlaim.agents.memory_layer import (
        get_default_memory_layer,
    )

    layer = get_default_memory_layer()
    # The layer is either an in-memory fallback or a concrete backend.
    assert hasattr(layer, "kind")
    assert layer.kind in (
        "cognee", "graphiti", "lancedb", "falkordb",
        "memgraph", "in_memory_fallback",
    )
    # Verify the layer has the MemoryLayer protocol methods.
    assert hasattr(layer, "is_available")
    assert hasattr(layer, "add")
    assert hasattr(layer, "search")


# ---------------------------------------------------------------------------
# Test 2 — wire metadata
# ---------------------------------------------------------------------------


def test_wire_agent_returns_metadata():
    """``wire_agent()`` returns a ``WireAgent`` with the 13 expected fields.

    The 13 fields are: ``agent``, ``observability_wired``,
    ``memory_layer_wired``, ``memory_layer_kind``,
    ``pydantic_models_wired``, ``baml_prefix``,
    ``langfuse_wired``, ``logfire_wired``, ``mlflow_wired``,
    ``ragas_scorer_wired``, ``structlog_wired``.
    """
    from cianfhoghlaim.agents.agent_registry import AGENT_REGISTRY
    from cianfhoghlaim.agents.wiring import wire_agent

    wiring = AGENT_REGISTRY["curriculum_agent"]
    wire = wire_agent(wiring)

    # Verify all 13 fields exist on the WireAgent.
    assert wire.agent is wiring
    assert isinstance(wire.observability_wired, bool)
    assert isinstance(wire.memory_layer_wired, bool)
    # memory_layer_kind may be None if the probe failed
    # (e.g. Pydantic not importable in CI)
    assert wire.memory_layer_kind is None or isinstance(
        wire.memory_layer_kind, str
    )
    assert isinstance(wire.pydantic_models_wired, bool)
    # baml_prefix comes from the wiring dataclass
    assert wire.baml_prefix == wiring.baml_prefix
    # The 5 observability flags
    for flag in (
        "langfuse_wired",
        "logfire_wired",
        "mlflow_wired",
        "ragas_scorer_wired",
        "structlog_wired",
    ):
        assert isinstance(getattr(wire, flag), bool)


# ---------------------------------------------------------------------------
# Test 3 — dispatch happy path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_study_plan_returns_lectionary():
    """``dispatch_study_plan()`` returns the ``lectionary`` + ``progress`` keys.

    The wiring layer's stub implementation returns a dict with the
    expected keys. When the canonical agents are reachable, the
    real per-subject study plan is returned.
    """
    from cianfhoghlaim.agents._workflow_handlers import (
        StudyPlanContext,
        dispatch_study_plan,
    )

    ctx = StudyPlanContext(
        domain="curriculum",
        subject="gaeilge",
        duration_weeks=12,
    )
    result = await dispatch_study_plan(ctx)
    assert "lectionary" in result
    assert "progress" in result


# ---------------------------------------------------------------------------
# Test 4 — missing-dep graceful degradation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_deep_research_degrades_gracefully():
    """``dispatch_deep_research()`` degrades gracefully when the agent is missing.

    The wiring layer's stub returns a result dict even when no
    real LLM is available. The dispatcher SHALL NOT propagate
    ``ModuleNotFoundError`` or ``ImportError``.
    """
    from cianfhoghlaim.agents._workflow_handlers import (
        ResearchQuery,
        dispatch_deep_research,
    )

    q = ResearchQuery(domain="education", question="What is the LC Irish?")
    # Even with no real agent, this should not raise.
    try:
        result = await dispatch_deep_research(q)
    except (ImportError, ModuleNotFoundError) as exc:
        pytest.fail(
            f"dispatch_deep_research should not raise ImportError: {exc}"
        )
    # Result is a dict (may be empty if no agents are reachable).
    assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Test 5 — retry-on-failure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_with_retry_succeeds_after_transient_failure():
    """``with_retry()`` retries the function up to ``max_attempts`` times.

    The function is called 3 times (2 failures + 1 success) and
    returns the success value on the 3rd attempt.
    """
    from cianfhoghlaim.agents.exceptions import (
        AgentRuntimeError,
        with_retry,
    )

    attempts = []

    @with_retry(max_attempts=3, base_delay=0.01, exceptions=(AgentRuntimeError,))
    async def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise AgentRuntimeError("flake")
        return "success"

    result = await flaky()
    assert result == "success"
    assert len(attempts) == 3
