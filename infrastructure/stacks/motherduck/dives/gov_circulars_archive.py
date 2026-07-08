"""
Education Circulars Dive — BIEP v1 MotherDuck Dive (definition + dashboard).

A live MotherDuck dashboard for `gov.ie` education circulars by dept +
year + subject area. Filterable by dept (DES / NCCA / SEC / DoE) and
language (en / ga).

Drill-down: click a circular → view summary + full text + linked
syllabuses (from `oideachais.government.circular_to_syllabus`).

Dive name: ``gov_circulars_archive``
DuckLake tables read:
  - ``md:oideachais.government.circulars``
  - ``md:oideachais.government.circular_to_syllabus``

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# The 4 government departments that issue education circulars.
GOV_DEPTS: tuple[str, ...] = ("DES", "NCCA", "SEC", "DOE_NI")


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
SELECT
    c.circular_id,
    c.dept,
    c.subject_area,
    c.year,
    c.language,
    c.title_en,
    c.title_ga,
    c.summary,
    c.url,
    c.published_at,
    c.extraction_confidence,
    count(l.circular_id) AS n_linked_syllabi,
    array_agg(DISTINCT l.syllabus_subject) AS linked_subjects,
    array_agg(DISTINCT l.link_type) AS link_types
FROM oideachais.government.circulars c
LEFT JOIN oideachais.government.circular_to_syllabus l
       ON c.circular_id = l.circular_id
WHERE c.dept IN ('DES', 'NCCA', 'SEC', 'DOE_NI')
  AND c.language IN ('en', 'ga')
GROUP BY c.circular_id, c.dept, c.subject_area, c.year, c.language,
         c.title_en, c.title_ga, c.summary, c.url, c.published_at, c.extraction_confidence
ORDER BY c.published_at DESC
"""


GOV_CIRCULARS_ARCHIVE_DIVE = DiveSpec(
    name="gov_circulars_archive",
    description=(
        "BIEP v1 — `gov.ie` circulars by dept + year + subject area. "
        "Filterable by dept (DES / NCCA / SEC / DoE) and language (en/ga). "
        "Drill-down: click a circular → view summary + full text + linked "
        "NCCA syllabuses."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Circulars per year per dept (bar chart)",
            "x": "year",
            "y": "n_circulars",
            "color": "dept",
        },
        {
            "type": "pie",
            "title": "Circulars by subject area (pie chart)",
            "x": "subject_area",
            "y": "n_circulars",
        },
        {
            "type": "table",
            "title": "Most recent circulars (table)",
            "columns": [
                "circular_id", "dept", "year", "subject_area",
                "title_en", "title_ga", "n_linked_syllabi",
            ],
        },
    ],
    filters=[
        {"column": "dept", "type": "multi_select", "options": list(GOV_DEPTS)},
        {"column": "subject_area", "type": "multi_select", "options": [
            "MATHEMATICS", "CHEMISTRY", "GEOGRAPHY", "GAEILGE",
            "ENGLISH", "COMPUTER_SCIENCE", "CROSS_SUBJECT",
            "SCHOOL_ADMINISTRATION", "INFRASTRUCTURE", "GENERAL",
        ]},
        {"column": "language", "type": "multi_select", "options": ["en", "ga"]},
        {"column": "year", "type": "range", "min": 2010, "max": 2026},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    """Return the Dive spec as a JSON-serialisable dict for save_dive()."""
    return GOV_CIRCULARS_ARCHIVE_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {GOV_CIRCULARS_ARCHIVE_DIVE.name}")
        print(f"Description: {GOV_CIRCULARS_ARCHIVE_DIVE.description}")
        print(f"Charts: {len(GOV_CIRCULARS_ARCHIVE_DIVE.charts)}")
        print(f"Filters: {len(GOV_CIRCULARS_ARCHIVE_DIVE.filters)}")
