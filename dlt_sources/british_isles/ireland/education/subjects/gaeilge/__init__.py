"""Gaeilge sub-package — Cianfhoghlaim Oideachais.

Per-subject NCCA Leaving Certificate + Junior Cycle Gaeilge pipeline.
Gaeilge is taught in IRISH at LC + JC levels.

See `sources.py` for the DLT source definition.
"""
from .sources import (
    gael_source,
    GAEL_CORPUS,
)

__all__ = [
    "gael_source",
    "GAEL_CORPUS",
]