"""meaisinfhoghlaim Converter Coverage Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 Converter Coverage Dive. Reads the 7 document converter
output and surfaces coverage by file format + per-converter success rate.

Dive name: ``meaisin_converter_coverage_dive``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.meaisin.converter.<name>.rows``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


CONVERTERS = (
    "docling",
    "marker",
    "unstructured",
    "deepseekocr",
    "pymupdf4llm",
    "curriculum_document",
    "pdf_factory",
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


DIVE_SQL = """
WITH converter_coverage AS (
    {' UNION ALL BY NAME '.join(
        f"SELECT '{c}' AS converter, "
        f"COUNT(*) AS row_count, "
        f"SUM(CASE WHEN conversion_status = 'success' THEN 1 ELSE 0 END) AS success_count, "
        f"AVG(quality_score) AS avg_quality_score, "
        f"AVG(conversion_latency_ms) AS avg_latency_ms "
        f"FROM cianfhoghlaim.education.meaisin.converter.{c}.rows"
        for c in CONVERTERS
    )}
)
SELECT * FROM converter_coverage
ORDER BY converter
"""


MEASIN_CONVERTER_COVERAGE_DIVE = DiveSpec(
    name="meaisin_converter_coverage_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim 7-converter coverage overview. "
        "Surfaces per-converter row count, success rate, quality score, "
        "and conversion latency."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Row count per converter (bar chart)",
            "x": "converter",
            "y": "row_count",
        },
        {
            "type": "histogram",
            "title": "Quality score per converter (histogram)",
            "x": "avg_quality_score",
            "y": "count",
            "facet": "converter",
        },
    ],
    filters=[
        {"column": "converter", "type": "multi_select", "options": list(CONVERTERS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_CONVERTER_COVERAGE_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_CONVERTER_COVERAGE_DIVE.name}")
        print(f"Description: {MEASIN_CONVERTER_COVERAGE_DIVE.description}")
        print(f"Charts: {len(MEASIN_CONVERTER_COVERAGE_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_CONVERTER_COVERAGE_DIVE.filters)}")
