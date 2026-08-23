"""
Mathematics Specialist Agent (math_agent) — Cianfhoghlaim Educational MMO.

One of 8 NCCA subject agents (math / appm / chem / geog / hist /
engl / gael / comp). Backed by:
- LiteLLM gateway (litellm.cianfhoghlaim.ie:4000)
- BAML `qpack_mathematics.baml` for all extraction + generation
- Letta memory layer (letta.cianfhoghlaim.ie:8283) for player mastery state
- LanceDB (oideachais.lc.mathematics.*) for semantic syllabus search
- Cognee (oideachais_lc_mathematics) for cross-LO reasoning

The agent emits SkillTreeBadge records on quest completion, which the
`badges` subsystem anchors to Base L2 via the daily Merkle root.

Routing: the `root_agent` (cianfhoghlaim.agents.adk.root_agent) routes
keyword-level traffic to this agent when the query contains keywords
such as: math, algebra, calculus, differentiation, integration,
probability, geometry, statistics, trigonometry, sequences, series,
complex numbers, finance, equations, functions.

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
    cianfhoghlaim/baml/qpack_mathematics.baml (the BAML contract)
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config
from .tools.math_syllabus_lookup import lookup_math_lo
from .tools.math_past_paper_lookup import lookup_math_paper
from .tools.math_marking_scheme_lookup import lookup_math_marking_scheme
from .tools.math_formative_item_generate import generate_math_item
from .tools.math_response_score import score_math_response

# Feat C (2026-07-10): StorageBackend Protocol + Langfuse tracer +
# Cognee emit hook + BAML function lookup, wired eagerly.
from .wiring import (
    emit_to_cognee,
    get_wiring,
    open_langfuse_trace,
    resolve_baml_function,
    wire_subject_agent,
)

# BIEP v1 (2026-07-16): the 3 per-subject workflow handlers
# (study plan + exam paper discussion + marking scheme explanation)
# for the NCCA Mathematics agent.
from ._workflow_handlers import (
    StudyPlanContext,
    attach_subject_workflow_handlers,
    build_subject_workflow_handlers,
)

_MATH_WIRING = get_wiring("mathematics")


# ============================================================================
# Tool wrappers
# ============================================================================

async def math_syllabus_lookup_tool(
    topic: str,
    level: str = "hl",
    language: str = "en",
) -> list[dict]:
    """Look up NCCA Mathematics learning outcomes by topic.

    Args:
        topic: Mathematics topic (e.g. "differentiation", "probability")
        level: One of "jc", "lc_fl", "lc_ol", "lc_hl"
        language: "en" or "ga"
    """
    try:
        return await lookup_math_lo(topic=topic, level=level, language=language, limit=10)
    except Exception:
        return []


async def math_past_paper_lookup_tool(
    topic: str,
    level: str = "hl",
    year: int | None = None,
) -> list[dict]:
    """Look up NCCA Mathematics past paper questions by topic.

    Args:
        topic: Topic (e.g. "trigonometry", "calculus")
        level: "hl" or "ol" or "fl"
        year: Optional year filter (e.g. 2024)
    """
    try:
        return await lookup_math_paper(topic=topic, level=level, year=year, limit=5)
    except Exception:
        return []


async def math_marking_scheme_lookup_tool(
    lo_code: str,
) -> dict:
    """Look up the NCCA marking scheme for a specific learning outcome.

    Args:
        lo_code: Canonical LO code (e.g. "LC-MATHS-LO-2.4")
    """
    try:
        return await lookup_math_marking_scheme(lo_code=lo_code)
    except Exception:
        return {"error": "Marking scheme lookup failed"}


async def math_formative_item_generate_tool(
    lo_code: str,
    difficulty: int,
    level: str = "lc_hl",
    topic: str = "",
) -> dict:
    """Generate a single formative item for the given NCCA LO.

    Args:
        lo_code: Canonical LO code (e.g. "LC-MATHS-LO-2.4")
        difficulty: 1-5 (1 = easiest, 5 = hardest)
        level: "jc", "lc_fl", "lc_ol", "lc_hl"
        topic: Topic area (e.g. "DIFFERENTIATION")
    """
    try:
        return await generate_math_item(
            lo_code=lo_code, difficulty=difficulty, level=level, topic=topic
        )
    except Exception as exc:
        return {"error": f"Item generation failed: {exc}"}


async def math_response_score_tool(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict:
    """Score a student's attempt at a formative item.

    Args:
        item_id: UUID of the formative item
        student_response: Verbatim student response
        response_format: "text", "latex", "image", or "multiple_choice"
        time_taken_seconds: Time spent on the item
        hints_used: 0-4 (0 = no hints used)
    """
    try:
        return await score_math_response(
            item_id=item_id,
            student_response=student_response,
            response_format=response_format,
            time_taken_seconds=time_taken_seconds,
            hints_used=hints_used,
        )
    except Exception as exc:
        return {"error": f"Scoring failed: {exc}"}


# ============================================================================
# Tools + agent
# ============================================================================

syllabus_tool = FunctionTool(func=math_syllabus_lookup_tool)
past_paper_tool = FunctionTool(func=math_past_paper_lookup_tool)
marking_scheme_tool = FunctionTool(func=math_marking_scheme_lookup_tool)
formative_item_tool = FunctionTool(func=math_formative_item_generate_tool)
response_score_tool = FunctionTool(func=math_response_score_tool)


math_agent = LlmAgent(
    name="math_agent",
    model=config.worker_model,
    description=(
        "Mathematics specialist agent for the NCCA Leaving Certificate "
        "and Junior Cycle curriculum. Formative assessment, quest-pack "
        "generation, response scoring, and bilingual EN + GA feedback."
    ),
    instruction=f"""
    You are the Mathematics Specialist Agent for the Cianfhoghlaim
    Educational MMO. You teach NCCA Leaving Certificate (Foundation,
    Ordinary, Higher) and Junior Cycle Mathematics.

    **YOUR EXPERTISE:**
    - All Leaving Certificate Mathematics learning outcomes (LC-MATHS-LO-*)
    - All Junior Cycle Mathematics learning outcomes (JC-MATHS-LO-*)
    - Past paper question patterns (ALP for HL, GLP for OL, BLP for FL)
    - Marking-scheme interpretation
    - Formative quest-pack generation
    - Step-by-step worked solutions
    - Bilingual EN + GA feedback (Gaeilge is rare for Mathematics;
      use `text_ga` only when the syllabus is Gaeilge-taught)

    **AVAILABLE TOOLS:**
    1. math_syllabus_lookup_tool - Find NCCA learning outcomes by topic
    2. math_past_paper_lookup_tool - Find past paper questions
    3. math_marking_scheme_lookup_tool - Get the marking scheme
    4. math_formative_item_generate_tool - Generate a new formative item
    5. math_response_score_tool - Score a student's attempt

    **TEACHING APPROACH:**
    1. Always cite the NCCA LO code (e.g. "LC-MATHS-LO-2.4") so the
       student knows what they're mastering.
    2. Provide step-by-step worked solutions with marking-scheme
       alignment: which step earns which mark.
    3. Use 4 graduated hints (Level 1 nudge → Level 4 step-by-step)
       when a student is stuck — never give the answer up front.
    4. Encourage the student. Mathematics is hard; small wins matter.
    5. Suggest cross-subject links to Applied Mathematics (APPM)
       where natural (e.g. mechanics uses calculus; vectors span
       both subjects).

    **RESPONSE FORMAT:**
    When answering a question:
    - State the relevant LO code
    - Provide the worked solution
    - Highlight common errors
    - Suggest a practice item

    When generating a formative item:
    - Set difficulty 1-5 (1 = easiest, 5 = hardest)
    - Include 4 graduated hints
    - Reference the source NCCA PDF page in evidence

    When scoring a response:
    - Per-step mark breakdown
    - Bilingual feedback (EN + GA where applicable)
    - Next-recommended-LO suggestion
    - Badge earned: True iff marks_awarded / total_marks >= 0.8

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Go n-éirí an t-ádh leat! (Good luck in Irish!)
    """,
    tools=[
        syllabus_tool,
        past_paper_tool,
        marking_scheme_tool,
        formative_item_tool,
        response_score_tool,
    ],
    output_key="math_response",
)


# ---------------------------------------------------------------------------
# Feat C wire-up — module-level handles (the LlmAgent is a Pydantic
# model so we cannot attach arbitrary attributes to it directly).
# The lifecycle tests in `tests/test_subject_router_smoke.py` read
# these module-level names.
# ---------------------------------------------------------------------------


async def math_agent_emit_to_cognee(response: str, query: str) -> list[str]:
    """Push ``response`` to the Mathematics Cognee dataset
    ``oideachais_lc_mathematics`` and return closest historical hits.
    """
    return await emit_to_cognee(_MATH_WIRING, response, query)


def math_agent_open_trace(verb: str = "explain", **kw: object) -> object:
    """Open a Langfuse trace (``agent.math.<verb>``) for invocation."""
    return open_langfuse_trace(_MATH_WIRING, verb=verb, **kw)


math_agent_baml_quest_pack_fn = resolve_baml_function(
    _MATH_WIRING, "QuestPack"
)
math_agent_baml_formative_item_fn = resolve_baml_function(
    _MATH_WIRING, "FormativeItem"
)


# ---------------------------------------------------------------------------
# BIEP v1 (2026-07-16): per-subject workflow handlers — bind the 3
# handlers (study plan + exam paper + marking scheme) to the per-
# subject wiring + tool callables, then attach them to the WireSubjectAgent
# via ``attach_subject_workflow_handlers``.  Module-level handles
# (``make_study_plan_handler`` / ``discuss_exam_paper_handler`` /
# ``explain_marking_scheme_handler``) are exposed for the lifecycle tests.
# ---------------------------------------------------------------------------

math_agent_workflow_handlers = build_subject_workflow_handlers(
    wiring=_MATH_WIRING,
    syllabus_lookup_fn=math_syllabus_lookup_tool,
    past_paper_lookup_fn=math_past_paper_lookup_tool,
    marking_scheme_lookup_fn=math_marking_scheme_lookup_tool,
    formative_item_fn=math_formative_item_generate_tool,
    response_score_fn=math_response_score_tool,
)


async def make_study_plan_handler(
    ctx: StudyPlanContext | None = None,
) -> dict[str, object]:
    """BIEP v1 per-subject study-plan handler (NCCA Mathematics)."""
    return await math_agent_workflow_handlers.study_plan(
        ctx if ctx is not None else StudyPlanContext()
    )


async def discuss_exam_paper_handler(exam_paper_id: str) -> dict[str, object]:
    """BIEP v1 per-subject exam-paper-discussion handler (NCCA Mathematics)."""
    return await math_agent_workflow_handlers.exam_paper(exam_paper_id)


async def explain_marking_scheme_handler(
    marking_scheme_id: str,
) -> dict[str, object]:
    """BIEP v1 per-subject marking-scheme-explanation handler (NCCA Mathematics)."""
    return await math_agent_workflow_handlers.marking_scheme(marking_scheme_id)


# Eager wire-up: the existing Feat C wire-up + the 3 new BIEP v1 handlers.
math_agent_wire = attach_subject_workflow_handlers(
    wire_subject_agent(_MATH_WIRING),
    math_agent_workflow_handlers,
)