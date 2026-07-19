"""Re-export the Slovenia Mathematics per-subject DLT source."""
from dlt_sources.european_nations.svn.education.subjects.mathematics import (
    svn_mathematics,
    svn_mathematics_source,
)  # noqa: F401

__all__ = ["svn_mathematics", "svn_mathematics_source"]
