"""ADK pipeline orchestrator agents.

Per the openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`, this sub-package
contains 3 ADK `LlmAgent` subclasses that wrap the canonical
DLT → BAML → CocoIndex pipeline as ADK `FunctionTool`s:

- :class:`dlt_trigger_agent` — runs a DLT source, emits a `STATE_DELTA`
  AG-UI event with the ``pipeline_run_id`` + ``load_info``.
- :class:`baml_extract_agent` — calls a BAML extraction function on
  each row; falls back through the 4-tier provider chain (Unsloth →
  LiteLLM → MiniMax → Gemini) on `quality_score < 0.6`.
- :class:`cocoindex_index_agent` — invokes `coco.update()` on the named
  CocoIndex App with the BAML-extracted rows.

The 3 agents are wrapped in a :class:`pipeline_orchestrator`
`SequentialAgent` (with a `LoopAgent` wrapping `baml_extract_agent`)
to drive the canonical pipeline from inside the ADK runtime.
"""

from .baml_extract_agent import baml_extract_agent, extract_baml_function
from .cocoindex_index_agent import cocoindex_index_agent, update_cocoindex_app
from .dlt_trigger_agent import dlt_trigger_agent, run_dlt_source
from .orchestrator import (
    extract_quality_loop,
    pipeline_orchestrator,
)

__all__ = [
    "baml_extract_agent",
    "cocoindex_index_agent",
    "dlt_trigger_agent",
    "extract_baml_function",
    "extract_quality_loop",
    "pipeline_orchestrator",
    "run_dlt_source",
    "update_cocoindex_app",
]
