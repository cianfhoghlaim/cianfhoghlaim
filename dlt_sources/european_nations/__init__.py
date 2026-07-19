"""European nations + Ukraine pipeline — per-nation DLT sub-trees.

Re-exports the 6 pilot country sub-trees. Call sites can do:

    from dlt_sources.european_nations import ukr, fra, deu, pol, esp, ita
    pipeline.run(ukr.education.ministry_education_science_source())
"""
from __future__ import annotations

from dlt_sources.european_nations import (
    deu,
    esp,
    fra,
    ita,
    pol,
    ukr,
)

__all__ = ["deu", "esp", "fra", "ita", "pol", "ukr"]
