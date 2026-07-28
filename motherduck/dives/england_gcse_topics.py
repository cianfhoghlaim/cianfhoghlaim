"""
England GCSE Curriculum Topics Dive — BIEP v3 MotherDuck Dive (M4).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 England GCSE Curriculum Topics Dive. Reads the 129
per-cohort DuckLake tables (43 subjects × 3 boards) and surfaces the
specification + learning-outcome frequency per board per subject
with RAGAS score histogram.

Dive name: ``england_gcse_topics``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.england.gcse.<board>.<subject>.voted_canonical``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

GCSE_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "english_language",
    "english_literature",
    "biology",
    "chemistry",
    "physics",
    "computer_science",
    "history",
    "geography",
    "religious_studies",
    "french",
    "german",
    "spanish",
    "latin",
    "classical_civilisation",
    "ancient_history",
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
    "food_preparation_nutrition",
    "further_mathematics",
    "statistics",
    "engineering",
    "electronics",
    "human_biology",
    "applied_business",
    "applied_ict",
    "applied_science_double",
    "applied_travel_tourism",
    "performing_arts",
    "statistics_9ma0",
    "geography_fieldwork",
    "environmental_science_team",
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
    unions = []
    for board in ENGLAND_BOARDS:
        for subject in GCSE_SUBJECTS:
            unions.append(
                f"SELECT '{board}' AS board, '{subject}' AS subject, * "
                f"FROM cianfhoghlaim.education.england.gcse.{board}.{subject}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


DIVE_SQL = f"""
WITH england_gcse_cohorts AS (
    {_build_unions()}
)
SELECT
    board,
    subject,
    topic,
    topic_label_en,
    COUNT(*) AS n_mentions,
    AVG(ragas_score) AS avg_ragas_score,
    AVG(total_marks) AS avg_total_marks
FROM england_gcse_cohorts
WHERE board IN ('aqa', 'ocr', 'edexcel')
GROUP BY board, subject, topic, topic_label_en
ORDER BY board, subject, n_mentions DESC
"""


ENGLAND_GCSE_TOPICS_DIVE = DiveSpec(
    name="england_gcse_topics",
    description=(
        "BIEP v3 — England GCSE topic + learning-outcome frequency per "
        "board per subject (43 subjects × 3 boards = 129 cohorts). "
        "Read from the canonical BIEP v3 namespace "
        "`cianfhoghlaim.education.england.gcse.<board>.<subject>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Topic distribution per GCSE subject (bar chart, all 3 boards)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "subject",
            "color": "board",
        },
        {
            "type": "histogram",
            "title": "RAGAS score distribution per GCSE board",
            "x": "avg_ragas_score",
            "y": "n_mentions",
            "facet": "board",
        },
    ],
    filters=[
        {"column": "board", "type": "multi_select", "options": list(ENGLAND_BOARDS)},
        {"column": "subject", "type": "multi_select", "options": list(GCSE_SUBJECTS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return ENGLAND_GCSE_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {ENGLAND_GCSE_TOPICS_DIVE.name}")
        print(f"Description: {ENGLAND_GCSE_TOPICS_DIVE.description}")
        print(f"Charts: {len(ENGLAND_GCSE_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(ENGLAND_GCSE_TOPICS_DIVE.filters)}")
