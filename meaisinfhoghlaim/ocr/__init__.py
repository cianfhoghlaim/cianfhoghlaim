"""OCR sub-package (back-compat shim home).

The OCR sub-package houses the BIEP v2 4-path ensemble
(``baml + unstract + qwen3_vl + gemma4``) plus the back-compat
shims for ``meaisinfhoghlaim.ocr.models``. The canonical home for
the OCR/VLM model registry is the **outer**
``meaisinfhoghlaim.models`` package; this nested ``ocr/`` package
exists for legacy imports and the ensemble runner.

Layout:
- ``meaisinfhoghlaim/ocr/ensemble/`` — the 4-path ensemble extractor
  (``EnsembledExtractor`` — runs ``asyncio.gather`` over the 4 OCR
  backends and emits RAGAS-voted chunks).
- ``meaisinfhoghlaim/ocr/models/`` — back-compat shim for legacy
  ``from meaisinfhoghlaim.ocr.models import VISION_MODELS`` imports.
  Emits a ``DeprecationWarning``; the canonical home is
  ``meaisinfhoghlaim.models``.
"""
from __future__ import annotations

# Re-export the ensemble package so
# ``from meaisinfhoghlaim.ocr.ensemble import EnsembledExtractor`` works.
from . import ensemble  # noqa: F401

__all__ = ["ensemble"]