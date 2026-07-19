"""dlt.british_isles.ireland.education — Ireland education DLT sources.

The education sub-package hosts:
- The 6 NCCA per-subject DLT sources (ncca_<subject>.py)
- The Junior Cycle subject factory
- The Leaving Cert composite source
- The 4 BIEP v3 jurisdiction pipeline classes (incl. IrelandJurisdictionPipeline)

The `law/` sub-package at `dlt_sources/british_isles/ireland/law/`
is a separate sibling — it provides the operational-law sources
(citizensinformation, courts_ie, etc.) and does NOT need to be
re-exported here. The previous v7-flattening era had a stale
`court_rules / courts / judgements / legal_aid / piab` set that
was renamed to `citizensinformation / courts_ie / ...` in the
2026-07-06-ireland-legal-pipeline change.
"""
from __future__ import annotations

__all__: list[str] = []