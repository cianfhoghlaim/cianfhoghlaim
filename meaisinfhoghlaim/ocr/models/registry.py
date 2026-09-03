"""Back-compat re-export shim for the v4 OCR/VLM model registry.

The canonical implementation lives at
`meaisinfhoghlaim.models.registry` (per the v4 platform
convention: the outer `models/` package is canonical, not the nested
`ocr/models/` sub-package).

This shim re-exports the same symbols so legacy code that does
`from meaisinfhoghlaim.ocr.models.registry import VISION_MODELS`
keeps working until v5. A `DeprecationWarning` is emitted on import;
callers should migrate to:

    from meaisinfhoghlaim.models.registry import VISION_MODELS

The shim will be removed in v5 of the registry.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from `meaisinfhoghlaim.ocr.models.registry` is a "
    "deprecated v4 back-compat shim. The canonical home is "
    "`meaisinfhoghlaim.models.registry` (per the v4 platform "
    "convention: the outer `models/` package is canonical). This shim will be "
    "removed in v5.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the canonical v4 home.
from meaisinfhoghlaim.models.registry import (  # noqa: E402
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