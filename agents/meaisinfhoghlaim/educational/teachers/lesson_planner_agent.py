"""lesson_planner_agent — Google ADK agent for K-12 teacher lesson planning.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Uses the BAML ExtractLessonPlan function from
baml_src/british_isles/ireland/education/teacher/teacher_extraction.baml.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def generate_lesson_plan_tool(
    class_id: str,
    subject: str,
    date_iso: str,
    duration_minutes: int = 40,
) -> dict[str, Any]:
    """Generate a lesson plan for a class + subject + date.

    Args:
        class_id: e.g. '5th-class-a'
        subject: e.g. 'primary_mathematics'
        date_iso: ISO date of the lesson
        duration_minutes: typical 30-60

    Returns:
        dict with keys: plan_id, learning_objectives, activities,
        differentiation, assessment, homework, sen_considerations
    """
    try:
        from baml_client import b

        prompt = f"Generate a lesson plan for {class_id} on {date_iso} for {subject} ({duration_minutes} min)"
        plan = b.ExtractLessonPlan(prompt, teacher_id="auto", class_id=class_id)
        return plan.model_dump()
    except Exception as exc:
        logger.warning("generate_lesson_plan_tool.baml_unavailable: %s", exc)
        return {"plan_id": f"lp-{class_id}-{date_iso}", "stub": True}


lesson_plan_tool = FunctionTool(func=generate_lesson_plan_tool)


lesson_planner_agent = LlmAgent(
    name="lesson_planner_agent",
    model="gemini-2.5-flash",
    description="Generates lesson plans from NCCA primary + JC + LC specifications + class roster + SEN flags + subject outcomes.",
    instruction="""
You are the lesson planner agent for Irish primary + post-primary
teachers. Given a class_id + subject + date, generate a lesson plan
using the canonical NCCA specification + the class roster + the
relevant SEN flags.

Always:
- Use 3-7 specific learning objectives (action-verb led)
- Include differentiation for mixed-ability classes
- Include SEN accommodations (e.g. reader-at-exam, separate-room)
- Include bilingual (EN/GA) considerations for Gaeltacht schools
- Reference the NCCA specification URL

Tone: professional, practical, time-conscious. Mirror the teacher's
own lesson-plan template.
""",
    tools=[lesson_plan_tool],
    output_key="lesson_plan_response",
)
