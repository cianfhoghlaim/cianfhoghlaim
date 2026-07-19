"""Mathematics sub-package — Cianfhoghlaim Oideachais.

Per-subject NCCA Leaving Certificate Mathematics pipeline.

See `sources.py` for the DLT source definition and
`openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md` (D3)
for the design rationale.
"""
from .sources import (
    math_source,
    MATH_CORPUS,
    MATH_CORPUS_EN,
    MATH_CORPUS_GA,
)

__all__ = [
    "math_source",
    "MATH_CORPUS",
    "MATH_CORPUS_EN",
    "MATH_CORPUS_GA",
]