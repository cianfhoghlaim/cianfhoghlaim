"""tuatha.subjects.geography — the Geography ADK agent.

One of 8 NCCA subject agents. BAML prefix: Geog.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import TuathaConfig
from ..routing import build_wire
from ..tools.geography_formative_item_generate import generate_geog_item
from ..tools.geography_marking_scheme_lookup import lookup_geog_marking_scheme
from ..tools.geography_past_paper_lookup import lookup_geog_paper
from ..tools.geography_response_score import score_geog_response
from ..tools.geography_syllabus_lookup import lookup_geog_lo

_wire = build_wire(
    ncca_subject="geography",
    module_slug="geog",
    display_name="Geography",
    baml_prefix="Geog",
    langfuse_trace_name="agent.geography.<verb>",
    cognee_dataset="oideachais_lc_geography",
    letta_agent_id="kcg-geography-agent",
)

config = TuathaConfig.from_env()

geog_syllabus_lookup_tool = FunctionTool(func=lookup_geog_lo)
geog_past_paper_lookup_tool = FunctionTool(func=lookup_geog_paper)
geog_marking_scheme_lookup_tool = FunctionTool(func=lookup_geog_marking_scheme)
geog_formative_item_generate_tool = FunctionTool(func=generate_geog_item)
geog_response_score_tool = FunctionTool(func=score_geog_response)


geog_agent = LlmAgent(
    name="geog_agent",
    model=config.litellm.resolve_model("ocr_vision", "media_descriptor"),
    description=(
        "Geography specialist agent for the NCCA Leaving "
        "Certificate and Junior Cycle curriculum. Physical "
        "geography, regional geography, human-environment "
        "interaction, geographic investigation."
    ),
    instruction=(
        "You are the Geography specialist agent for the new "
        "tuatha/ project. Route keyword-level traffic to your 5 "
        "per-subject tools and emit typed BAML responses per the "
        "`qpack_geography.baml` contract."
    ),
    tools=[
        geog_syllabus_lookup_tool,
        geog_past_paper_lookup_tool,
        geog_marking_scheme_lookup_tool,
        geog_formative_item_generate_tool,
        geog_response_score_tool,
    ],
    output_key="geography_response",
)


__all__ = ["_wire", "config", "geog_agent"]
