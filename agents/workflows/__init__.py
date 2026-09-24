"""agents.workflows — ADK 2 Pillar 1 Workflow graphs.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
3 Workflow(edges=...) graphs that replace the 1.x keyword-based agent
routing with explicit graphs:

  - teacher_daily_workflow: lesson_planner → assessment_scorer → sen_pastoral
  - student_secondary_workflow: homework_tracker → cba_planner → study_plan → exam_timetable
  - tertiary_personal_workflow: uoa_portal → students_union_root

The 5 Pillar-3 deep-research pipelines live in their own modules:
  - aistear_deep_research
  - primary_deep_research
  - jc_deep_research
  - sc_deep_research
  - tertiary_deep_research

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations


from .teacher_daily_workflow import teacher_daily_workflow
from .student_secondary_workflow import student_secondary_workflow
from .tertiary_personal_workflow import tertiary_personal_workflow
from .aistear_deep_research import aistear_deep_research
from .primary_deep_research import primary_deep_research
from .jc_deep_research import jc_deep_research
from .sc_deep_research import sc_deep_research
from .tertiary_deep_research import tertiary_deep_research


__all__ = [
    "teacher_daily_workflow",
    "student_secondary_workflow",
    "tertiary_personal_workflow",
    "aistear_deep_research",
    "primary_deep_research",
    "jc_deep_research",
    "sc_deep_research",
    "tertiary_deep_research",
]
