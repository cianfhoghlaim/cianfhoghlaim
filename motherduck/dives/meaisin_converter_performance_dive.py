"""meaisinfhoghlaim Converter Performance Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 Converter Performance Dive. Surfaces conversion performance
(avg latency, throughput) per converter.

Dive name: ``meaisin_converter_performance_dive``
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
WITH converter_performance AS (
    {' UNION ALL BY NAME '.join(
        f"SELECT '{c}' AS converter, "
        f"AVG(conversion_latency_ms) AS avg_latency_ms, "
        f"MIN(conversion_latency_ms) AS min_latency_ms, "
        f"MAX(conversion_latency_ms) AS max_latency_ms, "
        f"COUNT(*) AS throughput "
        f"FROM cianfhoghlaim.education.meaisin.converter.{c}.rows"
        for c in CONVERTERS
    )}
)
SELECT * FROM converter_performance
ORDER BY avg_latency_ms ASC
"""


MEASIN_CONVERTER_PERFORMANCE_DIVE = DiveSpec(
    name="meaisin_converter_performance_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim 7-converter performance overview. "
        "Surfaces per-converter latency (avg / min / max) and throughput."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Average conversion latency per converter (bar chart)",
            "x": "converter",
            "y": "avg_latency_ms",
        },
        {
            "type": "bar",
            "title": "Throughput per converter (bar chart)",
            "x": "converter",
            "y": "throughput",
        },
    ],
    filters=[
        {"column": "converter", "type": "multi_select", "options": list(CONVERTERS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_CONVERTER_PERFORMANCE_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_CONVERTER_PERFORMANCE_DIVE.name}")
        print(f"Description: {MEASIN_CONVERTER_PERFORMANCE_DIVE.description}")
        print(f"Charts: {len(MEASIN_CONVERTER_PERFORMANCE_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_CONVERTER_PERFORMANCE_DIVE.filters)}")
