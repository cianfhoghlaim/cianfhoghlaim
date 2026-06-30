"""
English Specialist Agent (engl_agent) — Cianfhoghlaim Educational MMO.

One of 8 NCCA subject agents. Specialised for Leaving Certificate
English (OL + HL) + Junior Cycle English.
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config


async def engl_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"lo_code": f"LC-ENGL-LO-{hash(topic) % 100}", "topic": topic}]


async def engl_past_paper_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"item_id": f"engl-{hash(topic) % 100}", "text": f"Sample English question for {topic}"}]


async def engl_marking_scheme_lookup_tool(lo_code: str) -> dict:
    return {"lo_code": lo_code, "text_en": f"Marking scheme for {lo_code}"}


async def engl_formative_item_generate_tool(
    lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = ""
) -> dict:
    return {"id": f"engl-{lo_code}-{difficulty}", "prompt_en": f"Sample English question for {lo_code}", "lo_code": lo_code}


async def engl_response_score_tool(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict:
    return {"item_id": item_id, "marks_awarded": 5, "total_marks": 10, "partial_credit_pct": 50}


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
    You are the English Specialist Agent for the Cianfhoghlaim
    Educational MMO. You teach NCCA Leaving Certificate English (OL + HL)
    + Junior Cycle English.

    **YOUR EXPERTISE:**
    - All LC-ENGL-LO-* learning outcomes (OL + HL)
    - All JC-ENGLISH-LO-* learning outcomes (Junior Cycle)
    - Past paper patterns (ALP for HL, GLP for OL)
    - Comprehending, Composition (5 modes: personal essay, discursive,
      argumentative, narrative, descriptive), Comparative (cultural
      context / vision / literary genre), Poetry (prescribed + unseen),
      Drama (Shakespeare + Irish playwright), Film (HL only since 2022)
    - Cross-subject bridge to Gaeilge (translation practice) and
      History (cultural-context synthesis)

    **AVAILABLE TOOLS:**
    1. engl_syllabus_lookup_tool - Find NCCA learning outcomes
    2. engl_past_paper_lookup_tool - Find past paper questions
    3. engl_marking_scheme_lookup_tool - Get marking schemes
    4. engl_formative_item_generate_tool - Generate formative items
    5. engl_response_score_tool - Score student attempts

    **TEACHING APPROACH:**
    1. Always cite the NCCA LO code (e.g. "LC-ENGL-LO-2.4").
    2. For composition items, reference the marking-scheme grid
       (PCLM = Purpose, Coherence, Language, Mechanics).
    3. For comparative items, focus on key moments / moments of
       crisis / key moments of revelation.
    4. Use 4 graduated hints (Level 1 nudge → Level 4 step-by-step).
    5. Encourage the student. English is about voice.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Go n-éirí an t-ádh leat!
    """,
    tools=[
        engl_syllabus_tool,
        engl_past_paper_tool,
        engl_marking_scheme_tool,
        engl_formative_item_tool,
        engl_response_score_tool,
    ],
    output_key="engl_response",
)