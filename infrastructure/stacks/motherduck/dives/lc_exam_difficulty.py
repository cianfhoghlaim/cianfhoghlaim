"""
Exam Paper Difficulty Dive — BIEP v1 MotherDuck Dive (definition + dashboard).

A live MotherDuck dashboard for per-subject per-year per-paper
difficulty score (computed from BAML mark weight × part complexity).

Drill-down: click a paper → view the questions + the matching
marking scheme descriptors.

Dive name: ``lc_exam_difficulty``
DuckLake tables read:
  - ``md:oideachais.leaving_cert.<subject>_papers``
  - ``md:oideachais.leaving_cert.<subject>_marking``

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .lc_syllabus_topics import BIEP_SUBJECTS


@dataclass
class DiveSpec:
    name: str
    description: str
    sql: str
    charts: list[dict[str, Any]] = field(default_factory=list)
    filters: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "sql": self.sql,
            "charts": self.charts,
            "filters": self.filters,
        }


# The canonical SQL query.
DIVE_SQL = """
WITH paper_difficulty AS (
    SELECT
        subject, year, paper_code, level, language,
        total_marks,
        total_questions,
        CASE
            WHEN total_questions = 0 THEN 0
            ELSE ROUND(total_marks * 1.0 / total_questions, 2)
        END AS avg_marks_per_question,
        has_formula_sheet,
        has_data_booklet,
        duration_minutes
    FROM oideachais.leaving_cert.mathematics_papers
    UNION ALL BY NAME
    SELECT subject, year, paper_code, level, language,
           total_marks, total_questions,
           CASE WHEN total_questions = 0 THEN 0
                ELSE ROUND(total_marks * 1.0 / total_questions, 2) END,
           has_formula_sheet, has_data_booklet, duration_minutes
    FROM oideachais.leaving_cert.chemistry_papers
    UNION ALL BY NAME
    SELECT subject, year, paper_code, level, language,
           total_marks, total_questions,
           CASE WHEN total_questions = 0 THEN 0
                ELSE ROUND(total_marks * 1.0 / total_questions, 2) END,
           has_formula_sheet, has_data_booklet, duration_minutes
    FROM oideachais.leaving_cert.geography_papers
    UNION ALL BY NAME
    SELECT subject, year, paper_code, level, language,
           total_marks, total_questions,
           CASE WHEN total_questions = 0 THEN 0
                ELSE ROUND(total_marks * 1.0 / total_questions, 2) END,
           has_formula_sheet, has_data_booklet, duration_minutes
    FROM oideachais.leaving_cert.english_papers
    UNION ALL BY NAME
    SELECT subject, year, paper_code, level, language,
           total_marks, total_questions,
           CASE WHEN total_questions = 0 THEN 0
                ELSE ROUND(total_marks * 1.0 / total_questions, 2) END,
           has_formula_sheet, has_data_booklet, duration_minutes
    FROM oideachais.leaving_cert.gaeilge_papers
    UNION ALL BY NAME
    SELECT subject, year, paper_code, level, language,
           total_marks, total_questions,
           CASE WHEN total_questions = 0 THEN 0
                ELSE ROUND(total_marks * 1.0 / total_questions, 2) END,
           has_formula_sheet, has_data_booklet, duration_minutes
    FROM oideachais.leaving_cert.computer_science_papers
)
SELECT
    subject,
    year,
    paper_code,
    level,
    language,
    total_marks,
    total_questions,
    avg_marks_per_question,
    CASE
        WHEN avg_marks_per_question >= 15 THEN 'high'
        WHEN avg_marks_per_question >= 8  THEN 'medium'
        ELSE 'low'
    END AS difficulty_band,
    has_formula_sheet,
    has_data_booklet,
    duration_minutes
FROM paper_difficulty
ORDER BY subject, year, paper_code
"""


LC_EXAM_DIFFICULTY_DIVE = DiveSpec(
    name="lc_exam_difficulty",
    description=(
        "BIEP v1 — Per-subject per-year per-paper difficulty score "
        "(computed from BAML mark weight × part complexity). "
        "Drill-down: click a paper → view the questions + the matching "
        "marking scheme descriptors."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Average marks per question per paper (bar chart)",
            "x": "year",
            "y": "avg_marks_per_question",
            "color": "paper_code",
            "facet": "subject",
        },
        {
            "type": "heatmap",
            "title": "Difficulty band distribution per year per subject (heatmap)",
            "x": "year",
            "y": "subject",
            "value": "n_papers",
            "color_by": "difficulty_band",
        },
    ],
    filters=[
        {"column": "subject", "type": "multi_select", "options": list(BIEP_SUBJECTS)},
        {"column": "level", "type": "multi_select", "options": ["hl", "ol", "fl"]},
        {"column": "language", "type": "multi_select", "options": ["en", "ga"]},
        {"column": "year", "type": "range", "min": 1990, "max": 2026},
        {"column": "difficulty_band", "type": "multi_select", "options": ["high", "medium", "low"]},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    """Return the Dive spec as a JSON-serialisable dict for save_dive()."""
    return LC_EXAM_DIFFICULTY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {LC_EXAM_DIFFICULTY_DIVE.name}")
        print(f"Description: {LC_EXAM_DIFFICULTY_DIVE.description}")
        print(f"Charts: {len(LC_EXAM_DIFFICULTY_DIVE.charts)}")
        print(f"Filters: {len(LC_EXAM_DIFFICULTY_DIVE.filters)}")
