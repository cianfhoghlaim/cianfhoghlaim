"""meaisinfhoghlaim OCR Registry Overview Dive — BIEP v3 MotherDuck Dive.

Per the meaisinfhoghlaim v5 umbrella spec.

The BIEP v3 OCR Registry Overview Dive. Reads the 24 OCR/VLM models
in the v4 registry and surfaces the per-model coverage by backend,
capability, and inference ID.

Dive name: ``meaisin_ocr_registry_dive``
DuckLake tables read:
  - ``md:cianfhoghlaim.education.meaisin.models.registry``
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
    key AS model_key,
    backend,
    unsloth_id,
    mlx_id,
    upstream_id,
    capabilities,
    m4_max_48gb_fit,
    available
FROM cianfhoghlaim.education.meaisin.models.registry
ORDER BY backend, key
"""


MEASIN_OCR_REGISTRY_DIVE = DiveSpec(
    name="meaisin_ocr_registry_dive",
    description=(
        "BIEP v3 — meaisinfhoghlaim OCR/VLM registry overview. "
        "Surfaces the 24-model × 4-backend coverage by inference ID, "
        "model capability, and M4 Max 48 GB fit."
    ),
    sql=DIVE_SQL,
    charts=[
        {
            "type": "bar",
            "title": "Model count per backend (bar chart)",
            "x": "backend",
            "y": "model_count",
        },
        {
            "type": "table",
            "title": "Per-model coverage (table)",
            "columns": ["model_key", "backend", "unsloth_id", "mlx_id", "upstream_id"],
        },
    ],
    filters=[
        {"column": "backend", "type": "multi_select", "options": ["litellm", "mlx", "transformers", "llama-swap"]},
        {"column": "model_key", "type": "multi_select", "options": list(OCR_MODELS)},
    ],
)


def save_dive_definition() -> dict[str, Any]:
    return MEASIN_OCR_REGISTRY_DIVE.to_dict()


if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(save_dive_definition(), indent=2))
    else:
        print(f"Dive: {MEASIN_OCR_REGISTRY_DIVE.name}")
        print(f"Description: {MEASIN_OCR_REGISTRY_DIVE.description}")
        print(f"Charts: {len(MEASIN_OCR_REGISTRY_DIVE.charts)}")
        print(f"Filters: {len(MEASIN_OCR_REGISTRY_DIVE.filters)}")
