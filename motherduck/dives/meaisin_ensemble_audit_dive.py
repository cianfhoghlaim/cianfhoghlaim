"""meaisinfhoghlaim Ensemble Audit Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 Ensemble Audit Dive. Reads the 4-path OCR ensemble output
(BAML + Unstract + qwen3-vl + gemma-4-26B-A4B) and surfaces RAGAS
scores per path.

Dive name: ``meaisin_ensemble_audit_dive``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.meaisin.ensemble.<path>.rows``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
WITH ensemble_runs AS (
    SELECT 'baml' AS path, AVG(ragas_score) AS avg_ragas, COUNT(*) AS run_count
    FROM cianfhoghlaim.education.meaisin.ensemble.baml.rows
    UNION ALL BY NAME
    SELECT 'unstract', AVG(ragas_score), COUNT(*)
    FROM cianfhoghlaim.education.meaisin.ensemble.unstract.rows
    UNION ALL BY NAME
    SELECT 'qwen3_vl', AVG(ragas_score), COUNT(*)
    FROM cianfhoghlaim.education.meaisin.ensemble.qwen3_vl.rows
    UNION ALL BY NAME
    SELECT 'gemma4', AVG(ragas_score), COUNT(*)
    FROM cianfhoghlaim.education.meaisin.ensemble.gemma4.rows
)
SELECT * FROM ensemble_runs
ORDER BY path
"""


MEASIN_ENSEMBLE_AUDIT_DIVE = DiveSpec(
    name="meaisin_ensemble_audit_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim 4-path OCR ensemble audit. "
        "Surfaces the RAGAS scores per path (BAML + Unstract + qwen3-vl + gemma-4-26B-A4B)."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Average RAGAS score per path (bar chart)",
            "x": "path",
            "y": "avg_ragas",
        },
        {
            "type": "bar",
            "title": "Run count per path (bar chart)",
            "x": "path",
            "y": "run_count",
        },
    ],
    filters=[],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_ENSEMBLE_AUDIT_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_ENSEMBLE_AUDIT_DIVE.name}")
        print(f"Description: {MEASIN_ENSEMBLE_AUDIT_DIVE.description}")
        print(f"Charts: {len(MEASIN_ENSEMBLE_AUDIT_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_ENSEMBLE_AUDIT_DIVE.filters)}")
