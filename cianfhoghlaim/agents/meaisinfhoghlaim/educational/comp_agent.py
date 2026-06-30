"""
Computer Science Specialist Agent (comp_agent) — Cianfhoghlaim Educational MMO.
"""
from __future__ import annotations

import datetime
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from ..adk.tuatha_config import config


async def comp_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"lo_code": f"LC-COMP-LO-{hash(topic) % 100}", "topic": topic}]


async def comp_past_paper_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"item_id": f"comp-{hash(topic) % 100}", "text": f"Sample CS question for {topic}"}]


async def comp_marking_scheme_lookup_tool(lo_code: str) -> dict:
    return {"lo_code": lo_code, "text_en": f"Marking scheme for {lo_code}"}


async def comp_formative_item_generate_tool(lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = "") -> dict:
    return {"id": f"comp-{lo_code}-{difficulty}", "prompt_en": f"Sample CS question for {lo_code}", "lo_code": lo_code}


async def comp_response_score_tool(item_id: str, student_response: str, response_format: str = "text", time_taken_seconds: int = 0, hints_used: int = 0) -> dict:
    return {"item_id": item_id, "marks_awarded": 5, "total_marks": 10, "partial_credit_pct": 50}


comp_syllabus_tool = FunctionTool(func=comp_syllabus_lookup_tool)
comp_past_paper_tool = FunctionTool(func=comp_past_paper_lookup_tool)
comp_marking_scheme_tool = FunctionTool(func=comp_marking_scheme_lookup_tool)
comp_formative_item_tool = FunctionTool(func=comp_formative_item_generate_tool)
comp_response_score_tool = FunctionTool(func=comp_response_score_tool)


comp_agent = LlmAgent(
    name="comp_agent",
    model=config.worker_model,
    description=(
        "Computer Science specialist agent for NCCA Leaving Certificate "
        "Computer Science (OL + HL) + Junior Cycle Coding short course. "
        "Algorithms, data structures, programming (Python), computational thinking."
    ),
    instruction=f"""
    You are the Computer Science Specialist Agent for the Cianfhoghlaim Educational MMO.
    You teach NCCA Leaving Certificate Computer Science (OL + HL) + Junior Cycle Coding short course.

    **YOUR EXPERTISE:**
    - All LC-COMP-LO-* learning outcomes (OL + HL)
    - Algorithms (sorting, searching, complexity analysis)
    - Data structures (arrays, lists, stacks, queues, trees, graphs)
    - Programming (Python; variables, control flow, functions, OOP)
    - Computational thinking (decomposition, pattern recognition, abstraction)
    - Computer systems (CPU, memory, storage, OS)
    - Networks (LAN, WAN, protocols, internet)
    - Databases (SQL, normalisation, ER diagrams)
    - Web development (HTML, CSS, JavaScript basics)
    - Data representation (binary, hex, character encoding)
    - Ethics (privacy, AI ethics, IP)

    **AVAILABLE TOOLS:**
    1. comp_syllabus_lookup_tool, 2. comp_past_paper_lookup_tool,
    3. comp_marking_scheme_lookup_tool, 4. comp_formative_item_generate_tool,
    5. comp_response_score_tool

    **TEACHING APPROACH:**
    1. Cite the NCCA LO code.
    2. For code items, run the code mentally + check correctness.
    3. For algorithm items, trace through with sample inputs.
    4. 4 graduated hints.
    5. Encourage the student.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    Go n-éirí an t-ádh leat!
    """,
    tools=[comp_syllabus_tool, comp_past_paper_tool, comp_marking_scheme_tool, comp_formative_item_tool, comp_response_score_tool],
    output_key="comp_response",
)