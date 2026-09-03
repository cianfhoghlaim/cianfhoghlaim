"""
England A-Level Curriculum Topics Dive — BIEP v3 MotherDuck Dive (M3).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 England A-Level Curriculum Topics Dive. Reads the 147
per-cohort DuckLake tables (49 subjects × 3 boards) and surfaces the
specification + learning-outcome frequency per board per subject
with RAGAS score histogram.

Dive name: ``england_a_level_topics``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.england.a_level.<board>.<subject>.voted_canonical``
  - ``md:cianfhoghlaim.education.england.a_level.<board>.<subject>.baml_canonical``
  - ``md:cianfhoghlaim.education.england.a_level.<board>.<subject>.qwen3_vl``
  - ``md:cianfhoghlaim.education.england.a_level.<board>.<subject>.gemma4``
  - ``md:cianfhoghlaim.education.england.a_level.<board>.<subject>.unstract_json``

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
openspec/specs/british-isles-education-pipeline-v3/spec.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The 3 England awarding boards
ENGLAND_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

# The 49 A-Level subjects (per baml_src/.../england/education/subject_taxonomy.baml)
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
    """Minimal MotherDuck Dive spec for the england_a_level_topics Dive."""

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


def _build_england_a_level_unions() -> str:
    """Build the UNION ALL clauses for the 147 A-Level cohorts (49 subjects × 3 boards)."""
    unions = []
    for board in ENGLAND_BOARDS:
        for subject in A_LEVEL_SUBJECTS:
            unions.append(
                f"SELECT '{board}' AS board, '{subject}' AS subject, * "
                f"FROM cianfhoghlaim.education.england.a_level.{board}.{subject}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


# The canonical SQL query for the BIEP v3 England A-Level Curriculum Topics Dive.
DIVE_SQL = f"""
WITH england_a_level_cohorts AS (
    {_build_england_a_level_unions()}
)
SELECT
    board,
    subject,
    topic,
    topic_label_en,
    COUNT(*) AS n_mentions,
    AVG(ragas_score) AS avg_ragas_score,
    AVG(total_marks) AS avg_total_marks
FROM england_a_level_cohorts
WHERE board IN ('aqa', 'ocr', 'edexcel')
GROUP BY board, subject, topic, topic_label_en
ORDER BY board, subject, n_mentions DESC
"""


# The canonical BIEP v3 England A-Level Dive spec.
ENGLAND_A_LEVEL_TOPICS_DIVE = DiveSpec(
    name="england_a_level_topics",
    description=(
        "BIEP v3 — England A-Level topic + learning-outcome frequency per "
        "board per subject (49 subjects × 3 boards = 147 cohorts). "
        "Read from the canonical BIEP v3 namespace "
        "`cianfhoghlaim.education.england.a_level.<board>.<subject>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Topic distribution per A-Level subject (bar chart, all 3 boards)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "subject",
            "color": "board",
        },
        {
            "type": "histogram",
            "title": "RAGAS score distribution per A-Level board",
            "x": "avg_ragas_score",
            "y": "n_mentions",
            "facet": "board",
        },
        {
            "type": "scatter",
            "title": "Total marks vs topic frequency per A-Level board",
            "x": "avg_total_marks",
            "y": "n_mentions",
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
    return ENGLAND_A_LEVEL_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {ENGLAND_A_LEVEL_TOPICS_DIVE.name}")
        print(f"Description: {ENGLAND_A_LEVEL_TOPICS_DIVE.description}")
        print(f"Charts: {len(ENGLAND_A_LEVEL_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(ENGLAND_A_LEVEL_TOPICS_DIVE.filters)}")
