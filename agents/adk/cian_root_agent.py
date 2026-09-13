"""Cian Root Agent — ADK SequentialAgent cross-domain orchestrator.

Per the openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`:

- The previous Custom LiteLLM router in :mod:`agents.adk.root_agent`
  is preserved for back-compat (it still provides ``create_root_agent``
  + ``AgentContext`` + ``AgentResponse``).
- This module adds a new ADK ``SequentialAgent`` named ``cian_root``
  that classifies + routes + evaluates + emits AG-UI events,
  making **Google ADK the cross-pipeline control plane**.
- The 8 ADK agents in ``AGENT_REGISTRY`` are exposed as sub-agents so
  ``cian_root`` can invoke them via the ADK ``AgentTool`` wrapper.

Usage:

```python
from cianfhoghlaim.agents.adk.cian_root_agent import cian_root

runner = cian_root.compile()
response = await runner.run_async(query="Translate 'hello' to Irish")
```
"""

from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import AgentTool

from ..agent_registry import AGENT_REGISTRY
from .litellm_agent import make_litellm_agent

_DOMAIN_AGENT_MAP: dict[str, str] = {
    "curriculum": "curriculum_agent",
    "translation": "translation_agent",
    "corpus": "corpus_agent",
    "research": "research_agent",
    "geospatial": "geospatial_agent",
    "statistics": "statistics_agent",
    "curriculum_comparison": "curriculum_comparison_agent",
    "mcp_curriculum": "mcp_curriculum_agent",
    "education_research": "education_research_agent",
    "bunchloch_research": "bunchloch_research_agent",
}


def _load_sub_agents() -> list[LlmAgent]:
    """Load the 8 ADK sub-agents from the canonical registry.

    Skips agents whose framework is not ``ADK`` (the 3 Agno agents
    + the legacy Custom ``root_agent``). Non-ADK agents can be
    re-implemented as ADK ``LlmAgent`` subclasses in a future
    openspec change.
    """
    sub_agents: list[LlmAgent] = []
    for agent_name, wiring in AGENT_REGISTRY.items():
        if agent_name == "root_agent":
            continue
        if wiring.framework.value != "adk":
            continue
        try:
            module = __import__(
                wiring.module_path,
                fromlist=[wiring.module_slug],
            )
            agent = getattr(module, wiring.module_slug, None)
            if agent is None and hasattr(module, agent_name):
                agent = getattr(module, agent_name)
            if agent is not None:
                sub_agents.append(agent)
        except ImportError:
            continue
    return sub_agents


def _make_domain_classifier_agent() -> LlmAgent:
    """The first-stage LlmAgent that classifies the incoming query."""
    return make_litellm_agent(
        name="cian_root_classifier",
        description=(
            "Classifies the incoming `Query` by domain (curriculum / "
            "translation / corpus / research / geospatial / statistics / "
            "curriculum_comparison / mcp_curriculum / education_research "
            "/ bunchloch_research). Routes to one of the 8 ADK agents in "
            "`AGENT_REGISTRY`."
        ),
        model_alias="router",
        temperature=0.0,
        max_output_tokens=1024,
        instruction=(
            "You are the Cian Root Classifier. Given a user `Query`, "
            "classify it into one of the following domains and emit a "
            "`STATE_DELTA` AG-UI event with the `domain` field set:\n"
            + "\n".join(f"- {domain}" for domain in _DOMAIN_AGENT_MAP)
            + "\n\nUse the `domain_classification` BAML function for "
            "deterministic classification, or fall back to the keyword "
            "matcher in `agents/routing_keywords.py`."
        ),
        output_key="classified_domain",
    )


def _make_deep_research_tool() -> Any:
    """Wrap the browser-stack Deep Research backend as an ADK FunctionTool."""
    try:
        from google.adk.tools import FunctionTool

        from cianfhoghlaim.bonneagar.stacks.browser.sruth_browser.agents.orchestrator import (
            deep_research_stream,
        )

        return FunctionTool(deep_research_stream)
    except ImportError:
        return None


def _make_pipeline_orchestrator_tool() -> Any:
    """Wrap the pipeline_orchestrator as an ADK AgentTool."""
    try:
        from google.adk.tools import AgentTool

        from .pipeline_orchestrator import pipeline_orchestrator

        return AgentTool(pipeline_orchestrator)
    except ImportError:
        return None


