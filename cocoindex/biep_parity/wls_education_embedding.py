"""DEPRECATED 2026-08-15 — replaced by `cocoindex/biep_parity/bi_factory.py`.

This file is now a 1-line re-export shim. The 8 hand-written
CocoIndex v1 Apps that previously lived here have been collapsed
into one factory at `cocoindex/biep_parity/bi_factory.py`
(parameterized on `JURISDICTION_CONFIG`).

Per the `centralized-schema-registry` capability.
"""
from cocoindex.biep_parity.bi_factory import wls_education_embedding  # noqa: F401
