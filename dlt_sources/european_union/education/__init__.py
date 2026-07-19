"""EU education institutional sub-tree.

Re-exports the canonical DLT sources for Eurydice, Cedefop, and the
School Education Gateway.
"""
from __future__ import annotations

from cianfhoghlaim.dlt.europeanunion.education import (
    cedefop,
    eurydice,
    school_education_gateway,
)

__all__ = ["cedefop", "eurydice", "school_education_gateway"]
