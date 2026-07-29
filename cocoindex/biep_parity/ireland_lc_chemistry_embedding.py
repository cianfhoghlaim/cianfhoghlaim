"""DEPRECATED 2026-08-15 — replaced by `cocoindex/biep_parity/ireland_lc_factory.py`.

This file is now a 1-line re-export shim. The 6 hand-written
CocoIndex v1 Apps that previously lived here have been collapsed
into one factory at `cocoindex/biep_parity/ireland_lc_factory.py`
(parameterized on `LC_SUBJECT_CONFIG`).

Per the `centralized-schema-registry` capability.
"""
from cocoindex.biep_parity.ireland_lc_factory import (  # noqa: F401
    ireland_lc_chemistry_untiered_en_embedding,
    ireland_lc_chemistry_untiered_ga_embedding,
)
