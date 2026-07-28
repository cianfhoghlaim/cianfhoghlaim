"""meaisinfhoghlaim Converter Quality Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 Converter Quality Dive. Surfaces conversion quality
(text accuracy, table detection rate, OCR confidence) per converter.

Dive name: ``meaisin_converter_quality_dive``
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
WITH converter_quality AS (
    {' UNION ALL BY NAME '.join(
        f"SELECT '{c}' AS converter, "
        f"AVG(text_accuracy) AS avg_text_accuracy, "
        f"AVG(table_detection_rate) AS avg_table_detection_rate, "
        f"AVG(ocr_confidence) AS avg_ocr_confidence, "
        f"COUNT(*) AS sample_count "
        f"FROM cianfhoghlaim.education.meaisin.converter.{c}.rows"
        for c in CONVERTERS
    )}
)
SELECT * FROM converter_quality
ORDER BY avg_text_accuracy DESC
"""


MEASIN_CONVERTER_QUALITY_DIVE = DiveSpec(
    name="meaisin_converter_quality_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim 7-converter quality overview. "
        "Surfaces per-converter text accuracy, table detection rate, "
        "and OCR confidence."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Text accuracy per converter (bar chart)",
            "x": "converter",
            "y": "avg_text_accuracy",
        },
        {
            "type": "bar",
            "title": "Table detection rate per converter (bar chart)",
            "x": "converter",
            "y": "avg_table_detection_rate",
        },
        {
            "type": "bar",
            "title": "OCR confidence per converter (bar chart)",
            "x": "converter",
            "y": "avg_ocr_confidence",
        },
    ],
    filters=[
        {"column": "converter", "type": "multi_select", "options": list(CONVERTERS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_CONVERTER_QUALITY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_CONVERTER_QUALITY_DIVE.name}")
        print(f"Description: {MEASIN_CONVERTER_QUALITY_DIVE.description}")
        print(f"Charts: {len(MEASIN_CONVERTER_QUALITY_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_CONVERTER_QUALITY_DIVE.filters)}")
