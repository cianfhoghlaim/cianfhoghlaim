"""tuatha.subjects.english — the English ADK agent.

One of 8 NCCA subject agents. BAML prefix: Engl.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.english_formative_item_generate import generate_engl_item
from ..tools.english_marking_scheme_lookup import lookup_engl_marking_scheme
from ..tools.english_past_paper_lookup import lookup_engl_paper
from ..tools.english_response_score import score_engl_response
from ..tools.english_syllabus_lookup import lookup_engl_lo

_wire = build_wire(
    ncca_subject="english",
    module_slug="engl",
    display_name="English",
    baml_prefix="Engl",
    langfuse_trace_name="agent.english.<verb>",
    cognee_dataset="oideachais_lc_english",
    letta_agent_id="kcg-english-agent",
)

config = TuathaConfig.from_env()

engl_syllabus_lookup_tool = FunctionTool(func=lookup_engl_lo)
engl_past_paper_lookup_tool = FunctionTool(func=lookup_engl_paper)
engl_marking_scheme_lookup_tool = FunctionTool(func=lookup_engl_marking_scheme)
engl_formative_item_generate_tool = FunctionTool(func=generate_engl_item)
engl_response_score_tool = FunctionTool(func=score_engl_response)


engl_agent = LlmAgent(
    name="engl_agent",
    model=config.litellm.resolve_model("ocr_vision", "media_descriptor"),
    description=(
        "English specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Comprehension, "
        "composition, language awareness, literary analysis."
    ),
    instruction=(
        "You are the English specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_english.baml` contract."
    ),
    tools=[
        engl_syllabus_lookup_tool,
        engl_past_paper_lookup_tool,
        engl_marking_scheme_lookup_tool,
        engl_formative_item_generate_tool,
        engl_response_score_tool,
    ],
    output_key="english_response",
)


__all__ = ["_wire", "config", "engl_agent"]
