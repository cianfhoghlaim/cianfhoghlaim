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


# Gaeilge-specific tools (5 minimum)
async def gael_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"lo_code": f"LC-GAEL-LO-{hash(topic) % 100}", "topic": topic, "competency_text_ga": f"Sample LO for {topic}"}]


async def gael_past_paper_lookup_tool(topic: str, level: str = "lc_hl", year: int | None = None) -> list[dict]:
    return [{"item_id": f"item-{hash(topic) % 100}", "text_ga": f"Sample question for {topic}", "level": level}]


async def gael_gramadach_review_tool(gramadach_topic: str) -> dict:
    return {"topic": gramadach_topic, "explanation_ga": f"Míniú ar an ghramadach: {gramadach_topic}"}


async def gael_formative_item_generate_tool(
    lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = ""
) -> dict:
    return {"id": f"gae-{lo_code}-{difficulty}", "prompt_ga": f"Ceist samplach do {lo_code}", "lo_code": lo_code}


async def gael_response_score_tool(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict:
    return {"item_id": item_id, "marks_awarded": 5, "total_marks": 10, "partial_credit_pct": 50, "feedback_ga": "Maith an iarracht!"}


gael_syllabus_tool = FunctionTool(func=gael_syllabus_lookup_tool)
gael_past_paper_tool = FunctionTool(func=gael_past_paper_lookup_tool)
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
    3. gael_gramadach_review_tool - Grammar review + conjugation tables
    4. gael_formative_item_generate_tool - Generate Irish-medium items
    5. gael_response_score_tool - Score attempts (Irish feedback canonical)

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
        gael_gramadach_tool,
        gael_formative_item_tool,
        gael_response_score_tool,
    ],
    output_key="gael_response",
)