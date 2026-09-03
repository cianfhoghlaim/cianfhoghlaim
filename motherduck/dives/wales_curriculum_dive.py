"""
Wales Curriculum Topics Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 Wales Curriculum Topics Dive. Reads the 160 per-cohort
DuckLake tables (80 WJEC subjects × 2 qualification levels × 1 Welsh
language) and surfaces the topic + learning-outcome frequency per
subject per level with RAGAS score histogram. Welsh-medium subjects
are flagged via the `is_welsh_medium` field.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The 80 WJEC subjects (per the load_wales_subjects() registry)
WALES_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature", "welsh_language",
    "welsh_literature", "welsh_second_language", "french", "german", "spanish",
    "italian", "physics", "chemistry", "biology", "combined_science",
    "computer_science", "history", "geography", "religious_studies",
    "philosophy", "psychology", "sociology", "economics", "business_studies",
    "law", "media_studies", "art_and_design", "design_technology", "music",
    "physical_education", "drama", "health_and_social_care", "travel_and_tourism",
    "applied_ict", "applied_science", "engineering", "construction",
    "hospitality", "catering", "film_studies", "media_production",
    "music_technology", "performing_arts", "classical_civilisation", "geology",
    "environmental_science", "astronomy", "statistics", "electronics",
    "mechanics", "psychology_a2", "sociology_a2", "law_a2", "economics_a2",
    "history_ancient", "world_development", "law_alevel", "history_a2",
    "geography_a2", "religious_studies_a2", "psychology_alevel", "sociology_alevel",
    "geology_a2", "english_language_a2", "english_literature_a2", "welsh_language_a2",
    "welsh_literature_a2", "welsh_second_language_a2", "french_a2", "german_a2",
    "spanish_a2", "italian_a2", "physics_a2", "chemistry_a2", "biology_a2",
    "mathematics_a2", "further_mathematics_a2", "design_technology_a2",
    "art_and_design_a2", "media_studies_a2", "computer_science_a2", "music_a2",
    "physical_education_a2", "drama_a2", "health_and_social_care_a2",
)

WALES_LEVELS: tuple[str, ...] = ("gcse", "a_level")


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


def _build_wales_unions() -> str:
    """Build the UNION ALL clauses for the 160 Wales cohorts."""
    unions = []
    for level in WALES_LEVELS:
        for subject in WALES_SUBJECTS:
            unions.append(
                f"SELECT '{level}' AS level, '{subject}' AS subject, * "
                f"FROM cianfhoghlaim.education.wales.{level}.{subject}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


DIVE_SQL = f"""
WITH wales_cohorts AS (
    {_build_wales_unions()}
)
SELECT
    level,
    subject,
    is_welsh_medium,
    topic,
    topic_label_en,
    COUNT(*) AS n_mentions,
    AVG(ragas_score) AS avg_ragas_score
FROM wales_cohorts
WHERE level IN ('gcse', 'a_level')
GROUP BY level, subject, is_welsh_medium, topic, topic_label_en
ORDER BY level, subject, n_mentions DESC
"""


WALES_CURRICULUM_TOPICS_DIVE = DiveSpec(
    name="wales_curriculum_topics",
    description=(
        "BIEP v3 — Wales (WJEC) curriculum topic + learning-outcome "
        "frequency per subject per level (80 subjects × 2 levels = 160 "
        "cohorts). Read from the canonical BIEP v3 namespace "
        "`cianfhoghlaim.education.wales.<level>.<subject>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Topic distribution per Wales subject (bar chart, all 2 levels)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "subject",
            "color": "level",
        },
        {
            "type": "histogram",
            "title": "RAGAS score distribution: Welsh-medium vs English-medium",
            "x": "avg_ragas_score",
            "y": "n_mentions",
            "color": "is_welsh_medium",
        },
    ],
    filters=[
        {"column": "level", "type": "multi_select", "options": list(WALES_LEVELS)},
        {"column": "subject", "type": "multi_select", "options": list(WALES_SUBJECTS)},
        {"column": "is_welsh_medium", "type": "select", "options": [True, False]},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return WALES_CURRICULUM_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {WALES_CURRICULUM_TOPICS_DIVE.name}")
        print(f"Description: {WALES_CURRICULUM_TOPICS_DIVE.description}")
        print(f"Charts: {len(WALES_CURRICULUM_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(WALES_CURRICULUM_TOPICS_DIVE.filters)}")
