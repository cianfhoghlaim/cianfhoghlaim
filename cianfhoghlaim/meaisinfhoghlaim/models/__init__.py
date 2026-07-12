"""Canonical v4 home for the OCR/VLM model registry (the outer models package).

The v4 platform convention is to keep the OCR/VLM model registry at
the outer `cianfhoghlaim.meaisinfhoghlaim.models` package (not in a
nested `ocr/models/` sub-package). The inner `ocr.models` path is
kept as a back-compat shim.

This `__init__.py` re-exports the symbols from `registry.py` so
callers can do:

    from cianfhoghlaim.meaisinfhoghlaim.models import (
        VISION_MODELS,
        get_default_for_m4_max,
        select_ocr_backend,
    )

The legacy `OCR_MODELS` and `VLM_MODELS` aliases are also exposed
for back-compat with pre-v4 callers (they collapse to the v4
`VISION_MODELS` dict).
"""

from __future__ import annotations

from cianfhoghlaim.meaisinfhoghlaim.models.registry import (
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

# Shared LlamaSwap routing table (added 2026-07-17)
from cianfhoghlaim.meaisinfhoghlaim.models.routing import (
    ROUTING_TABLE,
    RoutingConfig,
    route_language,
    get_baml_client,
    get_model_name,
    list_supported_routes,
)
