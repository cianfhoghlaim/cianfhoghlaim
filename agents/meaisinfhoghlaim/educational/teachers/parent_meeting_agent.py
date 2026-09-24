"""parent_meeting_agent — Google ADK agent for parent-teacher meeting prep.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def prepare_parent_meeting_tool(
    class_id: str,
    student_id: str,
    meeting_type: str = "progress",
) -> dict[str, Any]:
    """Prepare for a parent-teacher meeting.

    Args:
        class_id: e.g. '5th-class-a'
        student_id: e.g. 's00001'
        meeting_type: 'progress' | 'sen_review' | 'pastoral' | 'behaviour'
    """
    return {
        "agenda": [
            "Welcome + introductions",
            "Academic progress (subject-level)",
            "Social + pastoral update",
            "SEN provision + accommodations (if applicable)",
            "Actions + next steps",
            "Parent questions + close",
        ],
        "data_to_prepare": [
            "Latest CAT / test scores",
            "Attendance percentage YTD",
            "Behaviour log (positive + concerns)",
            "Class teacher comment",
        ],
        "duration_minutes": 30,
        "tone": "constructive, parent-friendly, solution-focused",
    }


parent_meeting_tool = FunctionTool(func=prepare_parent_meeting_tool)


parent_meeting_agent = LlmAgent(
    name="parent_meeting_agent",
    model="gemini-2.5-flash",
    description="Prepares for parent-teacher meetings (progress / SEN / pastoral / behaviour).",
    instruction="""
You are the parent-meeting preparation agent for an Irish primary +
post-primary teacher.

Always:
- Prepare a clear agenda with timings
- Surface the data the teacher needs to bring (CAT scores, attendance, behaviour log)
- Use Irish-appropriate language ('tuismitheoir', 'ag tuairim is dá mbuadh', etc.)
- Frame concerns constructively (solution-focused, not deficit-focused)
- Honour GDPR + Children First Act 2015 (parent consent + designated liaison)

Tone: warm, professional, parent-friendly.
""",
    tools=[parent_meeting_tool],
    output_key="parent_meeting_response",
)
