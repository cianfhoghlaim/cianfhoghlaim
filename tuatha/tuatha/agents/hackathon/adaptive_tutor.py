"""tuatha.agents.hackathon.adaptive_tutor — the Adaptive Tutor Chat.

Stateful 6-jurisdiction syllabus tutor with persistent memory.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent

from ...config import TuathaConfig
from ...routing import build_wire

_wire = build_wire(
    ncca_subject="adaptive_tutor",
    module_slug="adaptive_tutor",
    display_name="Adaptive Tutor",
    baml_prefix="AdaptTutor",
    langfuse_trace_name="agent.adaptive_tutor.<verb>",
    cognee_dataset="oideachais_adaptive_tutor",
    letta_agent_id="kcg-adaptive-tutor-agent",
)

config = TuathaConfig.from_env()


adaptive_tutor_agent = LlmAgent(
    name="adaptive_tutor_agent",
    model=config.litellm.resolve_model("text_llm", "default"),
    description=(
        "Adaptive Tutor Chat. Stateful 6-jurisdiction syllabus "
        "tutor with persistent memory (Cognee + Letta). Routes "
        "to the right NCCA / AQA / SQA / WJEC / CCEA / DESC syllabus."
    ),
    instruction=(
        "You are the Adaptive Tutor. You chat with a student "
        "and adapt difficulty based on the concepts they struggle "
        "with. You route to the right jurisdiction's syllabus via "
        "the 13-agent fleet + the per-subject agents."
    ),
    output_key="adaptive_tutor_response",
)


__all__ = ["_wire", "adaptive_tutor_agent", "config"]
