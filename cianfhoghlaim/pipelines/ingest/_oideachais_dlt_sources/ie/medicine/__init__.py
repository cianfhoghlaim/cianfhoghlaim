"""oideachais.dlt_sources.ie.medicine — Ireland medicine DLT sources.

Each sub-module is a small `@dlt.resource` over a public endpoint.
"""
from __future__ import annotations

from dlt_sources.ie.medicine import (
    doh,
    hpsc,
    hse,
    medical_council,
)

__all__ = ["doh", "hpsc", "hse", "medical_council"]
