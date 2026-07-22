"""EU government institutional sub-tree.

Re-exports the canonical DLT sources for the `europa.eu` portal + the
Commission press / Parliament documents / Council documents streams.
"""
from __future__ import annotations

from dlt_sources.europeanunion.government import (
    commission_press,
    council_documents,
    europa_portal,
    parliament_documents,
)

__all__ = [
    "commission_press",
    "council_documents",
    "europa_portal",
    "parliament_documents",
]
