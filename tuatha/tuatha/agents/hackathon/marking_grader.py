"""tuatha.agents.hackathon.marking_grader — the Adaptive Marking Grader.

Per the
`openspec/changes/2026-08-21-biiep-hackathon-agentic-educational-system-v1/`:
the student uploads answer + marking scheme → instant grade + feedback.
"""
from __future__ import annotations

from google.adk.agents import LlmAgent

from ...config import TuathaConfig
from ...routing import build_wire

_wire = build_wire(
    ncca_subject="marking_grader",
    module_slug="marking_grader",
    display_name="Marking Grader",
    baml_prefix="MarkGrade",
    langfuse_trace_name="agent.marking_grader.<verb>",
    cognee_dataset="oideachais_marking_grader",
    letta_agent_id="kcg-marking-grader-agent",
)

config = TuathaConfig.from_env()


marking_grader_agent = LlmAgent(
    name="marking_grader_agent",
    model=config.litellm.resolve_model("text_llm", "default"),
    description=(
        "Adaptive Marking Grader. Student uploads answer + "
        "marking scheme → instant grade + feedback. Uses the "
        "OCR Router + BAML ScoreMarkingScheme + BAML GenerateFeedback."
    ),
    instruction=(
        "You are the Adaptive Marking Grader. The student "
        "uploads (1) their written answer (PDF or photo) and "
        "(2) the marking scheme PDF. Extract via the OCR Router, "
        "match against the marking scheme, write personalised "
        "feedback, and persist the grade to the Cognee memory "
        "bank."
    ),
    output_key="marking_grader_response",
)


__all__ = ["_wire", "config", "marking_grader_agent"]
