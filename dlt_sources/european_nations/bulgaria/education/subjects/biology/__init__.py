"""Re-export the Bulgaria Biology per-subject DLT source."""
from dlt_sources.european_nations.bgr.education.subjects.biology import (
    bgr_biology,
    bgr_biology_source,
)  # noqa: F401

__all__ = ["bgr_biology", "bgr_biology_source"]
