"""teacher_daily_workflow — ADK 2 Pillar 1 Workflow graph for K-12 teachers.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.

Mirrors the L1_graph_basics + L2a_parallel_join pattern from
docs/google_examples/adk2-tutorial. A plain Python function and an
LLM agent are BOTH just nodes in the same `edges` list.

    START ─► plan_today (function, 0 LLM) ─► lesson_planner (agent)
                                                      │
                                                      ▼
                                              assessment_scorer (agent)
                                                      │
                                                      ▼
                                               sen_pastoral (agent)

The graph decides what runs next — predictable work (plan_today) stays a
function, reasoning uses the model.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os
from datetime import UTC, datetime

from google.adk import Agent, Event, Workflow
from google.adk.workflow import START

logger = logging.getLogger(__name__)


def _plan_today_inputs() -> dict:
    """Function node — captures the current day + class roster summary.

    Zero LLM calls. Returns the bundled inputs that the agent nodes consume.
    """
    now = datetime.now(UTC())
    return {
        "day_iso": now.date().isoformat(),
        "term": "autumn_2026",
        "class_roster_url": os.environ.get(
            "UOG_CLASS_ROSTER_URL", "md:cianfhoghlaim.education.british_isles.ireland.class_roster"
        ),
    }


def plan_today(_ctx, _node_input):
    """The 0-LLM function node — prepares the day."""
    payload = _plan_today_inputs()
    print(f"  [plan_today] function node · {payload['day_iso']}")
    return Event(output=payload)


# Agent nodes — imported lazily (the same pattern as the root orchestrators).
def _lesson_planner():
    from agents.meaisinfhoghlaim.educational.teachers.lesson_planner_agent import lesson_planner_agent
    return lesson_planner_agent


def _assessment_scorer():
    from agents.meaisinfhoghlaim.educational.teachers.assessment_scorer_agent import assessment_scorer_agent
    return assessment_scorer_agent


def _sen_pastoral():
    from agents.meaisinfhoghlaim.educational.teachers.sen_pastoral_care_agent import sen_pastoral_care_agent
    return sen_pastoral_care_agent


def build_teacher_daily_workflow() -> Workflow:
    """The ADK 2 Workflow(edges=...) graph for a teacher's daily workflow."""
    return Workflow(
        name="teacher_daily_workflow",
        description=(
            "K-12 teacher daily workflow (Pillar 1 graph): "
            "plan_today (0 LLM) → lesson_planner (agent) → assessment_scorer (agent) → sen_pastoral (agent)."
        ),
        edges=[
            (START, plan_today, _lesson_planner(), _assessment_scorer(), _sen_pastoral()),
        ],
    )


teacher_daily_workflow = build_teacher_daily_workflow()
