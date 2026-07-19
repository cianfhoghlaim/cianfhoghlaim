"""Re-export the Georgia Mathematics per-subject DLT source."""
from dlt_sources.european_nations.geo.education.subjects.mathematics.mathematics import (
    GEOMathematicsSource,
    geo_mathematics,
    geo_mathematics_source,
)  # noqa: F401

__all__ = ["GEOMathematicsSource", "geo_mathematics", "geo_mathematics_source"]
