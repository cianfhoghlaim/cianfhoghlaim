"""
DLT sources for Scotland education data.

DEPRECATED LOCATION (2026-06-24): This directory is a backward-compat
re-export shim. The canonical home for Scotland education sources is
`oideachais/dlt_sources/domains/education/sct/`. New code MUST import
from the canonical location; this shim will be removed in a
follow-up openspec change.

See `openspec/changes/lateralise-dlt-sources-to-domains/`.
"""

from sruth.oideachais.dlt_sources.sct.education import (
    gov_scot_statistics,
    insight_benchmarking,
    simd,
)

gov_scot_source = gov_scot_statistics.gov_scot_source
insight_source = insight_benchmarking.insight_source
simd_source = simd.simd_source

__all__ = [
    "gov_scot_source",
    "insight_source",
    "simd_source",
]
