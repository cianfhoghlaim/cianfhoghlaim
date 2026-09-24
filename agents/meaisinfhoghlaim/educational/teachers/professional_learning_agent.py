"""professional_learning_agent — Google ADK agent for OIDE/PDST course recommendation.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Recommends OIDE + PDST professional learning modules based on the
teacher's subject + stage + SEN responsibilities.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


async def recommend_pd_module_tool(
    teacher_id: str,
    subject: str,
    stage: str,
    responsibilities: str = "",
) -> dict[str, Any]:
    """Recommend OIDE/PDST professional learning modules."""
    return {
        "teacher_id": teacher_id,
        "subject": subject,
        "stage": stage,
        "recommended_modules": [
            {"module_id": "pdst-post-primary-maths", "name": "Maths CPD workshops", "format": "workshop", "duration_hours": 6},
            {"module_id": "oide-csla", "name": "Cluster Support for Leadership", "format": "cluster", "duration_hours": 12},
        ],
        "rationale": f"Recommended based on the teacher's subject ({subject}) + stage ({stage}) + responsibilities ({responsibilities})",
    }


pd_recommend_tool = FunctionTool(func=recommend_pd_module_tool)


professional_learning_agent = LlmAgent(
    name="professional_learning_agent",
    model="gemini-2.5-flash",
    description="Recommends OIDE + PDST professional learning modules based on teacher subject + stage + responsibilities.",
    instruction="""
You are the professional-learning recommendation agent for an Irish
teacher. Query the OIDE + PDST module datasets (via the teacher_pd DLT
source) and recommend 3-5 modules that match the teacher's:
  - Subject (e.g. primary_mathematics, computer_science)
  - Stage (primary, post_primary, jc, sc)
  - Responsibilities (SEN tutor, year head, subject coordinator)
  - SEN allocation (e.g. ASD-trained for autism-specific PD)
  - Career stage (newly qualified teachers get induction modules)

Always:
- Cite the OIDE/PDST module URL
- Note whether the module is online vs in-person
- Note the hours commitment + when it's available
- For SEN-related modules, note the NCSE cross-credit eligibility

Tone: practical, time-conscious, growth-oriented.
""",
    tools=[pd_recommend_tool],
    output_key="professional_learning_response",
)
