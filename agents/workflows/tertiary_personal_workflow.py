"""tertiary_personal_workflow — ADK 2 Pillar 1 Workflow graph for UoG tertiary students.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.

    START ─► load_profile (function, 0 LLM) ─► uoa_portal (agent)
                                                │
                                                ▼
                                       students_union_root (agent)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os

from google.adk import Agent, Event, Workflow
from google.adk.workflow import START

logger = logging.getLogger(__name__)


def load_profile(_ctx, _node_input):
    student_id = os.environ.get("UO_PORTAL_USER", "default")
    return Event(output={
        "student_id": student_id,
        "programmes_url": f"md:cianfhoghlaim.tertiary.uog.modules/{student_id}/programmes",
    })


def _uoa_portal():
    from agents.uoa_portal.portal_agent import build_root_agent
    return build_root_agent()


def _students_union_root():
    from agents.meaisinfhoghlaim.educational.students_union.root_agent import root_agent
    return root_agent


def build_tertiary_personal_workflow() -> Workflow:
    return Workflow(
        name="tertiary_personal_workflow",
        description=(
            "UoG tertiary personal workflow (Pillar 1 graph): "
            "load_profile (0 LLM) → uoa_portal → students_union_root."
        ),
        edges=[
            (START, load_profile, _uoa_portal(), _students_union_root()),
        ],
    )


tertiary_personal_workflow = build_tertiary_personal_workflow()
