"""Re-export the Moldova Biology per-subject DLT source."""
from dlt_sources.european_nations.mda.education.subjects.biology.biology import (
    MDABiologySource,
    mda_biology,
    mda_biology_source,
)  # noqa: F401

__all__ = ["MDABiologySource", "mda_biology", "mda_biology_source"]
