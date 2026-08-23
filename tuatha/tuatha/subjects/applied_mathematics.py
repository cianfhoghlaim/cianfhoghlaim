"""tuatha.subjects.applied_mathematics — the Applied Mathematics ADK agent.

One of 8 NCCA subject agents. Mirrors the Mathematics agent
pattern. BAML prefix: AppM.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.applied_mathematics_formative_item_generate import generate_appm_item
from ..tools.applied_mathematics_marking_scheme_lookup import lookup_appm_marking_scheme
from ..tools.applied_mathematics_past_paper_lookup import lookup_appm_paper
from ..tools.applied_mathematics_response_score import score_appm_response
from ..tools.applied_mathematics_syllabus_lookup import lookup_appm_lo

_wire = build_wire(
    ncca_subject="applied_mathematics",
    module_slug="appm",
    display_name="Applied Mathematics",
    baml_prefix="AppM",
    langfuse_trace_name="agent.applied_mathematics.<verb>",
    cognee_dataset="oideachais_lc_applied_mathematics",
    letta_agent_id="kcg-applied-mathematics-agent",
)

config = TuathaConfig.from_env()

appm_syllabus_lookup_tool = FunctionTool(func=lookup_appm_lo)
appm_past_paper_lookup_tool = FunctionTool(func=lookup_appm_paper)
appm_marking_scheme_lookup_tool = FunctionTool(func=lookup_appm_marking_scheme)
appm_formative_item_generate_tool = FunctionTool(func=generate_appm_item)
appm_response_score_tool = FunctionTool(func=score_appm_response)


appm_agent = LlmAgent(
    name="appm_agent",
    model=config.litellm.resolve_model("ocr_vision", "media_descriptor"),
    description=(
        "Applied Mathematics specialist agent for the NCCA "
        "Leaving Certificate and Junior Cycle curriculum. "
        "Mechanics, sequences + series, coordinate geometry, "
        "differential equations."
    ),
    instruction=(
        "You are the Applied Mathematics specialist agent for the "
        "new tuatha/ project. You handle queries about the NCCA "
        "Leaving Certificate + Junior Cycle Applied Mathematics "
        "syllabus. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_applied_mathematics.baml` contract."
    ),
    tools=[
        appm_syllabus_lookup_tool,
        appm_past_paper_lookup_tool,
        appm_marking_scheme_lookup_tool,
        appm_formative_item_generate_tool,
        appm_response_score_tool,
    ],
    output_key="applied_mathematics_response",
)


__all__ = ["_wire", "appm_agent", "config"]
