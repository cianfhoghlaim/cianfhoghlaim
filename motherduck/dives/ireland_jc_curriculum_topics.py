"""
Ireland JC Curriculum Topics Dive — BIEP v3 MotherDuck Dive.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The BIEP v3 Ireland JC Curriculum Topics Dive. Reads the 88 per-cohort
DuckLake tables (36 specs + 16 short courses + 36 CBAs) and surfaces
the topic + learning-outcome frequency per JC subject per language
with RAGAS score histogram.

Dive name: ``ireland_jc_curriculum_topics``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.ireland.junior_cycle.<subject>.<lang>.voted_canonical``
  - ``md:cianfhoghlaim.education.ireland.junior_cycle.short_courses.<code>.voted_canonical``
  - ``md:cianfhoghlaim.education.ireland.junior_cycle.cbas.<cba_id>.voted_canonical``

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
openspec/specs/british-isles-education-pipeline-v3/spec.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# The 18 NCCA JC subjects (canonical from JC_SUBJECTS in dlt_sources/.../junior_cycle.py)
JC_SUBJECTS: tuple[str, ...] = (
    "english",
    "gaeilge",
    "mathematics",
    "irish_history",
    "geography",
    "science",
    "business_studies",
    "french",
    "german",
    "spanish",
    "italian",
    "home_economics",
    "music",
    "art",
    "technology",
    "engineering",
    "graphics",
    "wood_technology",
)

# 16 NCCA JC short courses
JC_SHORT_COURSES: tuple[str, ...] = (
    "coding",
    "chinese",
    "japanese",
    "russian",
    "polish",
    "lithuanian",
    "portuguese",
    "arabic",
    "hebrew",
    "philosophy",
    "film_studies",
    "financial_literacy",
    "media_literacy",
    "personal_professional_development",
    "digital_media",
    "athletic_studies",
)

JC_LANGUAGES: tuple[str, ...] = ("en", "ga")


@dataclass
class DiveSpec:
    """Minimal MotherDuck Dive spec for the ireland_jc_curriculum_topics Dive."""

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


# Build the UNION ALL query for the 88 cohort tables (36 specs + 16 short courses + 36 CBAs).
def _build_jc_specs_unions() -> str:
    """Build the UNION ALL clauses for the 36 JC specification cohorts."""
    unions = []
    for subject in JC_SUBJECTS:
        for language in JC_LANGUAGES:
            unions.append(
                f"SELECT 'spec' AS cohort_kind, '{subject}' AS subject, NULL AS cba_id, NULL AS short_course_code, '{language}' AS language, * "
                f"FROM cianfhoghlaim.education.ireland.junior_cycle.{subject}.{language}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


def _build_jc_short_courses_unions() -> str:
    """Build the UNION ALL clauses for the 16 JC short course cohorts."""
    unions = []
    for code in JC_SHORT_COURSES:
        unions.append(
            f"SELECT 'short_course' AS cohort_kind, NULL AS subject, NULL AS cba_id, '{code}' AS short_course_code, 'en' AS language, * "
            f"FROM cianfhoghlaim.education.ireland.junior_cycle.short_courses.{code}.voted_canonical"
        )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


def _build_jc_cbas_unions() -> str:
    """Build the UNION ALL clauses for the 36 JC CBA cohorts."""
    unions = []
    for subject in JC_SUBJECTS:
        for cba_idx in range(2):
            cba_id = f"{subject}_{cba_idx + 1}"
            unions.append(
                f"SELECT 'cba' AS cohort_kind, '{subject}' AS subject, '{cba_id}' AS cba_id, NULL AS short_course_code, 'en' AS language, * "
                f"FROM cianfhoghlaim.education.ireland.junior_cycle.cbas.{cba_id}.voted_canonical"
            )
    return "\n    UNION ALL BY NAME\n    ".join(unions)


# The canonical SQL query for the BIEP v3 Ireland JC Curriculum Topics Dive.
# Reads the 88 per-cohort DuckLake tables and surfaces topic + learning
# outcome frequency.
DIVE_SQL = f"""
WITH ireland_jc_cohorts AS (
    {_build_jc_specs_unions()}

    UNION ALL BY NAME
    {_build_jc_short_courses_unions()}

    UNION ALL BY NAME
    {_build_jc_cbas_unions()}
)
SELECT
    cohort_kind,
    COALESCE(subject, short_course_code, cba_id) AS cohort_label,
    subject,
    cba_id,
    short_course_code,
    language,
    topic,
    topic_label_en,
    topic_label_ga,
    COUNT(*) AS n_mentions,
    AVG(ragas_score) AS avg_ragas_score
FROM ireland_jc_cohorts
GROUP BY cohort_kind, subject, cba_id, short_course_code, language, topic, topic_label_en, topic_label_ga
ORDER BY cohort_kind, subject, n_mentions DESC
"""


# The canonical BIEP v3 Ireland JC Dive spec.
IRELAND_JC_CURRICULUM_TOPICS_DIVE = DiveSpec(
    name="ireland_jc_curriculum_topics",
    description=(
        "BIEP v3 — Ireland Junior Cycle topic + learning-outcome frequency per "
        "cohort (36 specs × 2 langs + 16 short courses + 36 CBAs = 88 cohorts). "
        "Read from the canonical BIEP v3 namespace "
        "`cianfhoghlaim.education.ireland.junior_cycle.<cohort>.voted_canonical`."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Topic distribution per JC cohort (bar chart)",
            "x": "topic",
            "y": "n_mentions",
            "facet": "cohort_label",
            "color": "language",
        },
        {
            "type": "histogram",
            "title": "RAGAS score distribution per JC cohort",
            "x": "avg_ragas_score",
            "y": "n_mentions",
            "facet": "cohort_kind",
        },
    ],
    filters=[
        {"column": "cohort_kind", "type": "multi_select", "options": ["spec", "short_course", "cba"]},
        {"column": "language", "type": "multi_select", "options": list(JC_LANGUAGES)},
        {"column": "subject", "type": "multi_select", "options": list(JC_SUBJECTS)},
        {"column": "short_course_code", "type": "multi_select", "options": list(JC_SHORT_COURSES)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    """Return the Dive spec as a JSON-serialisable dict for save_dive()."""
    return IRELAND_JC_CURRICULUM_TOPICS_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {IRELAND_JC_CURRICULUM_TOPICS_DIVE.name}")
        print(f"Description: {IRELAND_JC_CURRICULUM_TOPICS_DIVE.description}")
        print(f"Charts: {len(IRELAND_JC_CURRICULUM_TOPICS_DIVE.charts)}")
        print(f"Filters: {len(IRELAND_JC_CURRICULUM_TOPICS_DIVE.filters)}")
