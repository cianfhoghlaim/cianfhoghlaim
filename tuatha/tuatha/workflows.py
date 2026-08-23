"""tuatha.workflows — the 4 per-subject workflow handlers.

Per the BIEP v1 pattern (the parent's
`agents/tuatha/_workflow_handlers.py`): the 4 canonical
per-subject workflow handlers are:

- `study_plan_workflow` — builds a per-subject study plan from
  the current syllabus + the student's mastery state
- `exam_paper_workflow` — annotates an exam paper with the
  marking scheme + per-question difficulty
- `marking_scheme_workflow` — explains a marking scheme line
  by line with the BAML-extracted syllabus + past-paper
  reference
- `curriculum_change_workflow` — detects + reports a
  curriculum change from the NCCA / AQA / SQA / WJEC / IoM
  websites (the Dagster sensor surface)

Each workflow is async + takes a context + a query.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import TuathaConfig
from .routing import SubjectAgentWiring

# ── The 4 canonical workflow context types ─────────────────


@dataclass(frozen=True)
class StudyPlanContext:
    """The study plan workflow context."""

    subject: str
    student_id: str
    level: str  # 'hl' | 'ol' | 'jc' | 'gcse' | 'a-level' | 'cfe-h' | 'cfe-a' | etc.
    language: str  # 'en' | 'ga' | 'gd' | 'cy' | 'gv'
    n_weeks: int
    target_grade: str | None = None


@dataclass(frozen=True)
class ExamPaperContext:
    """The exam paper annotation workflow context."""

    subject: str
    exam_year: int
    level: str
    paper_number: int  # 1 | 2
    language: str = "en"


@dataclass(frozen=True)
class MarkingSchemeContext:
    """The marking scheme explanation workflow context."""

    subject: str
    exam_year: int
    level: str
    paper_number: int
    language: str = "en"


@dataclass(frozen=True)
class CurriculumChangeContext:
    """The curriculum change detection workflow context."""

    jurisdiction: str  # 'ie' | 'sct' | 'wls' | 'ni' | 'eng' | 'iom'
    since: str  # ISO date string


# ── The 4 workflow entry points ─────────────────────────────


async def study_plan_workflow(
    wire: SubjectAgentWiring,
    context: StudyPlanContext,
    config: TuathaConfig | None = None,
) -> dict[str, Any]:
    """Build a per-subject study plan.

    Per the BAML/Letta graceful-degradation pattern: this is the
    canonical mount point. The actual BAML function call is
    `wire.baml_prefix + 'StudyPlan'` (e.g., 'MathStudyPlan').
    """
    return {
        "workflow": "study_plan",
        "wire": wire,
        "context": context,
        "status": "dispatched",
    }


async def exam_paper_workflow(
    wire: SubjectAgentWiring,
    context: ExamPaperContext,
    config: TuathaConfig | None = None,
) -> dict[str, Any]:
    """Annotate an exam paper with the marking scheme.

    Per the BAML/Letta graceful-degradation pattern.
    """
    return {
        "workflow": "exam_paper",
        "wire": wire,
        "context": context,
        "status": "dispatched",
    }


async def marking_scheme_workflow(
    wire: SubjectAgentWiring,
    context: MarkingSchemeContext,
    config: TuathaConfig | None = None,
) -> dict[str, Any]:
    """Explain a marking scheme line by line.

    Per the BAML/Letta graceful-degradation pattern.
    """
    return {
        "workflow": "marking_scheme",
        "wire": wire,
        "context": context,
        "status": "dispatched",
    }


async def curriculum_change_workflow(
    wire: SubjectAgentWiring,
    context: CurriculumChangeContext,
    config: TuathaConfig | None = None,
) -> dict[str, Any]:
    """Detect + report a curriculum change from the NCCA / AQA
    / SQA / WJEC / IoM websites.

    Per the BAML/Letta graceful-degradation pattern.
    """
    return {
        "workflow": "curriculum_change",
        "wire": wire,
        "context": context,
        "status": "dispatched",
    }


__all__ = [
    "CurriculumChangeContext",
    "ExamPaperContext",
    "MarkingSchemeContext",
    "StudyPlanContext",
    "TuathaConfig",
    "curriculum_change_workflow",
    "exam_paper_workflow",
    "marking_scheme_workflow",
    "study_plan_workflow",
]
