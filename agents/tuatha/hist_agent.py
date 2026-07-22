"""
History Specialist Agent (hist_agent) — Cianfhoghlaim Educational MMO.

One of 8 NCCA subject agents. Specialised for Leaving Certificate
History (OL + HL) + Junior Cycle History.
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config
from .tools.hist_syllabus_lookup import lookup_hist_lo
from .tools.hist_past_paper_lookup import lookup_hist_paper
from .tools.hist_marking_scheme_lookup import lookup_hist_marking_scheme
from .tools.hist_formative_item_generate import generate_hist_item
from .tools.hist_response_score import score_hist_response

# Feat C (2026-07-10): StorageBackend Protocol + Langfuse tracer +
# Cognee emit hook + BAML function lookup, wired eagerly.
from .wiring import (
    emit_to_cognee,
    get_wiring,
    open_langfuse_trace,
    resolve_baml_function,
    wire_subject_agent,
)

_HIST_WIRING = get_wiring("history")


async def hist_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    try:
        return await lookup_hist_lo(topic=topic, level=level, language="en", limit=10)
    except Exception:
        return []


async def hist_past_paper_lookup_tool(topic: str, level: str = "lc_hl", year: int | None = None) -> list[dict]:
    try:
        return await lookup_hist_paper(topic=topic, level=level, year=year, limit=5)
    except Exception:
        return []


async def hist_marking_scheme_lookup_tool(lo_code: str) -> dict:
    try:
        return await lookup_hist_marking_scheme(lo_code=lo_code)
    except Exception:
        return {"error": "marking scheme lookup failed"}


async def hist_formative_item_generate_tool(lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = "") -> dict:
    try:
        return await generate_hist_item(lo_code=lo_code, difficulty=difficulty, level=level, topic=topic)
    except Exception as exc:
        return {"error": f"Item generation failed: {exc}"}


async def hist_response_score_tool(item_id: str, student_response: str, response_format: str = "text", time_taken_seconds: int = 0, hints_used: int = 0) -> dict:
    try:
        return await score_hist_response(item_id=item_id, student_response=student_response, response_format=response_format, time_taken_seconds=time_taken_seconds, hints_used=hints_used)
    except Exception as exc:
        return {"error": f"Scoring failed: {exc}"}


hist_syllabus_tool = FunctionTool(func=hist_syllabus_lookup_tool)
hist_past_paper_tool = FunctionTool(func=hist_past_paper_lookup_tool)
hist_marking_scheme_tool = FunctionTool(func=hist_marking_scheme_lookup_tool)
hist_formative_item_tool = FunctionTool(func=hist_formative_item_generate_tool)
hist_response_score_tool = FunctionTool(func=hist_response_score_tool)


hist_agent = LlmAgent(
    name="hist_agent",
    model=config.worker_model,
    description=(
        "History specialist agent for NCCA Leaving Certificate History "
        "(OL + HL) + Junior Cycle History. Document-based questions, "
        "essay prompts, source comparison."
    ),
    instruction=f"""
    You are the History Specialist Agent for the Cianfhoghlaim Educational MMO.
    You teach NCCA Leaving Certificate History (OL + HL) + Junior Cycle History.

    **YOUR EXPERTISE:**
    - All LC-HIST-LO-* learning outcomes (OL + HL)
    - All JC-HISTORY-LO-* learning outcomes (Junior Cycle)
    - Past paper patterns (ALP for HL, GLP for OL)
    - Document-based questions, essay prompts, source comparison
    - Early Modern Ireland, Modern Ireland, European History, World History

    **AVAILABLE TOOLS:** hist_syllabus_lookup_tool, hist_past_paper_lookup_tool,
    hist_marking_scheme_lookup_tool, hist_formative_item_generate_tool,
    hist_response_score_tool

    **TEACHING APPROACH:**
    1. Cite the NCCA LO code (e.g. "LC-HIST-LO-2.4").
    2. For document-based questions, focus on SOAP (Subject, Occasion, Audience, Purpose).
    3. For essay prompts, structure as PEE (Point, Evidence, Explanation).
    4. 4 graduated hints.
    5. Encourage the student.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Go n-éirí an t-ádh leat!
    """,
    tools=[hist_syllabus_tool, hist_past_paper_tool, hist_marking_scheme_tool, hist_formative_item_tool, hist_response_score_tool],
    output_key="hist_response",
)


# ---------------------------------------------------------------------------
# Feat C wire-up — module-level handles (LlmAgent is a Pydantic model).
# ---------------------------------------------------------------------------


async def hist_agent_emit_to_cognee(response: str, query: str) -> list[str]:
    return await emit_to_cognee(_HIST_WIRING, response, query)


def hist_agent_open_trace(verb: str = "explain", **kw: object) -> object:
    return open_langfuse_trace(_HIST_WIRING, verb=verb, **kw)


hist_agent_baml_quest_pack_fn = resolve_baml_function(
    _HIST_WIRING, "QuestPack"
)
hist_agent_baml_formative_item_fn = resolve_baml_function(
    _HIST_WIRING, "FormativeItem"
)


hist_agent_wire = wire_subject_agent(_HIST_WIRING)