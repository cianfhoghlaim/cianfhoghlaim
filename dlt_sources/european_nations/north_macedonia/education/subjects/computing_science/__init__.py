"""Re-export the North Macedonia Computing Science per-subject DLT source."""
from dlt_sources.european_nations.mkd.education.subjects.computing_science.computing_science import (
    MKDComputingScienceSource,
    mkd_computing_science,
    mkd_computing_science_source,
)  # noqa: F401

__all__ = ["MKDComputingScienceSource", "mkd_computing_science", "mkd_computing_science_source"]
