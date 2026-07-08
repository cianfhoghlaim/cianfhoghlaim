"""Cianfhoghlaim OCR sub-package (canonical v4 home).

Per the v4 platform spec line 685, the canonical home for the
OCR/VLM model registry is `cianfhoghlaim/ocr/models/registry.py`.
The canonical implementation lives at that path; this package
re-exports the symbols from `cianfhoghlaim.ocr.models` so callers
can do `from cianfhoghlaim.ocr import VISION_MODELS, ...`.

A `DeprecationWarning` is emitted on import of the legacy
`cianfhoghlaim.meaisinfhoghlaim.models` shim — the canonical home
is now `cianfhoghlaim.ocr.models.registry`.

History (per
`openspec/changes/archive/2026-07-07-finalize-v4-landing/absorbed/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority/`):

- The original registry lived at
  `cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` (the
  legacy sruth layout).
- The 2026-06-28 v4 consolidation moved the canonical implementation
  to `cianfhoghlaim/meaisinfhoghlaim/models/registry.py` and removed
  the `_meaisinfhoghlaim_src` directory.
- The 2026-07-08 follow-up (the
  `2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority` change)
  moved the canonical home to
  `cianfhoghlaim/ocr/models/registry.py` per the v4 spec line 685
  and made the old `meaisinfhoghlaim/models/` path a back-compat
  shim.
"""

from __future__ import annotations

# Re-export the canonical v4 OCR/VLM registry symbols so callers can do
# `from cianfhoghlaim.ocr import VISION_MODELS, ...` (no DeprecationWarning
# at this level — only the legacy meaisinfhoghlaim shim emits the warning).
from cianfhoghlaim.ocr.models import (
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
