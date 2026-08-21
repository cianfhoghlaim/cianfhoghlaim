"""
CocoIndex Transforms for Irish Education Pipeline.

Provides text transformation and processing for curriculum content:
- CaighdeanTransform: Normalize pre-standard Irish to modern standard
- TerminologyTransform: Link curriculum terms to Téarma database
"""
from __future__ import annotations

from .caighdean_standardize import (
    CaighdeanTransform,
    CaighdeanCLITransform,
    TextTransform,
    TransformResult,
    get_caighdean_transform,
    create_caighdean_cocoindex_transform,
    CAIGHDEAN_DATA_DIR,
)

from .terminology_linking import (
    TerminologyTransform,
    TerminologyResult,
    TermLink,
    create_terminology_cocoindex_transform,
)

__all__ = [
    # Base classes
    "TextTransform",
    "TransformResult",
    # Caighdean
    "CaighdeanTransform",
    "CaighdeanCLITransform",
    "get_caighdean_transform",
    "create_caighdean_cocoindex_transform",
    "CAIGHDEAN_DATA_DIR",
    # Terminology
    "TerminologyTransform",
    "TerminologyResult",
    "TermLink",
    "create_terminology_cocoindex_transform",
]
