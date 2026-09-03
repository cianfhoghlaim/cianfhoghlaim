"""
English Specialist Agent (engl_agent) — Cianfhoghlaim Educational MMO.
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config
from .tools.engl_tools import (
    lookup_engl_lo,
    lookup_engl_paper,
    lookup_engl_marking_scheme,
    generate_engl_item,
    score_engl_response,
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

_ENGL_WIRING = get_wiring("english")


async def engl_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    try:
        return await lookup_engl_lo(topic=topic, level=level, language="en", limit=10)
    except Exception:
        return []


async def engl_past_paper_lookup_tool(topic: str, level: str = "lc_hl", year: int | None = None) -> list[dict]:
    try:
        return await lookup_engl_paper(topic=topic, level=level, year=year, limit=5)
    except Exception:
        return []


async def engl_marking_scheme_lookup_tool(lo_code: str) -> dict:
    try:
        return await lookup_engl_marking_scheme(lo_code=lo_code)
    except Exception:
        return {"error": "marking scheme lookup failed"}


async def engl_formative_item_generate_tool(lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = "") -> dict:
    try:
        return await generate_engl_item(lo_code=lo_code, difficulty=difficulty, level=level, topic=topic)
    except Exception as exc:
        return {"error": f"Item generation failed: {exc}"}


async def engl_response_score_tool(item_id: str, student_response: str, response_format: str = "text", time_taken_seconds: int = 0, hints_used: int = 0) -> dict:
    try:
        return await score_engl_response(item_id=item_id, student_response=student_response, response_format=response_format, time_taken_seconds=time_taken_seconds, hints_used=hints_used)
    except Exception as exc:
        return {"error": f"Scoring failed: {exc}"}


engl_syllabus_tool = FunctionTool(func=engl_syllabus_lookup_tool)
engl_past_paper_tool = FunctionTool(func=engl_past_paper_lookup_tool)
engl_marking_scheme_tool = FunctionTool(func=engl_marking_scheme_lookup_tool)
engl_formative_item_tool = FunctionTool(func=engl_formative_item_generate_tool)
engl_response_score_tool = FunctionTool(func=engl_response_score_tool)


engl_agent = LlmAgent(
    name="engl_agent",
    model=config.worker_model,
    description=(
        "English specialist agent for NCCA Leaving Certificate English "
        "(OL + HL) + Junior Cycle English. Comprehending, composition, "
        "comparative, poetry, drama, film."
    ),
    instruction=f"""
    You are the English Specialist Agent for the Cianfhoghlaim Educational MMO.
    You teach NCCA Leaving Certificate English (OL + HL) + Junior Cycle English.

    **YOUR EXPERTISE:** All LC-ENGL-LO-* + JC-ENGLISH-LO-*; comprehending,
    composition (5 modes), comparative, poetry (prescribed + unseen),
    drama, film (HL).

    **AVAILABLE TOOLS:** engl_syllabus_lookup_tool, engl_past_paper_lookup_tool,
    engl_marking_scheme_lookup_tool, engl_formative_item_generate_tool,
    engl_response_score_tool

    **TEACHING APPROACH:**
    1. Cite the NCCA LO code.
    2. For composition items, reference the PCLM marking grid.
    3. For comparative items, focus on key moments.
    4. 4 graduated hints.
    5. Encourage the student.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Go n-éirí an t-ádh leat!
    """,
    tools=[engl_syllabus_tool, engl_past_paper_tool, engl_marking_scheme_tool, engl_formative_item_tool, engl_response_score_tool],
    output_key="engl_response",
)


# ---------------------------------------------------------------------------
# Feat C wire-up — module-level handles (LlmAgent is a Pydantic model).
# ---------------------------------------------------------------------------


async def engl_agent_emit_to_cognee(response: str, query: str) -> list[str]:
    return await emit_to_cognee(_ENGL_WIRING, response, query)


def engl_agent_open_trace(verb: str = "explain", **kw: object) -> object:
    return open_langfuse_trace(_ENGL_WIRING, verb=verb, **kw)


engl_agent_baml_quest_pack_fn = resolve_baml_function(
    _ENGL_WIRING, "QuestPack"
)
engl_agent_baml_formative_item_fn = resolve_baml_function(
    _ENGL_WIRING, "FormativeItem"
)


# ---------------------------------------------------------------------------
# BIEP v1 (2026-07-16): per-subject workflow handlers.
# ---------------------------------------------------------------------------

engl_agent_workflow_handlers = build_subject_workflow_handlers(
    wiring=_ENGL_WIRING,
    syllabus_lookup_fn=engl_syllabus_lookup_tool,
    past_paper_lookup_fn=engl_past_paper_lookup_tool,
    marking_scheme_lookup_fn=engl_marking_scheme_lookup_tool,
    formative_item_fn=engl_formative_item_generate_tool,
    response_score_fn=engl_response_score_tool,
)


async def make_study_plan_handler(
    ctx: StudyPlanContext | None = None,
) -> dict[str, object]:
    """BIEP v1 per-subject study-plan handler (NCCA English)."""
    return await engl_agent_workflow_handlers.study_plan(
        ctx if ctx is not None else StudyPlanContext()
    )


async def discuss_exam_paper_handler(exam_paper_id: str) -> dict[str, object]:
    """BIEP v1 per-subject exam-paper-discussion handler (NCCA English)."""
    return await engl_agent_workflow_handlers.exam_paper(exam_paper_id)


async def explain_marking_scheme_handler(
    marking_scheme_id: str,
) -> dict[str, object]:
    """BIEP v1 per-subject marking-scheme-explanation handler (NCCA English)."""
    return await engl_agent_workflow_handlers.marking_scheme(marking_scheme_id)


engl_agent_wire = attach_subject_workflow_handlers(
    wire_subject_agent(_ENGL_WIRING),
    engl_agent_workflow_handlers,
)