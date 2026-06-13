"""oideachais.dlt_sources.domains.medicine.ie — Ireland medicine DLT sources.

Phase 6 of the openspec change. Each sub-module is a small
`@dlt.resource` over a public endpoint; the legacy address is
the same file under `oideachais.dlt_sources.ireland.<entity>` once
the Phase 5 re-organisation is complete.
"""
from __future__ import annotations

from oideachais.dlt_sources.domains.medicine.ie import (
    doh,
    hpsc,
    hse,
    medical_council,
)

__all__ = ["doh", "hpsc", "hse", "medical_council"]
