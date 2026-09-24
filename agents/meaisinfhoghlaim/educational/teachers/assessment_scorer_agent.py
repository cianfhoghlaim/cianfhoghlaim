"""assessment_scorer_agent — Google ADK agent for K-12 teacher assessment scoring.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Uses the BAML ExtractAssessmentTask function.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def score_assessment_task_tool(
    task_id: str,
    student_work: str,
    marks_available: int = 100,
) -> dict[str, Any]:
    """Score a student assessment task using the relevant NCCA rubric.

    Args:
        task_id: e.g. 'cba-english-jc1-2026-saoirse'
        student_work: the student's submitted work
        marks_available: max marks for the assessment

    Returns:
        dict with keys: marks_awarded, level, criterion_breakdown, feedback
    """
    try:
        from baml_client import b

        prompt = f"Score task {task_id} (max {marks_available} marks): {student_work}"
        task = b.ExtractAssessmentTask(prompt, task_id=task_id)
        return task.model_dump()
    except Exception as exc:
        logger.warning("score_assessment_task_tool.baml_unavailable: %s", exc)
        return {"task_id": task_id, "stub": True}


score_assessment_tool = FunctionTool(func=score_assessment_task_tool)


assessment_scorer_agent = LlmAgent(
    name="assessment_scorer_agent",
    model="gemini-2.5-flash",
    description="Scores CBA + LC exam papers + primary assessments using NCCA rubrics.",
    instruction="""
You are the assessment scorer agent. Given a task_id + student
work, score using the relevant NCCA assessment criteria + the marking
scheme rubric.

Always:
- Cite the criterion from the rubric (e.g. 'originality', 'research')
- Provide constructive feedback (2-3 sentences)
- Note if the work is at Higher / Ordinary / Common level
- For CBA scoring, reference the exemplar work URL if available
- Provide criterion-level breakdown (e.g. originality: 18/20)

Tone: fair, consistent, formative.
""",
    tools=[score_assessment_tool],
    output_key="assessment_score_response",
)
