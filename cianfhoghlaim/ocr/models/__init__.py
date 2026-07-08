"""Canonical v4 home for the OCR/VLM model registry.

Per the v4 platform spec line 685, the canonical home for the
OCR/VLM model registry is `cianfhoghlaim/ocr/models/registry.py`.
This `__init__.py` re-exports the symbols from `registry.py` so
callers can do:

    from cianfhoghlaim.ocr.models import (
        VISION_MODELS,
        get_default_for_m4_max,
        select_ocr_backend,
    )

The legacy `OCR_MODELS` and `VLM_MODELS` aliases are also exposed
for back-compat with pre-v4 callers (they collapse to the v4
`VISION_MODELS` dict).
"""

from __future__ import annotations

from cianfhoghlaim.ocr.models.registry import (
    CLASSICAL_OCR,
    MODEL_BACKEND,
    MODEL_CAPABILITY,
    TEXT_MODELS,
    VISION_MODELS,
    ClassicalOCRStack,
    ModelBackend,
    ModelCapability,
    ModelRegistry,
    ModelRole,
    OCRAwareSelection,
    OCRModel,
    all_classical_stacks,
    all_models,
    get_default_for_m4_max,
    get_optimal_for_m4,
    get_optimal_for_m4_id,
    select_ocr_backend,
)

# Legacy back-compat aliases (the pre-v4 OCR/VLM registries).
# Pre-v4, the lakehouse had two separate dicts — `OCR_MODELS` (10
# entries) and `VLM_MODELS` (6 entries). The v4 registry collapses
# them into a single 20-entry `VISION_MODELS` dict. These shims
# make old code keep working.
OCR_MODELS = VISION_MODELS
VLM_MODELS = VISION_MODELS

__all__ = [
    "CLASSICAL_OCR",
    "MODEL_BACKEND",
    "MODEL_CAPABILITY",
    "OCR_MODELS",
    "TEXT_MODELS",
    "VISION_MODELS",
    "VLM_MODELS",
    "ClassicalOCRStack",
    "ModelBackend",
    "ModelCapability",
    "ModelRegistry",
    "ModelRole",
    "OCRAwareSelection",
    "OCRModel",
    "all_classical_stacks",
    "all_models",
    "get_default_for_m4_max",
    "get_optimal_for_m4",
    "get_optimal_for_m4_id",
    "select_ocr_backend",
]
