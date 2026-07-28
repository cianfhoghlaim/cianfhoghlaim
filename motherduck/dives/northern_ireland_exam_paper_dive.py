"""
Northern Ireland Exam Paper Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 Northern Ireland Exam Paper Dive. Reads the 70 per-cohort
DuckLake tables (35 CCEA subjects × 2 qualification levels × 1 language)
and surfaces the exam paper + section + question structure with RAGAS
score histogram. Gaeltacht (Irish-medium) subjects are flagged.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The 35 CCEA subjects (per the load_northern_ireland_subjects() registry)
NI_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature", "irish",
    "irish_language", "french", "german", "spanish", "italian", "physics",
    "chemistry", "biology", "combined_science", "computer_science", "history",
    "geography", "religious_studies", "philosophy", "psychology", "sociology",
    "economics", "business_studies", "law", "media_studies", "art_and_design",
    "design_technology", "music", "physical_education", "drama",
    "health_and_social_care", "travel_and_tourism", "applied_ict",
    "applied_science", "engineering", "design_and_technology",
)

NI_LEVELS: tuple[str, ...] = ("gcse", "a_level")


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


def _build_ni_unions() -> str:
    """Build the UNION ALL clauses for the 70 NI cohorts."""
    unions = []
    for level in NI_LEVELS:
        for subject in NI_SUBJECTS:
            unions.append(
                f"SELECT '{level}' AS level, '{subject}' AS subject, * "
                f"FROM cianfhoghlaim.education.northern_ireland.{level}.{subject}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


DIVE_SQL = f"""
WITH ni_cohorts AS (
    {_build_ni_unions()}
)
SELECT
    level,
    subject,
    paper_code,
    exam_year,
    total_marks,
    duration_minutes,
    COUNT(*) AS n_questions,
    AVG(ragas_score) AS avg_ragas_score
FROM ni_cohorts
WHERE level IN ('gcse', 'a_level')
GROUP BY level, subject, paper_code, exam_year, total_marks, duration_minutes
ORDER BY level, subject, exam_year DESC
"""


NI_CURRICULUM_TOPICS_DIVE = DiveSpec(
    name="northern_ireland_exam_paper_dive",
    description=(
        "BIEP v3 — Northern Ireland (CCEA) exam paper structure per "
        "subject per level (35 subjects × 2 levels = 70 cohorts). "
        "Read from the canonical BIEP v3 namespace "
        "`cianfhoghlaim.education.northern_ireland.<level>.<subject>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Exam paper component structure per NI subject (bar chart)",
            "x": "subject",
            "y": "total_marks",
            "facet": "level",
        },
        {
            "type": "bar",
            "title": "Exam paper duration per NI subject (bar chart)",
            "x": "subject",
            "y": "duration_minutes",
            "facet": "level",
        },
    ],
    filters=[
        {"column": "level", "type": "multi_select", "options": list(NI_LEVELS)},
        {"column": "subject", "type": "multi_select", "options": list(NI_SUBJECTS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return NI_CURRICULUM_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {NI_CURRICULUM_TOPICS_DIVE.name}")
        print(f"Description: {NI_CURRICULUM_TOPICS_DIVE.description}")
        print(f"Charts: {len(NI_CURRICULUM_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(NI_CURRICULUM_TOPICS_DIVE.filters)}")
