"""Re-export the Turkey Physics per-subject DLT source."""
from dlt_sources.european_nations.tur.education.subjects.physics.physics import (
    TURPhysicsSource,
    tur_physics,
    tur_physics_source,
)  # noqa: F401

__all__ = ["TURPhysicsSource", "tur_physics", "tur_physics_source"]
