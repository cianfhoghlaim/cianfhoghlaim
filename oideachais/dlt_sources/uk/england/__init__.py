"""
DLT sources for England education data.

DEPRECATED LOCATION (2026-06-24): This directory is a backward-compat
re-export shim. The canonical home for England education sources is
`oideachais/dlt_sources/domains/education/en/`. New code MUST import
from the canonical location; this shim will be removed in a
follow-up openspec change.

See `openspec/changes/lateralise-dlt-sources-to-domains/`.
"""

# Lazy import via the canonical `domains/education/en/` package
# which itself does the lazy import from `uk/england/` to avoid
# the shared.http breakage (see domains/education/en/__init__.py).
from oideachais.dlt_sources.domains.education.en import (
    dfe_explore_statistics,
    national_curriculum,
    ofsted,
    school_info,
)

dfe_statistics_source = dfe_explore_statistics.dfe_statistics_source
ofsted_source = ofsted.ofsted_source
gias_source = school_info.gias_source

__all__ = [
    "dfe_statistics_source",
    "ofsted_source",
    "gias_source",
]
