"""tuatha.subjects.history — the History ADK agent.

One of 8 NCCA subject agents. BAML prefix: Hist.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.history_formative_item_generate import generate_hist_item
from ..tools.history_marking_scheme_lookup import lookup_hist_marking_scheme
from ..tools.history_past_paper_lookup import lookup_hist_paper
from ..tools.history_response_score import score_hist_response
from ..tools.history_syllabus_lookup import lookup_hist_lo

_wire = build_wire(
    ncca_subject="history",
    module_slug="hist",
    display_name="History",
    baml_prefix="Hist",
    langfuse_trace_name="agent.history.<verb>",
    cognee_dataset="oideachais_lc_history",
    letta_agent_id="kcg-history-agent",
)

config = TuathaConfig.from_env()

hist_syllabus_lookup_tool = FunctionTool(func=lookup_hist_lo)
hist_past_paper_lookup_tool = FunctionTool(func=lookup_hist_paper)
hist_marking_scheme_lookup_tool = FunctionTool(func=lookup_hist_marking_scheme)
hist_formative_item_generate_tool = FunctionTool(func=generate_hist_item)
hist_response_score_tool = FunctionTool(func=score_hist_response)


hist_agent = LlmAgent(
    name="hist_agent",
    model=config.litellm.resolve_model("ocr_vision", "media_descriptor"),
    description=(
        "History specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Early modern, "
        "modern Irish, European, world history."
    ),
    instruction=(
        "You are the History specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_history.baml` contract."
    ),
    tools=[
        hist_syllabus_lookup_tool,
        hist_past_paper_lookup_tool,
        hist_marking_scheme_lookup_tool,
        hist_formative_item_generate_tool,
        hist_response_score_tool,
    ],
    output_key="history_response",
)


__all__ = ["_wire", "config", "hist_agent"]
