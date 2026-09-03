"""Re-export the Estonia Physics per-subject DLT source."""
from dlt_sources.european_nations.est.education.subjects.physics import (
    est_physics,
    est_physics_source,
)  # noqa: F401

__all__ = ["est_physics", "est_physics_source"]
