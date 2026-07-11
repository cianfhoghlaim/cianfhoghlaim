"""
Chemistry Specialist Agent (chem_agent) — Cianfhoghlaim Educational MMO.

One of 8 NCCA subject agents. Specialised for Leaving Certificate
Chemistry (OL + HL) + Junior Cycle Science.
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config
from .tools.chem_syllabus_lookup import lookup_chem_lo
from .tools.chem_past_paper_lookup import lookup_chem_paper
from .tools.chem_marking_scheme_lookup import lookup_chem_marking_scheme
from .tools.chem_formative_item_generate import generate_chem_item
from .tools.chem_response_score import score_chem_response

# Feat C (2026-07-10): StorageBackend Protocol + Langfuse + Cognee + BAML.
from .wiring import (
    emit_to_cognee,
    get_wiring,
    open_langfuse_trace,
    resolve_baml_function,
    wire_subject_agent,
)

# BIEP v1 (2026-07-16): the 3 per-subject workflow handlers
# (study plan + exam paper discussion + marking scheme explanation)
# for the NCCA Chemistry agent.
from ._workflow_handlers import (
    StudyPlanContext,
    attach_subject_workflow_handlers,
    build_subject_workflow_handlers,
)

_CHEM_WIRING = get_wiring("chemistry")


async def chem_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    try:
        return await lookup_chem_lo(topic=topic, level=level, language="en", limit=10)
    except Exception:
        return []


async def chem_past_paper_lookup_tool(topic: str, level: str = "lc_hl", year: int | None = None) -> list[dict]:
    try:
        return await lookup_chem_paper(topic=topic, level=level, year=year, limit=5)
    except Exception:
        return []


async def chem_marking_scheme_lookup_tool(lo_code: str) -> dict:
    try:
        return await lookup_chem_marking_scheme(lo_code=lo_code)
    except Exception:
        return {"error": "marking scheme lookup failed"}


async def chem_formative_item_generate_tool(
    lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = ""
) -> dict:
    try:
        return await generate_chem_item(
            lo_code=lo_code, difficulty=difficulty, level=level, topic=topic
        )
    except Exception as exc:
        return {"error": f"Item generation failed: {exc}"}


async def chem_response_score_tool(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict:
    try:
        return await score_chem_response(
            item_id=item_id,
            student_response=student_response,
            response_format=response_format,
            time_taken_seconds=time_taken_seconds,
            hints_used=hints_used,
        )
    except Exception as exc:
        return {"error": f"Scoring failed: {exc}"}


chem_syllabus_tool = FunctionTool(func=chem_syllabus_lookup_tool)
chem_past_paper_tool = FunctionTool(func=chem_past_paper_lookup_tool)
chem_marking_scheme_tool = FunctionTool(func=chem_marking_scheme_lookup_tool)
chem_formative_item_tool = FunctionTool(func=chem_formative_item_generate_tool)
chem_response_score_tool = FunctionTool(func=chem_response_score_tool)


chem_agent = LlmAgent(
    name="chem_agent",
    model=config.worker_model,
    description=(
        "Chemistry specialist agent for NCCA Leaving Certificate Chemistry "
        "(OL + HL) + Junior Cycle Science. Atomic structure, bonding, "
        "stoichiometry, acids/bases, organic, thermodynamics, electrochemistry."
    ),
    instruction=f"""
    You are the Chemistry Specialist Agent for the Cianfhoghlaim
    Educational MMO. You teach NCCA Leaving Certificate Chemistry (OL + HL)
    + Junior Cycle Science.

    **YOUR EXPERTISE:**
    - All LC-CHEM-LO-* learning outcomes (OL + HL)
    - All JC-SCIENCE-LO-* learning outcomes (Junior Cycle)
    - Past paper patterns (ALP for HL, GLP for OL)
    - The 22 mandatory practical experiments (LC Chemistry)
    - Atomic structure, bonding, stoichiometry, acids/bases,
      organic chemistry, thermodynamics, electrochemistry,
      equilibria, rates of reaction, water chemistry, periodic table
    - Cross-subject bridge to Mathematics (calculus for kinetics) and
      Physics (atomic structure, waves for spectroscopy)

    **AVAILABLE TOOLS:**
    1. chem_syllabus_lookup_tool - Find NCCA learning outcomes
    2. chem_past_paper_lookup_tool - Find past paper questions
    3. chem_marking_scheme_lookup_tool - Get marking schemes
    4. chem_formative_item_generate_tool - Generate formative items
    5. chem_response_score_tool - Score student attempts

    **TEACHING APPROACH:**
    1. Always cite the NCCA LO code (e.g. "LC-CHEM-LO-2.4").
    2. Provide step-by-step worked solutions with marking-scheme
       alignment: which step earns which mark.
    3. Use 4 graduated hints (Level 1 nudge → Level 4 step-by-step).
    4. Reference the 22 mandatory practicals where relevant.
    5. Encourage the student. Chemistry has many abstract concepts.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Go n-éirí an t-ádh leat!
    """,
    tools=[
        chem_syllabus_tool,
        chem_past_paper_tool,
        chem_marking_scheme_tool,
        chem_formative_item_tool,
        chem_response_score_tool,
    ],
    output_key="chem_response",
)


# ---------------------------------------------------------------------------
# Feat C wire-up — module-level handles (LlmAgent is a Pydantic model).
# ---------------------------------------------------------------------------


async def chem_agent_emit_to_cognee(response: str, query: str) -> list[str]:
    return await emit_to_cognee(_CHEM_WIRING, response, query)


def chem_agent_open_trace(verb: str = "explain", **kw: object) -> object:
    return open_langfuse_trace(_CHEM_WIRING, verb=verb, **kw)


chem_agent_baml_quest_pack_fn = resolve_baml_function(
    _CHEM_WIRING, "QuestPack"
)
chem_agent_baml_formative_item_fn = resolve_baml_function(
    _CHEM_WIRING, "FormativeItem"
)


# ---------------------------------------------------------------------------
# BIEP v1 (2026-07-16): per-subject workflow handlers — bind the 3
# handlers (study plan + exam paper + marking scheme) to the per-
# subject wiring + tool callables, then attach them to the WireSubjectAgent
# via ``attach_subject_workflow_handlers``.  Module-level handles
# are exposed for the lifecycle tests.
# ---------------------------------------------------------------------------

chem_agent_workflow_handlers = build_subject_workflow_handlers(
    wiring=_CHEM_WIRING,
    syllabus_lookup_fn=chem_syllabus_lookup_tool,
    past_paper_lookup_fn=chem_past_paper_lookup_tool,
    marking_scheme_lookup_fn=chem_marking_scheme_lookup_tool,
    formative_item_fn=chem_formative_item_generate_tool,
    response_score_fn=chem_response_score_tool,
)


async def make_study_plan_handler(
    ctx: StudyPlanContext | None = None,
) -> dict[str, object]:
    """BIEP v1 per-subject study-plan handler (NCCA Chemistry)."""
    return await chem_agent_workflow_handlers.study_plan(
        ctx if ctx is not None else StudyPlanContext()
    )


async def discuss_exam_paper_handler(exam_paper_id: str) -> dict[str, object]:
    """BIEP v1 per-subject exam-paper-discussion handler (NCCA Chemistry)."""
    return await chem_agent_workflow_handlers.exam_paper(exam_paper_id)


async def explain_marking_scheme_handler(
    marking_scheme_id: str,
) -> dict[str, object]:
    """BIEP v1 per-subject marking-scheme-explanation handler (NCCA Chemistry)."""
    return await chem_agent_workflow_handlers.marking_scheme(marking_scheme_id)


chem_agent_wire = attach_subject_workflow_handlers(
    wire_subject_agent(_CHEM_WIRING),
    chem_agent_workflow_handlers,
)