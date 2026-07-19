"""Re-export the Slovenia Chemistry per-subject DLT source."""
from dlt_sources.european_nations.svn.education.subjects.chemistry import (
    svn_chemistry,
    svn_chemistry_source,
)  # noqa: F401

__all__ = ["svn_chemistry", "svn_chemistry_source"]
