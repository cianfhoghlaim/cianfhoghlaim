"""
Ireland LC Syllabus Topics Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 Ireland LC Syllabus Topics Dive. Replaces the legacy
BIEP v1 `lc_syllabus_topics` Dive (which uses the pre-v7 `leaving_cert`
namespace) with the post-v3 BIEP namespace `cianfhoghlaim.education.
ireland.leaving_cycle.<subject>`.

The 12 M1 cohorts (6 subjects × 2 languages) are surfaced here as
the per-subject topic frequency breakdown.

Dive name: ``ireland_lc_syllabus_topics``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.ireland.leaving_cycle.<subject>.voted_canonical``
  - ``md:cianfhoghlaim.education.ireland.leaving_cycle.<subject>.baml_canonical``
  - ``md:cianfhoghlaim.education.ireland.leaving_cycle.<subject>.qwen3_vl``
  - ``md:cianfhoghlaim.education.ireland.leaving_cycle.<subject>.gemma4``
  - ``md:cianfhoghlaim.education.ireland.leaving_cycle.<subject>.unstract_json``

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
openspec/specs/british-isles-education-pipeline-v3/spec.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The 6 BIEP v1 priority LC subjects (canonical per BIEP v1).
BIEP_LC_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "chemistry",
    "geography",
    "gaeilge",
    "english",
    "computer_science",
)

# The 2 working languages (Ireland LC is bilingual EN + GA).
LC_LANGUAGES: tuple[str, ...] = ("en", "ga")


@dataclass
class DiveSpec:
    """Minimal MotherDuck Dive spec for the ireland_lc_syllabus_topics Dive."""

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


# The canonical SQL query for the BIEP v3 Ireland LC Syllabus Topics Dive.
# Reads the 12 per-cohort DuckLake tables (6 subjects × 2 languages) and
# unions them into a single topic frequency breakdown.
DIVE_SQL = """
WITH ireland_lc_cohorts AS (
    SELECT 'mathematics'        AS subject, 'higher' AS level, 'en' AS language, * FROM cianfhoghlaim.education.ireland.leaving_cycle.mathematics.higher_en.voted_canonical
    UNION ALL BY NAME
    SELECT 'mathematics', 'higher', 'ga', * FROM cianfhoghlaim.education.ireland.leaving_cycle.mathematics.higher_ga.voted_canonical
    UNION ALL BY NAME
    SELECT 'chemistry',  'higher', 'en', * FROM cianfhoghlaim.education.ireland.leaving_cycle.chemistry.higher_en.voted_canonical
    UNION ALL BY NAME
    SELECT 'chemistry',  'higher', 'ga', * FROM cianfhoghlaim.education.ireland.leaving_cycle.chemistry.higher_ga.voted_canonical
    UNION ALL BY NAME
    SELECT 'geography',  'higher', 'en', * FROM cianfhoghlaim.education.ireland.leaving_cycle.geography.higher_en.voted_canonical
    UNION ALL BY NAME
    SELECT 'geography',  'higher', 'ga', * FROM cianfhoghlaim.education.ireland.leaving_cycle.geography.higher_ga.voted_canonical
    UNION ALL BY NAME
    SELECT 'gaeilge',    'higher', 'ga', * FROM cianfhoghlaim.education.ireland.leaving_cycle.gaeilge.higher_ga.voted_canonical
    UNION ALL BY NAME
    SELECT 'english',    'higher', 'en', * FROM cianfhoghlaim.education.ireland.leaving_cycle.english.higher_en.voted_canonical
    UNION ALL BY NAME
    SELECT 'english',    'higher', 'ga', * FROM cianfhoghlaim.education.ireland.leaving_cycle.english.higher_ga.voted_canonical
    UNION ALL BY NAME
    SELECT 'computer_science', 'higher', 'en', * FROM cianfhoghlaim.education.ireland.leaving_cycle.computer_science.higher_en.voted_canonical
    UNION ALL BY NAME
    SELECT 'computer_science', 'higher', 'ga', * FROM cianfhoghlaim.education.ireland.leaving_cycle.computer_science.higher_ga.voted_canonical
)
SELECT
    subject,
    level,
    language,
    topic,
    topic_label_en,
    topic_label_ga,
    COUNT(*) AS n_mentions,
    AVG(ragas_score) AS avg_ragas_score
FROM ireland_lc_cohorts
WHERE subject IN ('mathematics', 'chemistry', 'geography', 'gaeilge', 'english', 'computer_science')
  AND language IN ('en', 'ga')
GROUP BY subject, level, language, topic, topic_label_en, topic_label_ga
ORDER BY subject, language, n_mentions DESC
"""


# The canonical BIEP v3 Ireland LC Dive spec.
IRELAND_LC_SYLLABUS_TOPICS_DIVE = DiveSpec(
    name="ireland_lc_syllabus_topics",
    description=(
        "BIEP v3 — Ireland LC topic frequency per subject per language "
        "(EN + GA), with RAGAS score histogram. Read from the canonical "
        "BIEP v3 namespace `cianfhoghlaim.education.ireland.leaving_cycle."
        "<subject>.<level>_<lang>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Topic distribution per subject (bar chart, EN + GA)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "subject",
            "color": "language",
        },
        {
            "type": "histogram",
            "title": "RAGAS score distribution per cohort",
            "x": "avg_ragas_score",
            "y": "n_mentions",
            "facet": "subject",
        },
    ],
    filters=[
        {"column": "subject", "type": "multi_select", "options": list(BIEP_LC_SUBJECTS)},
        {"column": "language", "type": "multi_select", "options": list(LC_LANGUAGES)},
        {"column": "level", "type": "multi_select", "options": ["higher", "ordinary", "foundation"]},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    """Return the Dive spec as a JSON-serialisable dict for save_dive()."""
    return IRELAND_LC_SYLLABUS_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {IRELAND_LC_SYLLABUS_TOPICS_DIVE.name}")
        print(f"Description: {IRELAND_LC_SYLLABUS_TOPICS_DIVE.description}")
        print(f"Charts: {len(IRELAND_LC_SYLLABUS_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(IRELAND_LC_SYLLABUS_TOPICS_DIVE.filters)}")
