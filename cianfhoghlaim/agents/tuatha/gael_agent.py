"""
Gaeilge Specialist Agent (gael_agent) — Cianfhoghlaim Educational MMO.

One of 8 NCCA subject agents. Specialised for Irish-language teaching:
text_ga is canonical, text_en is optional helper translation. The
agent's primary model is an Irish-medium fine-tuned LLM.

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
    cianfhoghlaim/baml/qpack_gaeilge.baml
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config
from .tools.gael_syllabus_lookup import lookup_gael_lo
from .tools.gael_past_paper_lookup import lookup_gael_paper
from .tools.gael_marking_scheme_lookup import lookup_gael_marking_scheme
from .tools.gael_gramadach_review import lookup_gael_gramadach
from .tools.gael_formative_item_generate import generate_gael_item
from .tools.gael_response_score import score_gael_response

# Feat C (2026-07-10): wire the StorageBackend Protocol + Langfuse
# tracer + Cognee emit hook + BAML function lookup at agent-
# construction time.  See `cianfhoghlaim/agents/tuatha/wiring.py`.
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

_GAEL_WIRING = get_wiring("gaeilge")


async def gael_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    try:
        return await lookup_gael_lo(topic=topic, level=level, language="ga", limit=10)
    except Exception:
        return []


async def gael_past_paper_lookup_tool(topic: str, level: str = "lc_hl", year: int | None = None) -> list[dict]:
    try:
        return await lookup_gael_paper(topic=topic, level=level, year=year, limit=5)
    except Exception:
        return []


async def gael_marking_scheme_lookup_tool(lo_code: str) -> dict:
    try:
        return await lookup_gael_marking_scheme(lo_code=lo_code)
    except Exception:
        return {"error": "marking scheme lookup failed"}


async def gael_gramadach_review_tool(gramadach_topic: str) -> dict:
    try:
        return await lookup_gael_gramadach(gramadach_topic)
    except Exception:
        return {"topic": gramadach_topic, "error": "gramadach review failed"}


async def gael_formative_item_generate_tool(
    lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = ""
) -> dict:
    try:
        return await generate_gael_item(
            lo_code=lo_code, difficulty=difficulty, level=level, topic=topic
        )
    except Exception as exc:
        return {"error": f"Item generation failed: {exc}"}


async def gael_response_score_tool(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict:
    try:
        return await score_gael_response(
            item_id=item_id,
            student_response=student_response,
            response_format=response_format,
            time_taken_seconds=time_taken_seconds,
            hints_used=hints_used,
        )
    except Exception as exc:
        return {"error": f"Scoring failed: {exc}"}


gael_syllabus_tool = FunctionTool(func=gael_syllabus_lookup_tool)
gael_past_paper_tool = FunctionTool(func=gael_past_paper_lookup_tool)
gael_marking_scheme_tool = FunctionTool(func=gael_marking_scheme_lookup_tool)
gael_gramadach_tool = FunctionTool(func=gael_gramadach_review_tool)
gael_formative_item_tool = FunctionTool(func=gael_formative_item_generate_tool)
gael_response_score_tool = FunctionTool(func=gael_response_score_tool)


gael_agent = LlmAgent(
    name="gael_agent",
    model=config.worker_model,
    description=(
        "Gaeilge specialist agent for NCCA Leaving Certificate + Junior "
        "Cycle Irish. All content is canonical in Irish (text_ga); "
        "text_en is optional helper translation. 3 NCCA levels (FL / OL / HL)."
    ),
    instruction=f"""
    You are the Gaeilge Specialist Agent for the Cianfhoghlaim
    Educational MMO. You teach NCCA Gaeilge (Irish) — at Leaving
    Certificate (Foundation, Ordinary, Higher) and Junior Cycle.

    **YOUR EXPERTISE:**
    - All LC-GAEL-LO-* + JC-GAEL-LO-* learning outcomes
    - Léamhthuiscint, Litríocht, Filíocht, Gramadach, Prós, Béaloideas
    - Scríbhneoireacht (composition) at 3 levels
    - Cluastuiscint (listening comprehension, aural exam component)
    - Past paper patterns (ALP / GLP / BLP)
    - Bilingual scaffolding: English explanation → Irish application

    **AVAILABLE TOOLS:**
    1. gael_syllabus_lookup_tool - Find NCCA learning outcomes (Irish)
    2. gael_past_paper_lookup_tool - Find past paper questions
    3. gael_marking_scheme_lookup_tool - Get the marking scheme
    4. gael_gramadach_review_tool - Grammar review (réimíreanna, aimsirí, séimhiú, urú)
    5. gael_formative_item_generate_tool - Generate Irish-medium items
    6. gael_response_score_tool - Score attempts (Irish feedback canonical)

    **TEACHING APPROACH:**
    1. **Always cite the LO code** (e.g. "LC-GAEL-LO-3.1").
    2. **Primary feedback is in Irish (text_ga canonical)**. text_en
       is optional — only when it adds pedagogical value (e.g. for
       parents or non-Irish-speaking teachers).
    3. **Use 4 graduated hints in Irish** (Level 1 nudge →
       Level 4 step-by-step).
    4. **Reference the prescribed literature** (e.g. filí móra:
       Aogán Ó Rathaille, Máire Mhac an tSaoi, Nuala Ní Dhomhnaill).
    5. **Encourage Irish-medium conversation** even outside
       class. Praise the student's attempts in Irish.
    6. **Grammar feedback is specific** — name the rule (réimír,
       séimhiú, urú, aimsir chaite, etc.).

    **TONE:**
    - Friendly, encouraging, Gaeilge-medium
    - Use "Maith an iarracht!" (well done) liberally
    - Celebrate small wins — Irish is hard

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Go n-éirí an t-ádh leat!
    """,
    tools=[
        gael_syllabus_tool,
        gael_past_paper_tool,
        gael_marking_scheme_tool,
        gael_gramadach_tool,
        gael_formative_item_tool,
        gael_response_score_tool,
    ],
    output_key="gael_response",
)


# ---------------------------------------------------------------------------
# Feat C wire-up — module-level handles (the LlmAgent is a Pydantic
# model so we cannot attach arbitrary attributes to it directly).
# The lifecycle tests in `tests/test_subject_router_smoke.py` read
# these module-level names.
# ---------------------------------------------------------------------------


async def gael_agent_emit_to_cognee(response: str, query: str) -> list[str]:
    """Push ``response`` to the Gaeilge Cognee dataset
    ``oideachais_lc_gaeilge`` and return closest historical hits.
    """
    return await emit_to_cognee(_GAEL_WIRING, response, query)


def gael_agent_open_trace(verb: str = "explain", **kw: object) -> object:
    """Open a Langfuse trace (``agent.gael.<verb>``) for invocation."""
    return open_langfuse_trace(_GAEL_WIRING, verb=verb, **kw)


gael_agent_baml_quest_pack_fn = resolve_baml_function(
    _GAEL_WIRING, "QuestPack"
)
gael_agent_baml_formative_item_fn = resolve_baml_function(
    _GAEL_WIRING, "FormativeItem"
)


# ---------------------------------------------------------------------------
# BIEP v1 (2026-07-16): per-subject workflow handlers.
# ---------------------------------------------------------------------------

gael_agent_workflow_handlers = build_subject_workflow_handlers(
    wiring=_GAEL_WIRING,
    syllabus_lookup_fn=gael_syllabus_lookup_tool,
    past_paper_lookup_fn=gael_past_paper_lookup_tool,
    marking_scheme_lookup_fn=gael_marking_scheme_lookup_tool,
    formative_item_fn=gael_formative_item_generate_tool,
    response_score_fn=gael_response_score_tool,
)


async def make_study_plan_handler(
    ctx: StudyPlanContext | None = None,
) -> dict[str, object]:
    """BIEP v1 per-subject study-plan handler (NCCA Gaeilge)."""
    return await gael_agent_workflow_handlers.study_plan(
        ctx if ctx is not None else StudyPlanContext()
    )


async def discuss_exam_paper_handler(exam_paper_id: str) -> dict[str, object]:
    """BIEP v1 per-subject exam-paper-discussion handler (NCCA Gaeilge)."""
    return await gael_agent_workflow_handlers.exam_paper(exam_paper_id)


async def explain_marking_scheme_handler(
    marking_scheme_id: str,
) -> dict[str, object]:
    """BIEP v1 per-subject marking-scheme-explanation handler (NCCA Gaeilge)."""
    return await gael_agent_workflow_handlers.marking_scheme(marking_scheme_id)


gael_agent_wire = attach_subject_workflow_handlers(
    wire_subject_agent(_GAEL_WIRING),
    gael_agent_workflow_handlers,
)