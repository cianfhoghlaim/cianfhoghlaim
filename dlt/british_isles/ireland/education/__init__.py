"""dlt.british_isles.ireland.education — Ireland education DLT sources.

The education sub-package hosts:
- The 6 NCCA per-subject DLT sources (ncca_<subject>.py)
- The Junior Cycle subject factory
- The Leaving Cert composite source
- The 4 BIEP v3 jurisdiction pipeline classes (incl. IrelandJurisdictionPipeline)

The pre-v7 layout had `cianchoghlaim/dlt/british_isles/ireland/law/` as a
sibling — that path was a Pick-8 scoped legal data source reimplementation
that co-exists with the absorbed `2026-07-06-ireland-legal-pipeline` change.
"""
from __future__ import annotations

# Post-v7: import from the canonical sibling submodules directly.
from dlt.british_isles.ireland.law import (  # noqa: F401
    court_rules,
    courts,
    judgements,
    legal_aid,
    piab,
)

__all__ = [
    "court_rules",
    "courts",
    "judgements",
    "legal_aid",
    "piab",
]