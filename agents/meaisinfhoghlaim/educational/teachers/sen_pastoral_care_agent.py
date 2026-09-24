"""sen_pastoral_care_agent — Google ADK agent for SEN coordination + pastoral care.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Uses the BAML ExtractSENRecord function.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def extract_sen_record_tool(
    student_id: str,
    document_text: str,
) -> dict[str, Any]:
    """Extract a SEN record from an SENCO document."""
    try:
        from baml_client import b

        record = b.ExtractSENRecord(document_text, student_id)
        return record.model_dump()
    except Exception as exc:
        logger.warning("extract_sen_record_tool.baml_unavailable: %s", exc)
        return {"student_id": student_id, "stub": True}


sen_record_tool = FunctionTool(func=extract_sen_record_tool)


sen_pastoral_care_agent = LlmAgent(
    name="sen_pastoral_care_agent",
    model="gemini-2.5-flash",
    description="Coordinates SEN provision + pastoral care for Irish primary + post-primary schools.",
    instruction="""
You are the SEN + pastoral care coordinator agent for an Irish school.

Always:
- Apply the SEN allocation rules per the Department of Education NCSE guidelines
- Honour parent consent (GDPR + Children First Act 2015)
- Flag any welfare concern to the principal + designated liaison person
- Schedule next-review dates per the school's SEN policy
- Use Irish-appropriate language (e.g. 'tuismitheoir' for parent)

Tone: professional, empathetic, legally-aware.
""",
    tools=[sen_record_tool],
    output_key="sen_pastoral_response",
)
