"""Applied Mathematics sub-package — Cianfhoghlaim Oideachais.

Per-subject NCCA Leaving Certificate Applied Mathematics pipeline.
APPM is Higher Level only (no OL / FL).

See `sources.py` for the DLT source definition and
`openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md` (D3)
for the design rationale.
"""
from .sources import (
    appm_source,
    APPM_CORPUS,
    APPM_CORPUS_EN,
    APPM_CORPUS_GA,
)

__all__ = [
    "appm_source",
    "APPM_CORPUS",
    "APPM_CORPUS_EN",
    "APPM_CORPUS_GA",
]