"""
Syllabus Topics Dive — BIEP v1 MotherDuck Dive (definition + dashboard).

A live MotherDuck dashboard for topic frequency per LC subject per
year, filterable by level (Higher / Ordinary / Foundation) and
language (en / ga).

Drill-down: click a topic → list the syllabuses that mention it +
the years it appeared in exams.

Dive name: ``lc_syllabus_topics``
DuckLake tables read:
  - ``md:oideachais.leaving_cert.<subject>_topics``
  - ``md:oideachais.leaving_cert.<subject>_syllabus``

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The 6 BIEP v1 priority LC subjects.
BIEP_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "chemistry",
    "geography",
    "gaeilge",
    "english",
    "computer_science",
)

# The 3 LC levels.
LC_LEVELS: tuple[str, ...] = ("higher", "ordinary", "foundation")

# The 2 working languages.
LC_LANGUAGES: tuple[str, ...] = ("en", "ga")


@dataclass
class DiveSpec:
    """Minimal MotherDuck Dive spec for the lc_syllabus_topics Dive."""

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


# The canonical SQL query for the dive.
DIVE_SQL = """
WITH syllabus_topics AS (
    SELECT
        'mathematics'    AS subject, year, level, language, topic, topic_label_en, topic_label_ga
    FROM oideachais.leaving_cert.mathematics_topics
    UNION ALL BY NAME
    SELECT 'chemistry',    year, level, language, topic, topic_label_en, topic_label_ga
    FROM oideachais.leaving_cert.chemistry_topics
    UNION ALL BY NAME
    SELECT 'geography',    year, level, language, topic, topic_label_en, topic_label_ga
    FROM oideachais.leaving_cert.geography_topics
    UNION ALL BY NAME
    SELECT 'gaeilge',      year, level, language, topic, topic_label_en, topic_label_ga
    FROM oideachais.leaving_cert.gaeilge_topics
    UNION ALL BY NAME
    SELECT 'english',      year, level, language, topic, topic_label_en, topic_label_ga
    FROM oideachais.leaving_cert.english_topics
    UNION ALL BY NAME
    SELECT 'computer_science', year, level, language, topic, topic_label_en, topic_label_ga
    FROM oideachais.leaving_cert.computer_science_topics
)
SELECT
    subject,
    year,
    level,
    language,
    topic,
    topic_label_en,
    topic_label_ga,
    count(*) AS n_mentions
FROM syllabus_topics
WHERE subject IN ('mathematics', 'chemistry', 'geography', 'gaeilge', 'english', 'computer_science')
  AND level   IN ('higher', 'ordinary', 'foundation')
  AND language IN ('en', 'ga')
GROUP BY subject, year, level, language, topic, topic_label_en, topic_label_ga
ORDER BY subject, year, n_mentions DESC
"""


# The canonical Dive spec.
LC_SYLLABUS_TOPICS_DIVE = DiveSpec(
    name="lc_syllabus_topics",
    description=(
        "BIEP v1 — Topic frequency per LC subject per year, "
        "filterable by level (Higher/Ordinary/Foundation) and language (en/ga). "
        "Drill-down: click a topic → list the syllabuses that mention it + "
        "the years it appeared in exams."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "line",
            "title": "Topic frequency per year (line chart)",
            "x": "year",
            "y": "n_mentions",
            "color": "topic",
            "facet": "subject",
        },
        {
            "type": "bar",
            "title": "Topic distribution per subject (bar chart)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "subject",
        },
    ],
    filters=[
        {"column": "subject", "type": "multi_select", "options": list(BIEP_SUBJECTS)},
        {"column": "level", "type": "multi_select", "options": list(LC_LEVELS)},
        {"column": "language", "type": "multi_select", "options": list(LC_LANGUAGES)},
        {"column": "year", "type": "range", "min": 2010, "max": 2026},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    """Return the Dive spec as a JSON-serialisable dict for save_dive()."""
    return LC_SYLLABUS_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {LC_SYLLABUS_TOPICS_DIVE.name}")
        print(f"Description: {LC_SYLLABUS_TOPICS_DIVE.description}")
        print(f"Charts: {len(LC_SYLLABUS_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(LC_SYLLABUS_TOPICS_DIVE.filters)}")
