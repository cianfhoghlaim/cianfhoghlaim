"""oideachais.dlt_sources.cross.bunchloch — bunchloch filesystem source.

Per Phase 3D, each DLT source lives in its own file. Per-source functions
are re-exported at this package level for backward compatibility.
"""
from __future__ import annotations

from dlt_sources.cross.bunchloch.bunchloch import bunchloch_source
from dlt_sources.cross.bunchloch.bunchloch_by_subject import (
    bunchloch_by_subject_source,
)

__all__ = ["bunchloch_by_subject_source", "bunchloch_source"]
