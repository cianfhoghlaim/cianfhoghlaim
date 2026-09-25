"""student_secondary_workflow — ADK 2 Pillar 1 Workflow graph for JC + LC + TY students.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.

    START ─► load_subjects (function, 0 LLM) ─► homework_tracker (agent)
                                              │
                                              ▼
                                        cba_planner (agent)
                                              │
                                              ▼
                                       study_plan (agent)
                                              │
                                              ▼
                                    exam_timetable (agent)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os

from google.adk import Agent, Event, Workflow
from google.adk.workflow import START

logger = logging.getLogger(__name__)


def load_subjects(_ctx, _node_input):
    """The 0-LLM function node — loads the student's enrolled subjects."""
    student_id = os.environ.get("STUDENT_ID", "s00001")
    return Event(output={
        "student_id": student_id,
        "subjects_url": f"md:cianfhoghlaim.education.british_isles.ireland.class_roster/{student_id}/subjects",
    })


def _homework():
    from agents.meaisinfhoghlaim.educational.students_jc.homework_tracker_agent import homework_tracker_agent
    return homework_tracker_agent


def _cba():
    from agents.meaisinfhoghlaim.educational.students_jc.cba_planner_agent import cba_planner_agent
    return cba_planner_agent


def _study_plan():
    from agents.meaisinfhoghlaim.educational.students_jc.study_plan_agent import study_plan_agent
    return study_plan_agent


def _exam_tt():
    from agents.meaisinfhoghlaim.educational.students_jc.exam_timetable_agent import exam_timetable_agent
    return exam_timetable_agent


def build_student_secondary_workflow() -> Workflow:
    return Workflow(
        name="student_secondary_workflow",
        description=(
            "JC + LC + TY student workflow (Pillar 1 graph): "
            "load_subjects (0 LLM) → homework_tracker → cba_planner → study_plan → exam_timetable."
        ),
        edges=[
            (START, load_subjects, _homework(), _cba(), _study_plan(), _exam_tt()),
        ],
    )


student_secondary_workflow = build_student_secondary_workflow()
