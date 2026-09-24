"""student_root — ADK 2 collaborative root orchestrator for the 5 student agents.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors the L3a_collaborative pattern. The 5 student sub_agents are the
agents shipped in Phase 2C:
- homework_tracker_agent
- cba_planner_agent
- study_plan_agent
- wellbeing_agent
- exam_timetable_agent

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging

from google.adk.agents import Agent

logger = logging.getLogger(__name__)


def _homework():
    from agents.meaisinfhoghlaim.educational.students_jc.homework_tracker_agent import homework_tracker_agent
    return homework_tracker_agent


def _cba():
    from agents.meaisinfhoghlaim.educational.students_jc.cba_planner_agent import cba_planner_agent
    return cba_planner_agent


def _study_plan():
    from agents.meaisinfhoghlaim.educational.students_jc.study_plan_agent import study_plan_agent
    return study_plan_agent


def _wellbeing():
    from agents.meaisinfhoghlaim.educational.students_jc.wellbeing_agent import wellbeing_agent
    return wellbeing_agent


def _exam_tt():
    from agents.meaisinfhoghlaim.educational.students_jc.exam_timetable_agent import exam_timetable_agent
    return exam_timetable_agent


def build_student_root() -> Agent:
    """The Pillar-2 collaborative student root orchestrator."""
    return Agent(
        name="student_root",
        model="gemini-2.5-flash",
        sub_agents=[
            _homework(),
            _cba(),
            _study_plan(),
            _wellbeing(),
            _exam_tt(),
        ],
        mode="single_turn",
        description=(
            "The JC + LC + TY student root orchestrator (Pillar 2 collaborative). "
            "Routes multi-faceted student queries (homework + CBA + study + wellbeing + exam) "
            "to the relevant subset of specialists in parallel + synthesizes the answer."
        ),
        instruction="""
You are the JC + LC + TY student root orchestrator. Given a multi-faceted
student query (e.g. "I'm behind on Irish homework, my CBA draft is due Friday,
my LC exams are in 3 weeks, and I'm stressed"), invoke the relevant subset
of your 5 specialists in parallel:

  - homework_tracker_agent: for tracking + organising homework
  - cba_planner_agent: for JC CBA planning
  - study_plan_agent: for LC + TY revision planning
  - wellbeing_agent: for stress + sleep + wellbeing check-ins
  - exam_timetable_agent: for SEC exam timetable + logistics

Always:
- Invoke specialists in parallel (Pillar 2 "single_turn")
- Synthesize a 1-paragraph summary + concrete action items
- For wellbeing concerns ("crisis" or "struggling"), flag to the year head
- For exam logistics, reference the State Examinations Commission
- Use Irish-appropriate language ('obair bhaile', 'staidéar', 'scrúdú', 'meabhairshláinte')

Tone: supportive, age-appropriate (JC1 ~12 yo, LC6 ~18 yo), encouraging.
""",
    )


student_root = build_student_root()


__all__ = ["build_student_root", "student_root"]
