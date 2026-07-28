"""
Guernsey Curriculum Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 Guernsey Curriculum Dive. Reads the 120 per-cohort DuckLake
tables (30 subjects × 4 qualification levels × 1 language) and surfaces
the syllabus topic + learning-outcome frequency per subject per level.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

GUERNSEY_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature", "french", "physics",
    "chemistry", "biology", "combined_science", "computer_science", "history",
    "geography", "religious_studies", "psychology", "sociology", "economics",
    "business", "law", "media_studies", "art_design", "design_technology",
    "music", "physical_education", "drama", "child_development",
    "global_perspectives", "environmental_science", "media_production",
    "sport_science", "travel_tourism", "health_social_care",
)

GUERNSEY_LEVELS: tuple[str, ...] = ("gcse", "a_level", "ib", "local")


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


def _build_guernsey_unions() -> str:
    """Build the UNION ALL clauses for the 120 Guernsey cohorts."""
    unions = []
    for level in GUERNSEY_LEVELS:
        for subject in GUERNSEY_SUBJECTS:
            unions.append(
                f"SELECT '{level}' AS level, '{subject}' AS subject, * "
                f"FROM cianfhoghlaim.education.guernsey.{level}.{subject}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


DIVE_SQL = f"""
WITH guernsey_cohorts AS (
    {_build_guernsey_unions()}
)
SELECT
    level,
    subject,
    is_local_qualification,
    topic,
    topic_label_en,
    COUNT(*) AS n_mentions,
    AVG(ragas_score) AS avg_ragas_score
FROM guernsey_cohorts
WHERE level IN ('gcse', 'a_level', 'ib', 'local')
GROUP BY level, subject, is_local_qualification, topic, topic_label_en
ORDER BY level, subject, n_mentions DESC
"""


GUERNSEY_CURRICULUM_TOPICS_DIVE = DiveSpec(
    name="guernsey_curriculum_topics",
    description=(
        "BIEP v3 — Guernsey (States of Guernsey Education Services) "
        "curriculum topic + learning-outcome frequency per subject per "
        "level (30 subjects × 4 levels = 120 cohorts)."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Topic distribution per Guernsey subject (bar chart)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "subject",
        },
    ],
    filters=[
        {"column": "level", "type": "multi_select", "options": list(GUERNSEY_LEVELS)},
        {"column": "subject", "type": "multi_select", "options": list(GUERNSEY_SUBJECTS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return GUERNSEY_CURRICULUM_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {GUERNSEY_CURRICULUM_TOPICS_DIVE.name}")
        print(f"Description: {GUERNSEY_CURRICULUM_TOPICS_DIVE.description}")
        print(f"Charts: {len(GUERNSEY_CURRICULUM_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(GUERNSEY_CURRICULUM_TOPICS_DIVE.filters)}")
