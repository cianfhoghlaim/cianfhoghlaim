"""tuatha.agents.hackathon.equivalency_generator — the Cross-Jurisdiction Equivalency Generator.

Compare LC ↔ A-Level ↔ GCSE topics side-by-side. Uses
`BAML EquivalencyTable` + the per-jurisdiction syllabus lookup
tools.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent

from ...config import TuathaConfig
from ...routing import build_wire

_wire = build_wire(
    ncca_subject="equivalency_generator",
    module_slug="equivalency_generator",
    display_name="Equivalency Generator",
    baml_prefix="EquivGen",
    langfuse_trace_name="agent.equivalency_generator.<verb>",
    cognee_dataset="oideachais_equivalency_generator",
    letta_agent_id="kcg-equivalency-generator-agent",
)

config = TuathaConfig.from_env()


equivalency_generator_agent = LlmAgent(
    name="equivalency_generator_agent",
    model=config.litellm.resolve_model("text_llm", "default"),
    description=(
        "Cross-Jurisdiction Equivalency Generator. Compare "
        "LC ↔ A-Level ↔ GCSE topics side-by-side. Uses the BAML "
        "EquivalencyTable + the per-jurisdiction syllabus lookup tools."
    ),
    instruction=(
        "You are the Equivalency Generator. The user picks a "
        "jurisdiction + a subject + a level → you generate the "
        "equivalency table across the 6 jurisdictions "
        "(NCCA + AQA + SQA + WJEC + CCEA + DESC)."
    ),
    output_key="equivalency_generator_response",
)


__all__ = ["_wire", "config", "equivalency_generator_agent"]
