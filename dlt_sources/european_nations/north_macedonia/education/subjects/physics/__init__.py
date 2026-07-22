"""Re-export the North Macedonia Physics per-subject DLT source."""
from dlt_sources.european_nations.mkd.education.subjects.physics.physics import (
    MKDPhysicsSource,
    mkd_physics,
    mkd_physics_source,
)  # noqa: F401

__all__ = ["MKDPhysicsSource", "mkd_physics", "mkd_physics_source"]
