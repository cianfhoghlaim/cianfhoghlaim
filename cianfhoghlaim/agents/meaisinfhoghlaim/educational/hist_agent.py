"""
History Specialist Agent (hist_agent) — Cianfhoghlaim Educational MMO.
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config


async def hist_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"lo_code": f"LC-HIST-LO-{hash(topic) % 100}", "topic": topic}]


async def hist_past_paper_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"item_id": f"hist-{hash(topic) % 100}", "text": f"Sample History question for {topic}"}]


async def hist_marking_scheme_lookup_tool(lo_code: str) -> dict:
    return {"lo_code": lo_code, "text_en": f"Marking scheme for {lo_code}"}


async def hist_formative_item_generate_tool(
    lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = ""
) -> dict:
    return {"id": f"hist-{lo_code}-{difficulty}", "prompt_en": f"Sample History question for {lo_code}", "lo_code": lo_code}


async def hist_response_score_tool(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict:
    return {"item_id": item_id, "marks_awarded": 5, "total_marks": 10, "partial_credit_pct": 50}


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
    You are the History Specialist Agent for the Cianfhoghlaim
    Educational MMO. You teach NCCA Leaving Certificate History (OL + HL)
    + Junior Cycle History.

    **YOUR EXPERTISE:**
    - All LC-HIST-LO-* learning outcomes (OL + HL)
    - All JC-HISTORY-LO-* learning outcomes (Junior Cycle)
    - Past paper patterns (ALP for HL, GLP for OL)
    - Document-based questions, essay prompts, source comparison
    - Early Modern Ireland, Modern Ireland, European History,
      World History, Research Study, Document Study

    **AVAILABLE TOOLS:**
    1. hist_syllabus_lookup_tool - Find NCCA learning outcomes
    2. hist_past_paper_lookup_tool - Find past paper questions
    3. hist_marking_scheme_lookup_tool - Get marking schemes
    4. hist_formative_item_generate_tool - Generate formative items
    5. hist_response_score_tool - Score student attempts

    **TEACHING APPROACH:**
    1. Always cite the NCCA LO code (e.g. "LC-HIST-LO-2.4").
    2. For document-based questions, focus on SOAP (Subject, Occasion,
       Audience, Purpose) + inference + evaluation.
    3. For essay prompts, structure as PEE (Point, Evidence, Explanation).
    4. Use 4 graduated hints (Level 1 nudge → Level 4 step-by-step).
    5. Encourage the student. History rewards clear thinking.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Go n-éirí an t-ádh leat!
    """,
    tools=[
        hist_syllabus_tool,
        hist_past_paper_tool,
        hist_marking_scheme_tool,
        hist_formative_item_tool,
        hist_response_score_tool,
    ],
    output_key="hist_response",
)