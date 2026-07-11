"""
Geography Specialist Agent (geog_agent) — Cianfhoghlaim Educational MMO.
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config
from .tools.geog_tools import (
    lookup_geog_lo,
    lookup_geog_paper,
    lookup_geog_marking_scheme,
    generate_geog_item,
    score_geog_response,
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

_GEOG_WIRING = get_wiring("geography")


async def geog_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    try:
        return await lookup_geog_lo(topic=topic, level=level, language="en", limit=10)
    except Exception:
        return []


async def geog_past_paper_lookup_tool(topic: str, level: str = "lc_hl", year: int | None = None) -> list[dict]:
    try:
        return await lookup_geog_paper(topic=topic, level=level, year=year, limit=5)
    except Exception:
        return []


async def geog_marking_scheme_lookup_tool(lo_code: str) -> dict:
    try:
        return await lookup_geog_marking_scheme(lo_code=lo_code)
    except Exception:
        return {"error": "marking scheme lookup failed"}


async def geog_formative_item_generate_tool(lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = "") -> dict:
    try:
        return await generate_geog_item(lo_code=lo_code, difficulty=difficulty, level=level, topic=topic)
    except Exception as exc:
        return {"error": f"Item generation failed: {exc}"}


async def geog_response_score_tool(item_id: str, student_response: str, response_format: str = "text", time_taken_seconds: int = 0, hints_used: int = 0) -> dict:
    try:
        return await score_geog_response(item_id=item_id, student_response=student_response, response_format=response_format, time_taken_seconds=time_taken_seconds, hints_used=hints_used)
    except Exception as exc:
        return {"error": f"Scoring failed: {exc}"}


geog_syllabus_tool = FunctionTool(func=geog_syllabus_lookup_tool)
geog_past_paper_tool = FunctionTool(func=geog_past_paper_lookup_tool)
geog_marking_scheme_tool = FunctionTool(func=geog_marking_scheme_lookup_tool)
geog_formative_item_tool = FunctionTool(func=geog_formative_item_generate_tool)
geog_response_score_tool = FunctionTool(func=geog_response_score_tool)


geog_agent = LlmAgent(
    name="geog_agent",
    model=config.worker_model,
    description=(
        "Geography specialist agent for NCCA Leaving Certificate Geography "
        "(OL + HL) + Junior Cycle Geography. Physical + regional + human "
        "geography; map interpretation; fieldwork."
    ),
    instruction=f"""
    You are the Geography Specialist Agent for the Cianfhoghlaim Educational MMO.
    You teach NCCA Leaving Certificate Geography (OL + HL) + Junior Cycle Geography.

    **YOUR EXPERTISE:** All LC-GEOG-LO-* + JC-GEOGRAPHY-LO-*; physical (rivers,
    coasts, climate, biomes), regional (Ireland, Europe, sub-continent,
    global), human (population, urban, economic), geoecology + fieldwork.

    **AVAILABLE TOOLS:** geog_syllabus_lookup_tool, geog_past_paper_lookup_tool,
    geog_marking_scheme_lookup_tool, geog_formative_item_generate_tool,
    geog_response_score_tool

    **TEACHING APPROACH:**
    1. Cite the NCCA LO code.
    2. For OS map skills, focus on grid references, symbols, scale.
    3. For fieldwork, emphasize the investigative process.
    4. 4 graduated hints.
    5. Encourage the student.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Go n-éirí an t-ádh leat!
    """,
    tools=[geog_syllabus_tool, geog_past_paper_tool, geog_marking_scheme_tool, geog_formative_item_tool, geog_response_score_tool],
    output_key="geog_response",
)


# ---------------------------------------------------------------------------
# Feat C wire-up — module-level handles (LlmAgent is a Pydantic model).
# ---------------------------------------------------------------------------


async def geog_agent_emit_to_cognee(response: str, query: str) -> list[str]:
    return await emit_to_cognee(_GEOG_WIRING, response, query)


def geog_agent_open_trace(verb: str = "explain", **kw: object) -> object:
    return open_langfuse_trace(_GEOG_WIRING, verb=verb, **kw)


geog_agent_baml_quest_pack_fn = resolve_baml_function(
    _GEOG_WIRING, "QuestPack"
)
geog_agent_baml_formative_item_fn = resolve_baml_function(
    _GEOG_WIRING, "FormativeItem"
)


# ---------------------------------------------------------------------------
# BIEP v1 (2026-07-16): per-subject workflow handlers.
# ---------------------------------------------------------------------------

geog_agent_workflow_handlers = build_subject_workflow_handlers(
    wiring=_GEOG_WIRING,
    syllabus_lookup_fn=geog_syllabus_lookup_tool,
    past_paper_lookup_fn=geog_past_paper_lookup_tool,
    marking_scheme_lookup_fn=geog_marking_scheme_lookup_tool,
    formative_item_fn=geog_formative_item_generate_tool,
    response_score_fn=geog_response_score_tool,
)


async def make_study_plan_handler(
    ctx: StudyPlanContext | None = None,
) -> dict[str, object]:
    """BIEP v1 per-subject study-plan handler (NCCA Geography)."""
    return await geog_agent_workflow_handlers.study_plan(
        ctx if ctx is not None else StudyPlanContext()
    )


async def discuss_exam_paper_handler(exam_paper_id: str) -> dict[str, object]:
    """BIEP v1 per-subject exam-paper-discussion handler (NCCA Geography)."""
    return await geog_agent_workflow_handlers.exam_paper(exam_paper_id)


async def explain_marking_scheme_handler(
    marking_scheme_id: str,
) -> dict[str, object]:
    """BIEP v1 per-subject marking-scheme-explanation handler (NCCA Geography)."""
    return await geog_agent_workflow_handlers.marking_scheme(marking_scheme_id)


geog_agent_wire = attach_subject_workflow_handlers(
    wire_subject_agent(_GEOG_WIRING),
    geog_agent_workflow_handlers,
)