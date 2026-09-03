"""meaisinfhoghlaim Evaluation Summary Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 Evaluation Summary Dive. Reads the RAGAS BIEP ensemble output
and surfaces the quality metrics across the 24 OCR/VLM models.

Dive name: ``meaisin_evaluation_summary_dive``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.meaisin.evaluation.ragas_results``
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


OCR_MODELS = (
    "deepseek-ocr-2", "docling-serve", "dots-ocr", "gemma-3-4b",
    "glm-4.6v-flash", "internvl3-8b", "llama-3.2-vision-11b", "molmo2-4b",
    "molmo2-8b", "olmocr-2-7b-1025", "paddleocr-vl-1.6", "qwen3-vl-30b-a3b",
    "qwen3-vl-4b", "qwen3-vl-8b", "qwen3.6-27b-mtp", "uccix-llama-3.1-8b",
    "uccix-llama2-13b", "uccix-mistral-24b", "unstract-api",
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
SELECT
    model_key,
    AVG(ragas_score) AS avg_ragas_score,
    AVG(extraction_latency_ms) AS avg_latency_ms,
    COUNT(*) AS run_count
FROM cianfhoghlaim.education.meaisin.evaluation.ragas_results
WHERE model_key IN ('deepseek-ocr-2', 'docling-serve', 'dots-ocr', 'gemma-3-4b',
                      'glm-4.6v-flash', 'internvl3-8b', 'llama-3.2-vision-11b', 'molmo2-4b',
                      'molmo2-8b', 'olmocr-2-7b-1025', 'paddleocr-vl-1.6', 'qwen3-vl-30b-a3b',
                      'qwen3-vl-4b', 'qwen3-vl-8b', 'qwen3.6-27b-mtp', 'uccix-llama-3.1-8b',
                      'uccix-llama2-13b', 'uccix-mistral-24b', 'unstract-api')
GROUP BY model_key
ORDER BY avg_ragas_score DESC
"""


MEASIN_EVALUATION_SUMMARY_DIVE = DiveSpec(
    name="meaisin_evaluation_summary_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim RAGAS evaluation summary. "
        "Surfaces the quality metrics (avg RAGAS score, avg latency, run count) "
        "across the 24 OCR/VLM models."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Average RAGAS score per model (bar chart)",
            "x": "model_key",
            "y": "avg_ragas_score",
        },
        {
            "type": "bar",
            "title": "Average extraction latency per model (bar chart)",
            "x": "model_key",
            "y": "avg_latency_ms",
        },
    ],
    filters=[
        {"column": "model_key", "type": "multi_select", "options": list(OCR_MODELS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_EVALUATION_SUMMARY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_EVALUATION_SUMMARY_DIVE.name}")
        print(f"Description: {MEASIN_EVALUATION_SUMMARY_DIVE.description}")
        print(f"Charts: {len(MEASIN_EVALUATION_SUMMARY_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_EVALUATION_SUMMARY_DIVE.filters)}")
