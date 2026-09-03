"""
england_a_level_complexity_dive.sql — BIEP v3 MotherDuck Dive (M3).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 England A-Level Complexity Dive. Surfaces the mark-allocation
+ assessment-objective distribution per board per subject with RAGAS
score histogram.

Dive name: ``england_a_level_complexity``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.england.a_level.<board>.<subject>.voted_canonical``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

A_LEVEL_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "further_mathematics",
    "pure_mathematics",
    "statistics",
    "mechanics",
    "decision_maths",
    "english_literature",
    "english_language_and_literature",
    "biology",
    "chemistry",
    "physics",
    "geology",
    "human_biology",
    "environmental_science",
    "french",
    "german",
    "spanish",
    "latin",
    "italian",
    "classical_civilisation",
    "ancient_history",
    "history",
    "geography",
    "religious_studies",
    "philosophy",
    "economics",
    "business",
    "psychology",
    "sociology",
    "politics",
    "law",
    "art_and_design",
    "design_technology",
    "drama",
    "music",
    "pe",
    "dance",
    "media_studies",
    "applied_business",
    "applied_ict",
    "communication_and_culture",
    "critical_thinking",
    "general_studies",
    "performing_arts",
    "psychology_a2",
    "sociology_a2",
    "politics_a2",
    "law_a2",
    "other",
    "engineering",
)


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


def _build_unions() -> str:
    """Build the UNION ALL clauses for the 147 A-Level cohorts."""
    unions = []
    for board in ENGLAND_BOARDS:
        for subject in A_LEVEL_SUBJECTS:
            unions.append(
                f"SELECT '{board}' AS board, '{subject}' AS subject, * "
                f"FROM cianfhoghlaim.education.england.a_level.{board}.{subject}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


DIVE_SQL = f"""
WITH england_a_level_complexity AS (
    {_build_unions()}
)
SELECT
    board,
    subject,
    total_marks,
    component_papers,
    COUNT(*) AS cohort_count,
    AVG(ragas_score) AS avg_ragas_score
FROM england_a_level_complexity
WHERE board IN ('aqa', 'ocr', 'edexcel')
GROUP BY board, subject, total_marks, component_papers
ORDER BY board, subject, total_marks DESC
"""


ENGLAND_A_LEVEL_COMPLEXITY_DIVE = DiveSpec(
    name="england_a_level_complexity",
    description=(
        "BIEP v3 — England A-Level mark-allocation + assessment-objective "
        "distribution per board per subject (49 subjects × 3 boards = 147 "
        "cohorts). Read from the canonical BIEP v3 namespace "
        "`cianfhoghlaim.education.england.a_level.<board>.<subject>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Total marks per A-Level subject (per board)",
            "x": "subject",
            "y": "total_marks",
            "facet": "board",
        },
        {
            "type": "bar",
            "title": "Component papers per A-Level subject (per board)",
            "x": "subject",
            "y": "component_papers",
            "facet": "board",
        },
    ],
    filters=[
        {"column": "board", "type": "multi_select", "options": list(ENGLAND_BOARDS)},
        {"column": "subject", "type": "multi_select", "options": list(A_LEVEL_SUBJECTS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    """Return the Dive spec as a JSON-serialisable dict for save_dive()."""
    return ENGLAND_A_LEVEL_COMPLEXITY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {ENGLAND_A_LEVEL_COMPLEXITY_DIVE.name}")
        print(f"Description: {ENGLAND_A_LEVEL_COMPLEXITY_DIVE.description}")
        print(f"Charts: {len(ENGLAND_A_LEVEL_COMPLEXITY_DIVE.charts)}")
        print(f"Filters: {len(ENGLAND_A_LEVEL_COMPLEXITY_DIVE.filters)}")
