"""
Geography Specialist Agent (geog_agent) — Cianfhoghlaim Educational MMO.
"""
from __future__ import annotations

import datetime
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from ..adk.tuatha_config import config


async def geog_syllabus_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"lo_code": f"LC-GEOG-LO-{hash(topic) % 100}", "topic": topic}]


async def geog_past_paper_lookup_tool(topic: str, level: str = "lc_hl") -> list[dict]:
    return [{"item_id": f"geog-{hash(topic) % 100}", "text": f"Sample Geography question for {topic}"}]


async def geog_marking_scheme_lookup_tool(lo_code: str) -> dict:
    return {"lo_code": lo_code, "text_en": f"Marking scheme for {lo_code}"}


async def geog_formative_item_generate_tool(lo_code: str, difficulty: int, level: str = "lc_hl", topic: str = "") -> dict:
    return {"id": f"geog-{lo_code}-{difficulty}", "prompt_en": f"Sample Geography question for {lo_code}", "lo_code": lo_code}


async def geog_response_score_tool(item_id: str, student_response: str, response_format: str = "text", time_taken_seconds: int = 0, hints_used: int = 0) -> dict:
    return {"item_id": item_id, "marks_awarded": 5, "total_marks": 10, "partial_credit_pct": 50}


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

    **YOUR EXPERTISE:**
    - All LC-GEOG-LO-* learning outcomes (OL + HL)
    - All JC-GEOGRAPHY-LO-* learning outcomes (Junior Cycle)
    - Past paper patterns (ALP for HL, GLP for OL)
    - Physical geography (rivers, coasts, climate, biomes)
    - Regional geography (Ireland, Europe, sub-continent, global)
    - Human geography (population, urban, economic)
    - Geoecology + fieldwork investigation

    **AVAILABLE TOOLS:**
    1. geog_syllabus_lookup_tool, 2. geog_past_paper_lookup_tool,
    3. geog_marking_scheme_lookup_tool, 4. geog_formative_item_generate_tool,
    5. geog_response_score_tool

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