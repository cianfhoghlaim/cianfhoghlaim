"""
DLT sources for Wales education data.

DEPRECATED LOCATION (2026-06-24): This directory is a backward-compat
re-export shim. The canonical home for Wales education sources is
`oideachais/dlt_sources/domains/education/wls/`. New code MUST import
from the canonical location; this shim will be removed in a
follow-up openspec change.

See `openspec/changes/lateralise-dlt-sources-to-domains/`.
"""

from sruth.oideachais.dlt_sources.domains.education.wls import estyn, statswales

statswales_source = statswales.statswales_source
estyn_source = estyn.estyn_source

__all__ = [
    "statswales_source",
    "estyn_source",
]
