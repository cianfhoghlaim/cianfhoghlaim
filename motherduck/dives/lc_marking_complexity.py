"""
Marking Scheme Complexity Dive — BIEP v1 MotherDuck Dive (definition + dashboard).

A live MotherDuck dashboard for per-subject per-topic average
descriptor count + grade-band distribution.

Drill-down: click a topic → view the full marking scheme text for
the years it appeared.

Dive name: ``lc_marking_complexity``
DuckLake tables read:
  - ``md:cianfhoghlaim.leaving_cert.<subject>_marking``

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .lc_syllabus_topics import BIEP_SUBJECTS


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


DIVE_SQL = """
WITH marking_union AS (
    SELECT subject, year, level, language, topic, band,
           cardinality(descriptor_text_en) AS descriptor_word_count
    FROM cianfhoghlaim.leaving_cert.mathematics_marking
    UNION ALL BY NAME
    SELECT subject, year, level, language, topic, band,
           cardinality(descriptor_text_en)
    FROM cianfhoghlaim.leaving_cert.chemistry_marking
    UNION ALL BY NAME
    SELECT subject, year, level, language, topic, band,
           cardinality(descriptor_text_en)
    FROM cianfhoghlaim.leaving_cert.geography_marking
    UNION ALL BY NAME
    SELECT subject, year, level, language, topic, band,
           cardinality(descriptor_text_en)
    FROM cianfhoghlaim.leaving_cert.english_marking
    UNION ALL BY NAME
    SELECT subject, year, level, language, topic, band,
           cardinality(descriptor_text_en)
    FROM cianfhoghlaim.leaving_cert.gaeilge_marking
    UNION ALL BY NAME
    SELECT subject, year, level, language, topic, band,
           cardinality(descriptor_text_en)
    FROM cianfhoghlaim.leaving_cert.computer_science_marking
)
SELECT
    subject,
    topic,
    level,
    language,
    band,
    year,
    count(*) AS n_descriptors,
    avg(descriptor_word_count) AS avg_descriptor_word_count,
    max(year) AS most_recent_year
FROM marking_union
WHERE subject IN ('mathematics', 'chemistry', 'geography', 'gaeilge', 'english', 'computer_science')
GROUP BY subject, topic, level, language, band, year
ORDER BY subject, topic, band
"""


LC_MARKING_COMPLEXITY_DIVE = DiveSpec(
    name="lc_marking_complexity",
    description=(
        "BIEP v1 — Per-subject per-topic average descriptor count + "
        "grade-band distribution. Drill-down: click a topic → view the "
        "full marking scheme text for the years it appeared."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "heatmap",
            "title": "Marking scheme complexity per subject per topic (heatmap)",
            "x": "topic",
            "y": "subject",
            "value": "n_descriptors",
        },
        {
            "type": "bar",
            "title": "Grade-band distribution per subject (bar chart)",
            "x": "band",
            "y": "n_descriptors",
            "color": "band",
            "facet": "subject",
        },
    ],
    filters=[
        {"column": "subject", "type": "multi_select", "options": list(BIEP_SUBJECTS)},
        {"column": "level", "type": "multi_select", "options": ["hl", "ol", "fl"]},
        {"column": "language", "type": "multi_select", "options": ["en", "ga"]},
        {"column": "year", "type": "range", "min": 1990, "max": 2026},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    """Return the Dive spec as a JSON-serialisable dict for save_dive()."""
    return LC_MARKING_COMPLEXITY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {LC_MARKING_COMPLEXITY_DIVE.name}")
        print(f"Description: {LC_MARKING_COMPLEXITY_DIVE.description}")
        print(f"Charts: {len(LC_MARKING_COMPLEXITY_DIVE.charts)}")
        print(f"Filters: {len(LC_MARKING_COMPLEXITY_DIVE.filters)}")
