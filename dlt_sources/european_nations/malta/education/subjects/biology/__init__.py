"""Re-export the Malta Biology per-subject DLT source."""
from dlt_sources.european_nations.mlt.education.subjects.biology import (
    mlt_biology,
    mlt_biology_source,
)  # noqa: F401

__all__ = ["mlt_biology", "mlt_biology_source"]
