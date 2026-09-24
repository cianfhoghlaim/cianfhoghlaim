"""homework_tracker_agent — Google ADK agent for JC/LC student homework tracking.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def track_homework_tool(
    student_id: str,
    class_id: str,
    subject: str,
    action: str = "list",  # 'list' | 'mark_done' | 'add'
) -> dict[str, Any]:
    """Track homework for a student.

    Args:
        student_id: e.g. 's00001'
        class_id: e.g. 'jc1-english-a'
        subject: e.g. 'english' or 'all'
        action: 'list' | 'mark_done' | 'add'
    """
    return {
        "student_id": student_id,
        "class_id": class_id,
        "subject": subject,
        "action": action,
        "stub": True,
        "note": "Phase 2 fills from Google Classroom / Microsoft Teams API",
    }


homework_tracker_tool = FunctionTool(func=track_homework_tool)


homework_tracker_agent = LlmAgent(
    name="homework_tracker_agent",
    model="gemini-2.5-flash",
    description="Tracks homework per JC + LC student per subject.",
    instruction="""
You are the homework tracker agent for a JC / LC student. Help them:
  - See all upcoming homework
  - Mark items as done
  - Add new homework items
  - Track completion percentage by subject
  - Identify overdue items + nudges
  - Estimate time required

Tone: supportive, organized, age-appropriate (JC1 = ~12 yo, LC6 = ~18 yo).
""",
    tools=[homework_tracker_tool],
    output_key="homework_response",
)
