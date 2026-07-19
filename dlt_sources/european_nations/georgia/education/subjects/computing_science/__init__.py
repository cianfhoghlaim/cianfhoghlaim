"""Re-export the Georgia Computing Science per-subject DLT source."""
from dlt_sources.european_nations.geo.education.subjects.computing_science.computing_science import (
    GEOComputingScienceSource,
    geo_computing_science,
    geo_computing_science_source,
)  # noqa: F401

__all__ = ["GEOComputingScienceSource", "geo_computing_science", "geo_computing_science_source"]
