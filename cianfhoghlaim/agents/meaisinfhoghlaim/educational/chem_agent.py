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


async def chem_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"lo_code": f"LC-CHEM-LO-{hash(topic) % 100}", "topic": topic}]


async def chem_past_paper_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"item_id": f"chem-{hash(topic) % 100}", "text": f"Sample Chemistry question for {topic}"}]


async def chem_marking_scheme_lookup_tool(lo_code: str) -> dict:
    return {"lo_code": lo_code, "text_en": f"Marking scheme for {lo_code}"}


async def chem_formative_item_generate_tool(
    lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = ""
) -> dict:
    return {"id": f"chem-{lo_code}-{difficulty}", "prompt_en": f"Sample chemistry question for {lo_code}", "lo_code": lo_code}


async def chem_response_score_tool(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict:
    return {"item_id": item_id, "marks_awarded": 5, "total_marks": 10, "partial_credit_pct": 50}


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