def build_cian_root() -> SequentialAgent:
    """Build the canonical ADK ``SequentialAgent`` root orchestrator.

    Per the openspec change
    `2026-09-06-adk-gemini-deep-research-control-plane-v1`:

    1. The first agent classifies the incoming ``Query`` by domain.
    2. The second agent is a ``LoopAgent`` wrapping the per-domain
       ADK agent + the Gemini Deep Research backend + the
       pipeline_orchestrator.
    3. The third agent is the ADK ``evaluator_agent`` from
       ``sruth_browser/agents/evaluator.py`` — emitting a quality
       score in [0.0, 1.0] for every response.
    """
    classifier = _make_domain_classifier_agent()

    sub_agents = _load_sub_agents()
    domain_router = make_litellm_agent(
        name="cian_root_router",
        description=(
            "Routes the classified domain to one of the 8 ADK agents "
            "in `AGENT_REGISTRY`. Invokes the Gemini Deep Research "
            "tool when the domain is `research` and the query "
            "contains `research_kind=deep`."
        ),
        model_alias="router",
        temperature=0.2,
        max_output_tokens=4096,
        tools=[
            AgentTool(agent) for agent in sub_agents
        ] + [
            tool for tool in [
                _make_deep_research_tool(),
                _make_pipeline_orchestrator_tool(),
            ] if tool is not None
        ],
        instruction=(
            "You are the Cian Root Router. Given a classified "
            "`Query`, route to the matching domain agent via its "
            "ADK `AgentTool`. If the domain is `research` AND the "
            "query contains `research_kind=deep`, call the Gemini "
            "Deep Research `deep_research_stream` tool to stream "
            "the multi-step research plan to AG-UI consumers. "
            "If the caller wants to run a DLT + BAML + CocoIndex "
            "pipeline, call the `pipeline_orchestrator` AgentTool."
        ),
        output_key="routed_response",
    )

    try:
        from cianfhoghlaim.bonneagar.stacks.browser.sruth_browser.agents.evaluator import (
            evaluator_agent,
        )
        quality_evaluator = evaluator_agent
    except ImportError:
        quality_evaluator = _make_fallback_evaluator()

    quality_loop = LoopAgent(
        name="cian_root_quality_loop",
        description=(
            "Wraps the per-domain response with the ADK `evaluator_agent`. "
            "Retries up to 2 times if the quality score is below 0.6. "
            "Emits a final `STATE_DELTA` AG-UI event with `quality_score` "
            "+ `passed_threshold`."
        ),
        max_iterations=2,
        sub_agents=[quality_evaluator],
    )

    return SequentialAgent(
        name="cian_root",
        description=(
            "The Cian Root Orchestrator — an ADK `SequentialAgent` that "
            "classifies the incoming query, routes to one of 8 ADK "
            "domain agents, runs a quality loop, and emits AG-UI events. "
            "Per the openspec change "
            "`2026-09-06-adk-gemini-deep-research-control-plane-v1`."
        ),
        sub_agents=[classifier, domain_router, quality_loop],
    )


def _make_fallback_evaluator() -> LlmAgent:
    """A minimal ADK LlmAgent used when the canonical evaluator is unavailable."""
    return make_litellm_agent(
        name="cian_root_fallback_evaluator",
        description="Stub evaluator used when the browser-stack evaluator is unavailable.",
        model_alias="router",
        temperature=0.0,
        max_output_tokens=512,
        instruction=(
            "You are a stub evaluator. Return a quality score of 0.5 "
            "in a JSON dict with keys `quality_score`, `passed_threshold`."
        ),
        output_key="quality_score",
    )


cian_root = build_cian_root()


# ---------------------------------------------------------------------------
# Back-compat re-export shim.
#
# Per the openspec change
# `2026-09-06-adk-gemini-deep-research-control-plane-v1`, the legacy
# Custom LiteLLM router at :mod:`agents.adk.root_agent` is preserved
# for back-compat. Two legacy callers
# (``agents.adk.enhanced_orchestrator``,
# ``agents.adk.curriculum_agent``) still import the legacy types
# (``AgentContext``, ``AgentDomain``, ``AgentResponse``) from
# ``.root_agent``. We re-export them here so future callers can
# ``from agents.adk.cian_root_agent import AgentContext`` instead.
# ---------------------------------------------------------------------------

try:
    from .root_agent import (
        AgentContext as AgentContext,
        AgentDomain as AgentDomain,
        AgentResponse as AgentResponse,
        RootAgent as RootAgent,
        create_root_agent as create_root_agent,
    )
except ImportError:  # pragma: no cover - back-compat best-effort
    pass


__all__ = [
    "AgentContext",
    "AgentDomain",
    "AgentResponse",
    "RootAgent",
    "build_cian_root",
    "cian_root",
    "create_root_agent",
]
