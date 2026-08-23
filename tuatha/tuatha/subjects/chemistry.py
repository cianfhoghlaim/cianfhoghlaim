"""tuatha.subjects.chemistry — the Chemistry ADK agent.

One of 8 NCCA subject agents. BAML prefix: Chem.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.chemistry_formative_item_generate import generate_chem_item
from ..tools.chemistry_marking_scheme_lookup import lookup_chem_marking_scheme
from ..tools.chemistry_past_paper_lookup import lookup_chem_paper
from ..tools.chemistry_response_score import score_chem_response
from ..tools.chemistry_syllabus_lookup import lookup_chem_lo

_wire = build_wire(
    ncca_subject="chemistry",
    module_slug="chem",
    display_name="Chemistry",
    baml_prefix="Chem",
    langfuse_trace_name="agent.chemistry.<verb>",
    cognee_dataset="oideachais_lc_chemistry",
    letta_agent_id="kcg-chemistry-agent",
)

config = TuathaConfig.from_env()

chem_syllabus_lookup_tool = FunctionTool(func=lookup_chem_lo)
chem_past_paper_lookup_tool = FunctionTool(func=lookup_chem_paper)
chem_marking_scheme_lookup_tool = FunctionTool(func=lookup_chem_marking_scheme)
chem_formative_item_generate_tool = FunctionTool(func=generate_chem_item)
chem_response_score_tool = FunctionTool(func=score_chem_response)


chem_agent = LlmAgent(
    name="chem_agent",
    model=config.litellm.resolve_model("ocr_vision", "media_descriptor"),
    description=(
        "Chemistry specialist agent for the NCCA Leaving Certificate "
        "and Junior Cycle curriculum. Atomic structure, bonding, "
        "stoichiometry, organic chemistry, equilibrium."
    ),
    instruction=(
        "You are the Chemistry specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_chemistry.baml` contract."
    ),
    tools=[
        chem_syllabus_lookup_tool,
        chem_past_paper_lookup_tool,
        chem_marking_scheme_lookup_tool,
        chem_formative_item_generate_tool,
        chem_response_score_tool,
    ],
    output_key="chemistry_response",
)


__all__ = ["_wire", "chem_agent", "config"]
