"""
Jersey Curriculum Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 Jersey Curriculum Dive. Reads the 120 per-cohort DuckLake
tables (30 subjects × 4 qualification levels × 1 language) and surfaces
the syllabus topic + learning-outcome frequency per subject per level
with RAGAS score histogram. Jersey-specific flags (French Bac, etc.)
are exposed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The 30 Jersey subjects (per the load_jersey_subjects() registry)
JERSEY_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature", "french", "physics",
    "chemistry", "biology", "combined_science", "computer_science", "history",
    "geography", "religious_studies", "psychology", "sociology", "economics",
    "business", "law", "media_studies", "art_design", "design_technology",
    "music", "physical_education", "drama", "global_perspectives",
    "environmental_science", "media_production", "sport_science",
    "travel_tourism", "health_social_care",
)

JERSEY_LEVELS: tuple[str, ...] = ("gcse", "a_level", "ib", "french_bac")


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


def _build_jersey_unions() -> str:
    """Build the UNION ALL clauses for the 120 Jersey cohorts."""
    unions = []
    for level in JERSEY_LEVELS:
        for subject in JERSEY_SUBJECTS:
            unions.append(
                f"SELECT '{level}' AS level, '{subject}' AS subject, * "
                f"FROM cianfhoghlaim.education.jersey.{level}.{subject}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


DIVE_SQL = f"""
WITH jersey_cohorts AS (
    {_build_jersey_unions()}
)
SELECT
    level,
    subject,
    is_french_bac,
    topic,
    topic_label_en,
    COUNT(*) AS n_mentions,
    AVG(ragas_score) AS avg_ragas_score
FROM jersey_cohorts
WHERE level IN ('gcse', 'a_level', 'ib', 'french_bac')
GROUP BY level, subject, is_french_bac, topic, topic_label_en
ORDER BY level, subject, n_mentions DESC
"""


JERSEY_CURRICULUM_TOPICS_DIVE = DiveSpec(
    name="jersey_curriculum_topics",
    description=(
        "BIEP v3 — Jersey (States of Jersey Education Department) "
        "curriculum topic + learning-outcome frequency per subject per "
        "level (30 subjects × 4 levels = 120 cohorts). Read from the "
        "canonical BIEP v3 namespace "
        "`cianfhoghlaim.education.jersey.<level>.<subject>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Topic distribution per Jersey subject (bar chart, all 4 levels)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "subject",
            "color": "level",
        },
        {
            "type": "histogram",
            "title": "RAGAS score distribution: French Bac vs other",
            "x": "avg_ragas_score",
            "y": "n_mentions",
            "color": "is_french_bac",
        },
    ],
    filters=[
        {"column": "level", "type": "multi_select", "options": list(JERSEY_LEVELS)},
        {"column": "subject", "type": "multi_select", "options": list(JERSEY_SUBJECTS)},
        {"column": "is_french_bac", "type": "select", "options": [True, False]},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return JERSEY_CURRICULUM_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {JERSEY_CURRICULUM_TOPICS_DIVE.name}")
        print(f"Description: {JERSEY_CURRICULUM_TOPICS_DIVE.description}")
        print(f"Charts: {len(JERSEY_CURRICULUM_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(JERSEY_CURRICULUM_TOPICS_DIVE.filters)}")
