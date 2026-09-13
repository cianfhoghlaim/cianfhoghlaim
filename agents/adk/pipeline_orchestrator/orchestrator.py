"""Pipeline orchestrator — SequentialAgent + LoopAgent wrapping the 3 pipeline agents.

Per the openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`. Drives the
canonical DLT → BAML → CocoIndex pipeline from inside the ADK runtime.
"""

from __future__ import annotations

from google.adk.agents import LoopAgent, SequentialAgent

from .baml_extract_agent import baml_extract_agent
from .cocoindex_index_agent import cocoindex_index_agent
from .dlt_trigger_agent import dlt_trigger_agent

extract_quality_loop = LoopAgent(
    name="extract_quality_loop",
    description=(
        "Retries the BAML extraction step with the 4-tier provider "
        "chain (Unsloth → LiteLLM → MiniMax → Gemini) until "
        "`quality_score >= 0.6` or 3 attempts have been made."
    ),
    max_iterations=3,
    sub_agents=[baml_extract_agent],
)

pipeline_orchestrator = SequentialAgent(
    name="pipeline_orchestrator",
    description=(
        "Runs the canonical DLT → BAML → CocoIndex pipeline as an ADK "
        "agent chain. Per the "
        "2026-09-06-adk-gemini-deep-research-control-plane-v1 change. "
        "Emits a `STATE_DELTA` AG-UI event after each stage."
    ),
    sub_agents=[
        dlt_trigger_agent,
        extract_quality_loop,
        cocoindex_index_agent,
    ],
)


__all__ = ["extract_quality_loop", "pipeline_orchestrator"]
