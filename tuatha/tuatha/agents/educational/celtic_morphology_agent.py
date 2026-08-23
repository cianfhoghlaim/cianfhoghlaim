"""tuatha.agents.educational.celtic_morphology_agent — the Celtic morphology specialist agent.

Handles queries about the morphology of the 6 Celtic languages
(verb conjugation + noun declension + adjective agreement +
prefix/suffix/infix patterns + calque identification).
"""
from __future__ import annotations

from google.adk.agents import LlmAgent

from ...config import TuathaConfig
from ...routing import build_wire

_wire = build_wire(
    ncca_subject="celtic_morphology",
    module_slug="celtic_morphology",
    display_name="Celtic Morphology",
    baml_prefix="CeltMorph",
    langfuse_trace_name="agent.celtic_morphology.<verb>",
    cognee_dataset="oideachais_celtic_morphology",
    letta_agent_id="kcg-celtic-morphology-agent",
)

config = TuathaConfig.from_env()


celtic_morphology_agent = LlmAgent(
    name="celtic_morphology_agent",
    model=config.litellm.resolve_model("text_llm", "default"),
    description=(
        "Celtic morphology specialist agent for the 6 Celtic "
        "languages. Verb conjugation + noun declension + "
        "adjective agreement + prefix/suffix/infix patterns + "
        "calque identification."
    ),
    instruction=(
        "You are the Celtic morphology specialist agent. You "
        "handle queries about the morphology of the 6 Celtic "
        "languages. Route keyword-level traffic and emit typed "
        "BAML responses per the `qpack_celtic_morphology.baml` contract."
    ),
    output_key="celtic_morphology_response",
)


__all__ = ["_wire", "celtic_morphology_agent", "config"]
