"""Re-export the Moldova Physics per-subject DLT source."""
from cianfhoghlaim.dlt.european_nations.mda.education.subjects.physics.physics import (
    MDAPhysicsSource,
    mda_physics,
    mda_physics_source,
)  # noqa: F401

__all__ = ["MDAPhysicsSource", "mda_physics", "mda_physics_source"]
