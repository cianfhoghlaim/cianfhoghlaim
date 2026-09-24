"""teacher_root — ADK 2 collaborative root orchestrator for the 5 teacher agents.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors the L3a_collaborative pattern from docs/google_examples/adk2-tutorial:
a coordinator agent with `sub_agents=[...]` + `mode="single_turn"` so the
relevant subset of specialists is invoked in parallel and the coordinator
synthesizes one answer.

The 5 teacher sub_agents are the agents shipped in Phase 2C of the umbrella
K-12 teacher-student-pipeline change:
- lesson_planner_agent
- assessment_scorer_agent
- sen_pastoral_care_agent
- parent_meeting_agent
- professional_learning_agent

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging

from google.adk.agents import Agent

logger = logging.getLogger(__name__)


# Lazy-load the 5 sub_agents (each is its own module under agents/meaisinfhoghlaim/educational/teachers/)
def _lesson_planner():
    from agents.meaisinfhoghlaim.educational.teachers.lesson_planner_agent import lesson_planner_agent
    return lesson_planner_agent


def _assessment_scorer():
    from agents.meaisinfhoghlaim.educational.teachers.assessment_scorer_agent import assessment_scorer_agent
    return assessment_scorer_agent


def _sen_pastoral():
    from agents.meaisinfhoghlaim.educational.teachers.sen_pastoral_care_agent import sen_pastoral_care_agent
    return sen_pastoral_care_agent


def _parent_meeting():
    from agents.meaisinfhoghlaim.educational.teachers.parent_meeting_agent import parent_meeting_agent
    return parent_meeting_agent


def _pro_learning():
    from agents.meaisinfhoghlaim.educational.teachers.professional_learning_agent import professional_learning_agent
    return professional_learning_agent


def build_teacher_root() -> Agent:
    """The Pillar-2 collaborative teacher root orchestrator."""
    return Agent(
        name="teacher_root",
        model="gemini-2.5-flash",
        sub_agents=[
            _lesson_planner(),
            _assessment_scorer(),
            _sen_pastoral(),
            _parent_meeting(),
            _pro_learning(),
        ],
        mode="single_turn",
        description=(
            "The K-12 teacher root orchestrator (Pillar 2 collaborative). "
            "Routes multi-faceted teacher queries (lesson plan + assessment + SEN + parent + PD) "
            "to the relevant subset of specialists in parallel + synthesizes the answer."
        ),
        instruction="""
You are the teacher root orchestrator for an Irish primary + post-primary
school. Given a multi-faceted teacher query (e.g. "plan next week's Year 4
maths lesson on fractions, then assess it, and check if Aoibh requires an SEN
accommodation"), invoke the relevant subset of your 5 specialists in parallel:

  - lesson_planner_agent: for lesson planning
  - assessment_scorer_agent: for assessment scoring
  - sen_pastoral_care_agent: for SEN + pastoral care
  - parent_meeting_agent: for parent meetings
  - professional_learning_agent: for OIDE/PDST course recommendations

Always:
- Invoke specialists in parallel (the Pillar 2 "single_turn" mode)
- Synthesize a 1-paragraph summary + action items per specialist
- For SEN queries, honour GDPR + Children First Act 2015 (parent consent)
- For PD queries, recommend only OIDE + PDST modules (the canonical 2 providers)
- Use Irish-appropriate language ('múinteoir', 'tuismitheoir', 'dalta', 'roinnt ranga')
- Cite the specialist in your synthesis (e.g. 'According to lesson_planner_agent...')

Tone: practical, time-conscious, growth-oriented.
""",
    )


teacher_root = build_teacher_root()


__all__ = ["build_teacher_root", "teacher_root"]
