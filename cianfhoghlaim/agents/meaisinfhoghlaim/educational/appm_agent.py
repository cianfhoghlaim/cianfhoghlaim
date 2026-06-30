"""
Applied Mathematics Specialist Agent (appm_agent) — Cianfhoghlaim Educational MMO.

One of 8 NCCA subject agents. Backed by BAML `qpack_applied_mathematics.baml`,
LiteLLM gateway, LanceDB (oideachais.lc.applied_mathematics.*), and Letta.

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
    cianfhoghlaim/baml/qpack_applied_mathematics.baml
"""
from __future__ import annotations

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..adk.tuatha_config import config
from .tools.appm_syllabus_lookup import lookup_appm_lo
from .tools.appm_past_paper_lookup import lookup_appm_paper
from .tools.appm_marking_scheme_lookup import lookup_appm_marking_scheme
from .tools.appm_formative_item_generate import generate_appm_item
from .tools.appm_response_score import score_appm_response


async def appm_syllabus_lookup_tool(topic: str, language: str = "en") -> list[dict]:
    try:
        return await lookup_appm_lo(topic=topic, language=language, limit=10)
    except Exception:
        return []


async def appm_past_paper_lookup_tool(topic: str, year: int | None = None) -> list[dict]:
    try:
        return await lookup_appm_paper(topic=topic, year=year, limit=5)
    except Exception:
        return []


async def appm_marking_scheme_lookup_tool(lo_code: str) -> dict:
    try:
        return await lookup_appm_marking_scheme(lo_code=lo_code)
    except Exception:
        return {"error": "Marking scheme lookup failed"}


async def appm_formative_item_generate_tool(
    lo_code: str, difficulty: int, topic: str = ""
) -> dict:
    try:
        return await generate_appm_item(
            lo_code=lo_code, difficulty=difficulty, level="lc_hl", topic=topic
        )
    except Exception as exc:
        return {"error": f"Item generation failed: {exc}"}


async def appm_response_score_tool(
    item_id: str,
    student_response: str,
    response_format: str = "text",
    time_taken_seconds: int = 0,
    hints_used: int = 0,
) -> dict:
    try:
        return await score_appm_response(
            item_id=item_id,
            student_response=student_response,
            response_format=response_format,
            time_taken_seconds=time_taken_seconds,
            hints_used=hints_used,
        )
    except Exception as exc:
        return {"error": f"Scoring failed: {exc}"}


syllabus_tool = FunctionTool(func=appm_syllabus_lookup_tool)
past_paper_tool = FunctionTool(func=appm_past_paper_lookup_tool)
marking_scheme_tool = FunctionTool(func=appm_marking_scheme_lookup_tool)
formative_item_tool = FunctionTool(func=appm_formative_item_generate_tool)
response_score_tool = FunctionTool(func=appm_response_score_tool)


appm_agent = LlmAgent(
    name="appm_agent",
    model=config.worker_model,
    description=(
        "Applied Mathematics specialist agent for the NCCA Leaving Certificate "
        "(Higher Level only). Mechanics, dynamics, projectiles, friction, "
        "work-energy-power, circular motion, SHM, rigid bodies, statics, "
        "gravity. Bilingual EN + GA feedback."
    ),
    instruction=f"""
    You are the Applied Mathematics Specialist Agent for the Cianfhoghlaim
    Educational MMO. You teach NCCA Leaving Certificate Applied Mathematics
    at Higher Level (APPM is HL only).

    **YOUR EXPERTISE:**
    - All LC-APPM-LO-* learning outcomes
    - Past paper patterns (ALP papers)
    - Mechanics, dynamics, projectiles, friction, work-energy-power
    - Circular motion, simple harmonic motion, rigid body dynamics
    - Statics, hydrostatics, gravitation
    - Cross-subject bridge to Pure Mathematics (LC-MATHS-LO-*) — calculus,
      vectors, complex numbers all bridge naturally

    **AVAILABLE TOOLS:**
    1. appm_syllabus_lookup_tool - Find NCCA learning outcomes
    2. appm_past_paper_lookup_tool - Find past paper questions
    3. appm_marking_scheme_lookup_tool - Get marking schemes
    4. appm_formative_item_generate_tool - Generate formative items
    5. appm_response_score_tool - Score student attempts

    **TEACHING APPROACH:**
    1. Always cite the NCCA LO code (e.g. "LC-APPM-LO-2.4").
    2. Provide step-by-step worked solutions with marking-scheme
       alignment: which step earns which mark.
    3. Use 4 graduated hints (Level 1 nudge → Level 4 step-by-step).
    4. Use diagrams / free-body diagrams where appropriate.
    5. When the student is stuck on a derivative/integration, suggest
       bridging to Pure Mathematics first.
    6. Encourage the student. APPM is the hardest LC subject.

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Go n-éirí an t-ádh leat!
    """,
    tools=[
        syllabus_tool,
        past_paper_tool,
        marking_scheme_tool,
        formative_item_tool,
        response_score_tool,
    ],
    output_key="appm_response",
)