"""Re-export the Serbia Physics per-subject DLT source."""
from dlt_sources.european_nations.srb.education.subjects.physics.physics import (
    SRBPhysicsSource,
    srb_physics,
    srb_physics_source,
)  # noqa: F401

__all__ = ["SRBPhysicsSource", "srb_physics", "srb_physics_source"]
