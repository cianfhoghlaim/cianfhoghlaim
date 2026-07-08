"""
Back-compat re-export for the v4 OCR/VLM model registry.

The canonical implementation lives at
`cianfhoghlaim.ocr.models.registry` (per the v4 platform spec
line 685). This file is a thin re-export so legacy code that
imports from `cianfhoghlaim.meaisinfhoghlaim.models.registry`
keeps working until v5.

Migration: replace
    from cianfhoghlaim.meaisinfhoghlaim.models.registry import VISION_MODELS
with
    from cianfhoghlaim.ocr.models.registry import VISION_MODELS

A `DeprecationWarning` is emitted on import. The warning is also
emitted by the legacy `__init__.py` in this package.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from `cianfhoghlaim.meaisinfhoghlaim.models.registry` is a "
    "deprecated v4 back-compat shim. The canonical home is "
    "`cianfhoghlaim.ocr.models.registry` (per the v4 platform spec "
    "line 685). This shim will be removed in v5.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the canonical v4 home.
from cianfhoghlaim.ocr.models.registry import (  # noqa: E402
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

# Legacy back-compat aliases (pre-v4 had separate OCR_MODELS + VLM_MODELS)
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
