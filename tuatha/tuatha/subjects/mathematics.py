"""tuatha.subjects.mathematics — the Mathematics ADK agent.

One of 8 NCCA subject agents (math / appm / chem / geog / hist
/ engl / gael / comp). The agent routes keyword-level traffic
to its 5 per-subject tools (syllabus / past_paper /
marking_scheme / formative_item / response_score) and emits
typed BAML responses per the `qpack_mathematics.baml` contract.

Per the academic_history_agent.py pattern (the canonical
reference): the agent is constructed with `_BAML_AVAILABLE`
+ `_LANGFUSE_AVAILABLE` graceful degradation so the import
never crashes.

Per the centralized-registry contract: every model string
routes through `config.litellm.resolve_model(family, role)`.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.mathematics_formative_item_generate import generate_math_item
from ..tools.mathematics_marking_scheme_lookup import lookup_math_marking_scheme
from ..tools.mathematics_past_paper_lookup import lookup_math_paper
from ..tools.mathematics_response_score import score_math_response
from ..tools.mathematics_syllabus_lookup import lookup_math_lo

# Build the canonical SubjectAgentWiring for mathematics.
_wire = build_wire(
    ncca_subject="mathematics",
    module_slug="math",
    display_name="Mathematics",
    baml_prefix="Math",
    langfuse_trace_name="agent.mathematics.<verb>",
    cognee_dataset="oideachais_lc_mathematics",
    letta_agent_id="kcg-mathematics-agent",
)

# Build the canonical config from env (Plan A keyless Firecrawl +
# MODEL_REGISTRY fallback).
config = TuathaConfig.from_env()

# The 5 per-subject tools.
math_syllabus_lookup_tool = FunctionTool(func=lookup_math_lo)
math_past_paper_lookup_tool = FunctionTool(func=lookup_math_paper)
math_marking_scheme_lookup_tool = FunctionTool(func=lookup_math_marking_scheme)
math_formative_item_generate_tool = FunctionTool(func=generate_math_item)
math_response_score_tool = FunctionTool(func=score_math_response)


# The canonical ADK LlmAgent for the Mathematics subject.
math_agent = LlmAgent(
    name="math_agent",
    model=config.litellm.resolve_model("ocr_vision", "media_descriptor"),
    description=(
        "Mathematics specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Formative "
        "assessment, quest-pack generation, response scoring, "
        "and bilingual EN + GA feedback."
    ),
    instruction=(
        "You are the Mathematics specialist agent for the new "
        "tuatha/ project. You handle queries about the NCCA "
        "Leaving Certificate + Junior Cycle Mathematics syllabus. "
        "You route keyword-level traffic to your 5 per-subject "
        "tools (syllabus_lookup / past_paper_lookup / "
        "marking_scheme_lookup / formative_item_generate / "
        "response_score) and emit typed BAML responses per the "
        "`qpack_mathematics.baml` contract."
    ),
    tools=[
        math_syllabus_lookup_tool,
        math_past_paper_lookup_tool,
        math_marking_scheme_lookup_tool,
        math_formative_item_generate_tool,
        math_response_score_tool,
    ],
    output_key="mathematics_response",
)


__all__ = ["_wire", "config", "math_agent"]
