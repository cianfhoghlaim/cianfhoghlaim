"""Re-export the Slovenia Biology per-subject DLT source."""
from dlt_sources.european_nations.svn.education.subjects.biology import (
    svn_biology,
    svn_biology_source,
)  # noqa: F401

__all__ = ["svn_biology", "svn_biology_source"]
