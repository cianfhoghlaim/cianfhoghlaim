"""
v4 OCR Models registry (post-2026-06-28 consolidation).

This package is the canonical home for the OCR/VLM model registry per
`openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` and the v4 platform
spec at `openspec/specs/meaisinfhoghlaim-platform/spec.md:683-691`.

The 24-entry `VISION_MODELS` dict at `registry.py` is the single source
of truth for all OCR/VLM model references in the Cianfhoghlaim
platform. The legacy `OCR_MODELS` + `VLM_MODELS` dicts at
`cianfhoghlaim/ocr/_meaisinfhoghlaim_src/model_registry.py` and
`vlm_finetune_comparison.py` are deprecated; they re-export from
this package with a `DeprecationWarning`.

See:
- `openspec/changes/2026-06-29-fix-ocr-vlm-registry-with-unsloth-priority/`
  (the change that introduced this v4 home)
- `openspec/research/2026-06-29-ocr-vlm-registry-audit/kcg-ocr-vlm-registry.md`
  (the 592-line HF Hub audit that verified every model_id live on 2026-06-29)
"""

from .registry import (
    CLASSICAL_OCR,
    MODEL_BACKEND,
    MODEL_CAPABILITY,
    OCRAwareSelection,
    OCRModel,
    TEXT_MODELS,
    VISION_MODELS,
    ModelBackend,
    ModelCapability,
    ModelRegistry,
    get_default_for_m4_max,
    get_optimal_for_m4,
    select_ocr_backend,
)
from .vlm_finetune_comparison import (
    VLM_COMPARISON_MODELS,
    VLM_MODELS,
    VLMComparisonPipeline,
    FinetuneConfig,
    EvaluationResult,
)

__all__ = [
    # v4 registry exports
    "VISION_MODELS",
    "CLASSICAL_OCR",
    "TEXT_MODELS",
    "MODEL_BACKEND",
    "MODEL_CAPABILITY",
    "OCRModel",
    "OCRAwareSelection",
    "ModelRegistry",
    "ModelBackend",
    "ModelCapability",
    "get_optimal_for_m4",
    "get_default_for_m4_max",
    "select_ocr_backend",
    # v4 VLM fine-tune comparison
    "VLM_MODELS",
    "VLM_COMPARISON_MODELS",
    "VLMComparisonPipeline",
    "FinetuneConfig",
    "EvaluationResult",
]
