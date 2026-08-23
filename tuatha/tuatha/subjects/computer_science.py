"""tuatha.subjects.computer_science — the Computer Science ADK agent.

One of 8 NCCA subject agents. BAML prefix: Comp.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.computer_science_formative_item_generate import generate_comp_item
from ..tools.computer_science_marking_scheme_lookup import lookup_comp_marking_scheme
from ..tools.computer_science_past_paper_lookup import lookup_comp_paper
from ..tools.computer_science_response_score import score_comp_response
from ..tools.computer_science_syllabus_lookup import lookup_comp_lo

_wire = build_wire(
    ncca_subject="computer_science",
    module_slug="comp",
    display_name="Computer Science",
    baml_prefix="Comp",
    langfuse_trace_name="agent.computer_science.<verb>",
    cognee_dataset="oideachais_lc_computer_science",
    letta_agent_id="kcg-computer-science-agent",
)

config = TuathaConfig.from_env()

comp_syllabus_lookup_tool = FunctionTool(func=lookup_comp_lo)
comp_past_paper_lookup_tool = FunctionTool(func=lookup_comp_paper)
comp_marking_scheme_lookup_tool = FunctionTool(func=lookup_comp_marking_scheme)
comp_formative_item_generate_tool = FunctionTool(func=generate_comp_item)
comp_response_score_tool = FunctionTool(func=score_comp_response)


comp_agent = LlmAgent(
    name="comp_agent",
    model=config.litellm.resolve_model("ocr_vision", "media_descriptor"),
    description=(
        "Computer Science specialist agent for the NCCA Leaving "
        "Certificate curriculum. Algorithms, data structures, "
        "computational thinking, programming, databases."
    ),
    instruction=(
        "You are the Computer Science specialist agent for the "
        "new tuatha/ project. Route keyword-level traffic to your "
        "5 per-subject tools and emit typed BAML responses per the "
        "`qpack_computer_science.baml` contract."
    ),
    tools=[
        comp_syllabus_lookup_tool,
        comp_past_paper_lookup_tool,
        comp_marking_scheme_lookup_tool,
        comp_formative_item_generate_tool,
        comp_response_score_tool,
    ],
    output_key="computer_science_response",
)


__all__ = ["_wire", "comp_agent", "config"]
