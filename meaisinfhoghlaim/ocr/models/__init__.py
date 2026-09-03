"""Back-compat re-export shim for the v4 OCR/VLM model registry (nested `ocr.models` package).

The canonical implementation lives at the OUTER
`meaisinfhoghlaim.models` package (per the v4 platform convention).
This nested `ocr.models` package is kept as a back-compat shim so
legacy code that does
`from meaisinfhoghlaim.ocr.models import VISION_MODELS`
keeps working until v5. A `DeprecationWarning` is emitted on import.

Migration:
    # before
    from meaisinfhoghlaim.ocr.models import VISION_MODELS
    # after
    from meaisinfhoghlaim.models import VISION_MODELS
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from `meaisinfhoghlaim.ocr.models` is a "
    "deprecated v4 back-compat shim. The canonical home is "
    "`meaisinfhoghlaim.models` (per the v4 platform "
    "convention: the outer `models/` package is canonical). This shim "
    "will be removed in v5.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from the canonical v4 home.
from meaisinfhoghlaim.models import (  # noqa: E402
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