"""
Scotland Curriculum Topics Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 Scotland Curriculum Topics Dive. Reads the 150 per-cohort
DuckLake tables (50 SCQF subjects × 3 qualification levels × 1 language)
and surfaces the topic + learning-outcome frequency per subject per
level with RAGAS score histogram.

Dive name: ``scotland_curriculum_topics``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.scotland.higher.<subject>.voted_canonical``
  - ``md:cianfhoghlaim.education.scotland.national_5.<subject>.voted_canonical``
  - ``md:cianfhoghlaim.education.scotland.advanced_higher.<subject>.voted_canonical``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The 50 Scotland SCQF subjects (per the load_scotland_subjects() registry)
SCOTLAND_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english", "physics", "chemistry", "biology",
    "mathematics_statistics", "mathematics_mechanics", "human_biology",
    "environmental_science", "computing_science", "design_technology",
    "graphic_communication", "engineering_science", "physics_technology",
    "chemistry_technology", "biology_technology", "history", "modern_studies",
    "geography", "philosophy", "religious_moral_education", "classical_studies",
    "history_ancient", "french", "german", "spanish", "italian", "mandarin_chinese",
    "gaelic_learners", "english_for_work", "mathematics_applications", "media",
    "music_technology", "art_design", "physical_education", "music", "drama",
    "business_management", "accounting", "economics", "health_food_technology",
    "early_years", "travel_tourism", "hospitality", "care", "construction",
    "engineering_systems", "design_engineering", "graphic_com_advanced",
)

SCOTLAND_LEVELS: tuple[str, ...] = ("national_5", "higher", "advanced_higher")


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


def _build_scotland_unions() -> str:
    """Build the UNION ALL clauses for the 150 Scotland cohorts."""
    unions = []
    for level in SCOTLAND_LEVELS:
        for subject in SCOTLAND_SUBJECTS:
            unions.append(
                f"SELECT '{level}' AS level, '{subject}' AS subject, * "
                f"FROM cianfhoghlaim.education.scotland.{level}.{subject}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


DIVE_SQL = f"""
WITH scotland_cohorts AS (
    {_build_scotland_unions()}
)
SELECT
    level,
    subject,
    topic,
    topic_label_en,
    COUNT(*) AS n_mentions,
    AVG(ragas_score) AS avg_ragas_score
FROM scotland_cohorts
WHERE level IN ('national_5', 'higher', 'advanced_higher')
GROUP BY level, subject, topic, topic_label_en
ORDER BY level, subject, n_mentions DESC
"""


SCOTLAND_CURRICULUM_TOPICS_DIVE = DiveSpec(
    name="scotland_curriculum_topics",
    description=(
        "BIEP v3 — Scotland (SQA) curriculum topic + learning-outcome "
        "frequency per subject per level (50 subjects × 3 levels = 150 "
        "cohorts). Read from the canonical BIEP v3 namespace "
        "`cianfhoghlaim.education.scotland.<level>.<subject>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Topic distribution per Scotland subject (bar chart, all 3 levels)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "subject",
            "color": "level",
        },
        {
            "type": "histogram",
            "title": "RAGAS score distribution per Scotland level",
            "x": "avg_ragas_score",
            "y": "n_mentions",
            "facet": "level",
        },
    ],
    filters=[
        {"column": "level", "type": "multi_select", "options": list(SCOTLAND_LEVELS)},
        {"column": "subject", "type": "multi_select", "options": list(SCOTLAND_SUBJECTS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return SCOTLAND_CURRICULUM_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {SCOTLAND_CURRICULUM_TOPICS_DIVE.name}")
        print(f"Description: {SCOTLAND_CURRICULUM_TOPICS_DIVE.description}")
        print(f"Charts: {len(SCOTLAND_CURRICULUM_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(SCOTLAND_CURRICULUM_TOPICS_DIVE.filters)}")
