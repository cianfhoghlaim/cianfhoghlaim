"""Re-export the Kosovo Computing Science per-subject DLT source."""
from dlt_sources.european_nations.xkx.education.subjects.computing_science.computing_science import (
    XKXComputingScienceSource,
    xkx_computing_science,
    xkx_computing_science_source,
)  # noqa: F401

__all__ = ["XKXComputingScienceSource", "xkx_computing_science", "xkx_computing_science_source"]
