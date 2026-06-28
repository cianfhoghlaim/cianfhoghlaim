"""meaisin_fhoghlaim — AI/ML quadrant of the Cianfhoghlaim monorepo.

The package is a *meta-bundle* of 8 integrated components. They live
as sub-packages (sub-directories) of this directory so the runtime
import graph is shallow and the docs README layout mirrors the code
layout.

Components (per docs/meaisínfhoghlaim/README.md §1):
  - agents       : 12 specialised agents (curriculum, translation, ...)
  - ocr          : 10 OCR models across 6 backends + Irish-specific metrics
  - language     : DLT sources for Dúchas, Canúint, Téarma, Gaois + cognate DB
  - pipelines    : Irish document scanner, dialect classifier, transcript aligner, LLM router
  - alignment    : Sentence-level en/ga aligner, ColPali, G2P, dataset export
  - evaluation   : RAGAS evaluation (baseline 65.2% → agentic 87.9%)
  - quality      : Curriculum document quality + audio validation
  - catalog      : 13 models + 16 sources + 3 training mixes
  - scripts      : Glue scripts (Konductor etc.)
  - services     : FastAPI service surfaces

Quadrant context: see docs/00-core/CLAUDE.md §QUADRANT_MAP.
"""
from __future__ import annotations

__all__ = [
    "agents",
    "alignment",
    "catalog",
    "evaluation",
    "language",
    "ocr",
    "pipelines",
    "quality",
    "scripts",
    "services",
]
