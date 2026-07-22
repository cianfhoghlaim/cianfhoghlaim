"""Re-export the Albania Physics per-subject DLT source."""
from dlt_sources.european_nations.alb.education.subjects.physics.physics import (
    ALBPhysicsSource,
    alb_physics,
    alb_physics_source,
)  # noqa: F401

__all__ = ["ALBPhysicsSource", "alb_physics", "alb_physics_source"]
