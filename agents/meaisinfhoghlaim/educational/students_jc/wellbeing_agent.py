"""wellbeing_agent — Google ADK agent for student wellbeing check-ins.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Confidential wellbeing check-ins for JC + LC + TY students across 6
domains (academic, social, family, physical, emotional, financial).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def wellbeing_checkin_tool(
    student_id: str,
    domain: str = "all",  # 'academic' | 'social' | 'family' | 'physical' | 'emotional' | 'financial'
    response: str = "",
) -> dict[str, Any]:
    """Confidential wellbeing check-in."""
    return {
        "student_id": student_id,
        "domain": domain,
        "response": response,
        "stub": True,
        "follow_up": "If any domain is 'crisis' or 'struggling', flag to the year head.",
    }


wellbeing_tool = FunctionTool(func=wellbeing_checkin_tool)


wellbeing_agent = LlmAgent(
    name="wellbeing_agent",
    model="gemini-2.5-flash",
    description="Confidential wellbeing check-ins for JC + LC + TY students across 6 domains.",
    instruction="""
You are the student wellbeing check-in agent. Conduct confidential
check-ins across 6 domains:
  - Academic (coping with workload, study-life balance)
  - Social (peer relationships, sense of belonging)
  - Family (home life, parental support)
  - Physical (sleep, exercise, nutrition)
  - Emotional (anxiety, mood, resilience)
  - Financial (cost of materials, transport, exam fees)

Always:
- Be empathetic, non-judgmental
- Use the Irish-appropriate language (cuidigh + cabhair)
- Flag any 'crisis' or 'struggling' domain to the year head + designated liaison person
- Honour GDPR + Children First Act 2015 (consent, escalation)

Tone: warm, supportive, professional.
""",
    tools=[wellbeing_tool],
    output_key="wellbeing_response",
)
