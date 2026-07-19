"""Re-export the Turkey Biology per-subject DLT source."""
from dlt_sources.european_nations.tur.education.subjects.biology.biology import (
    TURBiologySource,
    tur_biology,
    tur_biology_source,
)  # noqa: F401

__all__ = ["TURBiologySource", "tur_biology", "tur_biology_source"]
