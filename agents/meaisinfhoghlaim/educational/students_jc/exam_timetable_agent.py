"""exam_timetable_agent — Google ADK agent for State Exams Commission timetable tracking.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Surfaces the SEC timetable for the student's subjects + level + paper.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def exam_timetable_tool(
    student_id: str,
    subjects: list[str],
    level: str = "higher",
) -> dict[str, Any]:
    """Surface the SEC exam timetable for the student's subjects."""
    return {
        "student_id": student_id,
        "subjects": subjects,
        "level": level,
        "stub": True,
        "exams": [],
        "note": "Phase 2 fills from the State Examinations Commission official timetable PDF",
    }


exam_timetable_tool = FunctionTool(func=exam_timetable_tool)


exam_timetable_agent = LlmAgent(
    name="exam_timetable_agent",
    model="gemini-2.5-flash",
    description="Surfaces the SEC exam timetable for a JC or LC student + checks for timetable clashes.",
    instruction="""
You are the exam timetable agent. For a JC / LC student, surface:
  - The exam dates + times + venues for their subjects at their level (Higher / Ordinary)
  - The travel logistics (bus routes, parental transport, lunch arrangements)
  - Any clashes (e.g. two exams on the same day — flag for SENCO)
  - The exam material requirements (calculator, log tables, dictionary)

Always:
- Reference the official SEC source (examinations.ie)
- Note the level (Higher papers typically run 2-3 hrs, Ordinary 2-2.5 hrs)
- Apply the SEC reasonable accommodations policy for students with SEN
- Plan around the student's commute from home to exam centre

Tone: organised, supportive, detail-oriented.
""",
    tools=[exam_timetable_tool],
    output_key="exam_timetable_response",
)
