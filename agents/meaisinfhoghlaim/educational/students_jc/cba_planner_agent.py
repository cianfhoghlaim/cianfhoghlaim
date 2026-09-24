"""cba_planner_agent — Google ADK agent for JC Classroom-Based Assessment planning.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Helps JC students plan + execute the 2 CBAs per subject (worth 10% of the
final grade in 2026 spec).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def plan_cba_tool(
    student_id: str,
    cba_id: str,
) -> dict[str, Any]:
    """Plan a JC CBA.

    Args:
        student_id: e.g. 's00003'
        cba_id: e.g. 'cba-english-jc1-2026-saoirse'
    """
    return {
        "student_id": student_id,
        "cba_id": cba_id,
        "stub": True,
        "phases": [
            "Receive the brief (Week 1)",
            "Research + plan (Weeks 2-3)",
            "Draft (Week 4)",
            "Teacher feedback + revision (Week 5)",
            "Final submission (Week 6)",
            "Assessment feedback received (Week 8)",
        ],
        "warning": "CBAs are worth 10% of the final grade per the 2026 NCCA spec",
    }


cba_plan_tool = FunctionTool(func=plan_cba_tool)


cba_planner_agent = LlmAgent(
    name="cba_planner_agent",
    model="gemini-2.5-flash",
    description="Plans + tracks the 2 CBAs per JC subject (worth 10% of the final grade in the 2026 spec).",
    instruction="""
You are the JC CBA planner agent. JC students complete 2 CBAs per
subject worth 10% of the final grade (per the 2026 NCCA spec). Help
them:
  - Break the brief down into manageable phases
  - Track word counts + sources
  - Plan around other subjects' deadlines
  - Reference exemplar work URLs where available
  - Use teacher feedback rounds effectively

Tone: organised, encouraging, age-appropriate (JC1 = ~12 yo).
""",
    tools=[cba_plan_tool],
    output_key="cba_plan_response",
)
