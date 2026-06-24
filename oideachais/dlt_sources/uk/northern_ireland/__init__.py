"""
DLT sources for Northern Ireland education data.

DEPRECATED LOCATION (2026-06-24): This directory is a backward-compat
re-export shim. The canonical home for Northern Ireland education
sources is `oideachais/dlt_sources/domains/education/ni/`. New code MUST
import from the canonical location; this shim will be removed in a
follow-up openspec change.

See `openspec/changes/lateralise-dlt-sources-to-domains/`.
"""

from oideachais.dlt_sources.domains.education.ni import (
    education_ni,
    etini,
    nisra,
)

nisra_source = nisra.nisra_source
education_ni_source = education_ni.education_ni_source
etini_source = etini.etini_source

__all__ = [
    "nisra_source",
    "education_ni_source",
    "etini_source",
]
