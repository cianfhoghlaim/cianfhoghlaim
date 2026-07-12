"""
Computer Science Specialist Agent (comp_agent) — Cianfhoghlaim Educational MMO.
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config
from .tools.comp_tools import (
    lookup_comp_lo,
    lookup_comp_paper,
    lookup_comp_marking_scheme,
    generate_comp_item,
    score_comp_response,
)

# Feat C (2026-07-10): StorageBackend Protocol + Langfuse + Cognee + BAML.
from .wiring import (
    emit_to_cognee,
    get_wiring,
    open_langfuse_trace,
    resolve_baml_function,
    wire_subject_agent,
)

# BIEP v1 (2026-07-16): per-subject workflow handlers.
from ._workflow_handlers import (
    StudyPlanContext,
    attach_subject_workflow_handlers,
    build_subject_workflow_handlers,
)

_COMP_WIRING = get_wiring("computer_science")


async def comp_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    try:
        return await lookup_comp_lo(topic=topic, level=level, language="en", limit=10)
    except Exception:
        return []


async def comp_past_paper_lookup_tool(topic: str, level: str = "lc_hl", year: int | None = None) -> list[dict]:
    try:
        return await lookup_comp_paper(topic=topic, level=level, year=year, limit=5)
    except Exception:
        return []


async def comp_marking_scheme_lookup_tool(lo_code: str) -> dict:
    try:
        return await lookup_comp_marking_scheme(lo_code=lo_code)
    except Exception:
        return {"error": "marking scheme lookup failed"}


async def comp_formative_item_generate_tool(lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = "") -> dict:
    try:
        return await generate_comp_item(lo_code=lo_code, difficulty=difficulty, level=level, topic=topic)
    except Exception as exc:
        return {"error": f"Item generation failed: {exc}"}


async def comp_response_score_tool(item_id: str, student_response: str, response_format: str = "code", time_taken_seconds: int = 0, hints_used: int = 0) -> dict:
    try:
        return await score_comp_response(item_id=item_id, student_response=student_response, response_format=response_format, time_taken_seconds=time_taken_seconds, hints_used=hints_used)
    except Exception as exc:
        return {"error": f"Scoring failed: {exc}"}


comp_syllabus_tool = FunctionTool(func=comp_syllabus_lookup_tool)
comp_past_paper_tool = FunctionTool(func=comp_past_paper_lookup_tool)
comp_marking_scheme_tool = FunctionTool(func=comp_marking_scheme_lookup_tool)
comp_formative_item_tool = FunctionTool(func=comp_formative_item_generate_tool)
comp_response_score_tool = FunctionTool(func=comp_response_score_tool)


comp_agent = LlmAgent(
    name="comp_agent",
    model=config.worker_model,
    description=(
        "Computer Science specialist agent for NCCA Leaving Certificate "
        "Computer Science (OL + HL) + Junior Cycle Coding short course. "
        "Algorithms, data structures, programming (Python), computational thinking."
    ),
    instruction=f"""
    You are the Computer Science Specialist Agent for the Cianfhoghlaim Educational MMO.
    You teach NCCA Leaving Certificate Computer Science (OL + HL) + Junior Cycle Coding short course.

    **YOUR EXPERTISE:** All LC-COMP-LO-* + JC-CODING-*; algorithms,
    data structures, Python programming, computational thinking,
    computer systems, networks, databases, web development, data
    representation, ethics.

    **AVAILABLE TOOLS:** comp_syllabus_lookup_tool, comp_past_paper_lookup_tool,
    comp_marking_scheme_lookup_tool, comp_formative_item_generate_tool,
    comp_response_score_tool

    **TEACHING APPROACH:**
    1. Cite the NCCA LO code.
    2. For code items, run the code mentally + check correctness.
    3. For algorithm items, trace through with sample inputs.
    4. 4 graduated hints.
    5. Encourage the student.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Go n-éirí an t-ádh leat!
    """,
    tools=[comp_syllabus_tool, comp_past_paper_tool, comp_marking_scheme_tool, comp_formative_item_tool, comp_response_score_tool],
    output_key="comp_response",
)


# ---------------------------------------------------------------------------
# Feat C wire-up — module-level handles (LlmAgent is a Pydantic model).
# ---------------------------------------------------------------------------


async def comp_agent_emit_to_cognee(response: str, query: str) -> list[str]:
    return await emit_to_cognee(_COMP_WIRING, response, query)


def comp_agent_open_trace(verb: str = "explain", **kw: object) -> object:
    return open_langfuse_trace(_COMP_WIRING, verb=verb, **kw)


comp_agent_baml_quest_pack_fn = resolve_baml_function(
    _COMP_WIRING, "QuestPack"
)
comp_agent_baml_formative_item_fn = resolve_baml_function(
    _COMP_WIRING, "FormativeItem"
)


# ---------------------------------------------------------------------------
# BIEP v1 (2026-07-16): per-subject workflow handlers.
# ---------------------------------------------------------------------------

comp_agent_workflow_handlers = build_subject_workflow_handlers(
    wiring=_COMP_WIRING,
    syllabus_lookup_fn=comp_syllabus_lookup_tool,
    past_paper_lookup_fn=comp_past_paper_lookup_tool,
    marking_scheme_lookup_fn=comp_marking_scheme_lookup_tool,
    formative_item_fn=comp_formative_item_generate_tool,
    response_score_fn=comp_response_score_tool,
)


async def make_study_plan_handler(
    ctx: StudyPlanContext | None = None,
) -> dict[str, object]:
    """BIEP v1 per-subject study-plan handler (NCCA Computer Science)."""
    return await comp_agent_workflow_handlers.study_plan(
        ctx if ctx is not None else StudyPlanContext()
    )


async def discuss_exam_paper_handler(exam_paper_id: str) -> dict[str, object]:
    """BIEP v1 per-subject exam-paper-discussion handler (NCCA Computer Science)."""
    return await comp_agent_workflow_handlers.exam_paper(exam_paper_id)


async def explain_marking_scheme_handler(
    marking_scheme_id: str,
) -> dict[str, object]:
    """BIEP v1 per-subject marking-scheme-explanation handler (NCCA Computer Science)."""
    return await comp_agent_workflow_handlers.marking_scheme(marking_scheme_id)


comp_agent_wire = attach_subject_workflow_handlers(
    wire_subject_agent(_COMP_WIRING),
    comp_agent_workflow_handlers,
)