"""study_plan_agent — Google ADK agent for LC + TY student exam revision planning.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Plans the LC June exam window + TY portfolio + module revision.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def build_study_plan_tool(
    student_id: str,
    subjects: list[str],
    exam_window: str = "LC 2026 June",
) -> dict[str, Any]:
    """Build a study plan for the LC exam window."""
    return {
        "student_id": student_id,
        "subjects": subjects,
        "exam_window": exam_window,
        "stub": True,
        "plan": {
            subject: {
                "weeks_allocated": 3,
                "topics": [],
                "resources": [],
            } for subject in subjects
        },
    }


study_plan_tool = FunctionTool(func=build_study_plan_tool)


study_plan_agent = LlmAgent(
    name="study_plan_agent",
    model="gemini-2.5-flash",
    description="Plans the LC June exam window + TY portfolio + module revision per subject.",
    instruction="""
You are the study plan agent for an LC / TY student. Help them:
  - Allocate weeks per subject (Higher = 4 weeks, Ordinary = 3 weeks, common = 1 week)
  - Mix subjects across days (avoid stacking related subjects)
  - Include active recall (past papers) + spaced repetition (1-week, 1-month, 3-month reviews)
  - Plan exam-day logistics (State Exams Commission timetable + transport)
  - Include wellbeing (sleep, exercise, breaks)

Tone: organised, encouraging, age-appropriate (LC6 = ~18 yo, TY = ~16 yo).
""",
    tools=[study_plan_tool],
    output_key="study_plan_response",
)
