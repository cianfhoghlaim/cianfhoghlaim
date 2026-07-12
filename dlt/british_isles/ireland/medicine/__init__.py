"""oideachais.cianfhoghlaim.dlt.british_isles.ireland.medicine — Ireland medicine DLT sources.

Each sub-module is a small `@dlt.resource` over a public endpoint.
"""
from __future__ import annotations

from cianfhoghlaim.dlt.british_isles.ireland.medicine import (
    doh,
    hpsc,
    hse,
    medical_council,
)

__all__ = ["doh", "hpsc", "hse", "medical_council"]
