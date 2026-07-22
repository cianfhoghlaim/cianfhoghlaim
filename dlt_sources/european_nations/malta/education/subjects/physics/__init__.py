"""Re-export the Malta Physics per-subject DLT source."""
from dlt_sources.european_nations.mlt.education.subjects.physics import (
    mlt_physics,
    mlt_physics_source,
)  # noqa: F401

__all__ = ["mlt_physics", "mlt_physics_source"]
