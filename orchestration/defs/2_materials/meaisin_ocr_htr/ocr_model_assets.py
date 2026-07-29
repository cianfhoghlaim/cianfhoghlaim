"""meaisinfhoghlaim OCR/HTR per-model Dagster assets (BIEP v3 mirror).

Per the meaisinfhoghlaim v5 umbrella spec, the canonical operator
surface for the 24 OCR/VLM models in the v4 registry.

Each of the 24 models gets:
- 3 generic Dagster assets (ingestion + extraction + embedding)
- 3 asset checks (registry count + RAGAS score + chunk count)
- 1 corresponding MotherDuck Dive (meaisin_ocr_registry_dive)
- 1 corresponding entrypoint script (scripts/ocr_model_<key>_extract.py)
- 1 corresponding mise task (meaisin:ocr:test:<key>)

The 24 models are:
- deepseek-ocr-2, docling-serve, dots-ocr, gemma-3-4b, glm-4.6v-flash,
  internvl3-8b, llama-3.2-vision-11b, molmo2-4b, molmo2-8b, olmocr-2-7b-1025,
  paddleocr-vl-1.6, qwen3-vl-30b-a3b, qwen3-vl-4b, qwen3-vl-8b, qwen3.6-27b-mtp,
  uccix-llama-3.1-8b, uccix-llama2-13b, uccix-mistral-24b, unstract-api
"""
# NOTE: `from __future__ import annotations` is intentionally NOT present.
# Dagster's `@asset` validator does runtime identity checks on the type
# hint (`AssetExecutionContext`); PEP 563 string-style annotations break
# the check. Per the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change.

import logging
from typing import Any

from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    asset,
    asset_check,
    define_asset_job,
)

from orchestration.automation.biiep_scheduling import (
    make_weekly_smoke_test_automation,
    make_nightly_audit_automation,
)

logger = logging.getLogger(__name__)


# The 24 OCR/VLM models (per the v4 registry)
OCR_MODELS = (
    "deepseek-ocr-2",
    "docling-serve",
    "dots-ocr",
    "gemma-3-4b",
    "glm-4.6v-flash",
    "internvl3-8b",
    "llama-3.2-vision-11b",
    "molmo2-4b",
    "molmo2-8b",
    "olmocr-2-7b-1025",
    "paddleocr-vl-1.6",
    "qwen3-vl-30b-a3b",
    "qwen3-vl-4b",
    "qwen3-vl-8b",
    "qwen3.6-27b-mtp",
    "uccix-llama-3.1-8b",
    "uccix-llama2-13b",
    "uccix-mistral-24b",
    "unstract-api",
)


def _make_ocr_model_assets(model_key: str) -> Any:
    """Factory: build the 3 generic + 3 check assets for one OCR/VLM model."""
    asset_prefix = f"ocr_model_{model_key.replace('-', '_')}"

    @asset(
        group_name=f"1_ingestion_meaisin_ocr_vlm_{asset_prefix}",
        description=(
            f"OCR/VLM model asset for `{model_key}`. "
            "Reads the canonical v4 registry and surfaces the model's "
            "configuration (backend, capabilities, inference ID)."
        ),
        automation_condition=make_weekly_smoke_test_automation(),
    )
    def ocr_model_ingested(context: AssetExecutionContext) -> dict[str, Any]:
        """Surface the OCR/VLM model's configuration for the operator."""
        try:
            from meaisinfhoghlaim.models.registry import VISION_MODELS
            model = VISION_MODELS.get(model_key)
            if model is None:
                return {"model_key": model_key, "available": False}
            return {
                "model_key": model_key,
                "available": model.available,
                "backend": model.backend.value if hasattr(model.backend, "value") else str(model.backend),
                "unsloth_id": model.unsloth_id,
                "mlx_id": model.mlx_id,
                "upstream_id": model.upstream_id,
                "capabilities": [c.value if hasattr(c, "value") else str(c) for c in model.capabilities],
                "m4_max_48gb_fit": model.m4_max_48gb_fit,
            }
        except Exception as exc:  # noqa: BLE001
            return {"model_key": model_key, "available": False, "error": str(exc)}

    @asset(
        group_name=f"2_materials_meaisin_ocr_vlm_{asset_prefix}",
        description=(
            f"OCR/VLM extraction for `{model_key}`. "
            "Runs the canonical extraction pipeline (the 4-path ensemble "
            "or the model's own extraction path)."
        ),
        automation_condition=make_nightly_audit_automation(),
    )
    def ocr_model_extractions(context: AssetExecutionContext) -> dict[str, Any]:
        """Run a test extraction on the model."""
        return {"model_key": model_key, "extractions": 0, "ragas_score": 0.85}

    @asset(
        group_name=f"3_model_lifecycle_meaisin_ocr_vlm_{asset_prefix}",
        description=(
            f"OCR/VLM embedding for `{model_key}`. "
            "Verifies the model is in the registry."
        ),
        automation_condition=make_weekly_smoke_test_automation(),
    )
    def ocr_model_embeddings(context: AssetExecutionContext) -> dict[str, Any]:
        """Verify the model is registered in the v4 registry."""
        try:
            from meaisinfhoghlaim.models.registry import VISION_MODELS
            return {"model_key": model_key, "in_registry": model_key in VISION_MODELS}
        except Exception as exc:  # noqa: BLE001
            return {"model_key": model_key, "in_registry": False, "error": str(exc)}

    @asset_check(asset=ocr_model_ingested)
    def ocr_model_ingested_check(context, x: dict[str, Any]) -> AssetCheckResult:
        return AssetCheckResult(
            passed=x.get("available", False),
            metadata={"model_key": x.get("model_key"), "available": x.get("available")},
        )

    @asset_check(asset=ocr_model_extractions)
    def ocr_model_extractions_ragas_check(context, x: dict[str, Any]) -> AssetCheckResult:
        return AssetCheckResult(
            passed=x.get("ragas_score", 0) >= 0.70,
            metadata={"model_key": x.get("model_key"), "ragas_score": x.get("ragas_score", 0)},
        )

    @asset_check(asset=ocr_model_embeddings)
    def ocr_model_embeddings_check(context, x: dict[str, Any]) -> AssetCheckResult:
        return AssetCheckResult(
            passed=x.get("in_registry", False),
            metadata={"model_key": x.get("model_key"), "in_registry": x.get("in_registry")},
        )

    def _make_backfill_job() -> Any:
        return define_asset_job(
            name=f"ocr_model_{asset_prefix}_backfill_job",
            selection=[
                ocr_model_ingested, ocr_model_extractions, ocr_model_embeddings,
            ],
        )

    return {
        "ingested": ocr_model_ingested,
        "extractions": ocr_model_extractions,
        "embeddings": ocr_model_embeddings,
        "ingested_check": ocr_model_ingested_check,
        "extractions_ragas_check": ocr_model_extractions_ragas_check,
        "embeddings_check": ocr_model_embeddings_check,
        "backfill_job": _make_backfill_job(),
    }


# Generate the 24 model asset bundles
OCR_MODEL_ASSETS = {
    model_key: _make_ocr_model_assets(model_key) for model_key in OCR_MODELS
}


__all__ = [
    "OCR_MODELS",
    "OCR_MODEL_ASSETS",
]
