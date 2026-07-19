"""Commonwealth institutional sub-tree.

Re-exports the canonical Commonwealth Secretariat + Commonwealth
Foundation DLT sources.
"""
from __future__ import annotations

from dlt_sources.commonwealth.official import (
    commonwealth_foundation,
    commonwealth_secretariat,
)

__all__ = ["commonwealth_foundation", "commonwealth_secretariat"]
