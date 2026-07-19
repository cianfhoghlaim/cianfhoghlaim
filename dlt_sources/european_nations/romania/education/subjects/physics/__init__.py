"""Re-export the Romania Physics per-subject DLT source."""
from dlt_sources.european_nations.rou.education.subjects.physics import (
    rou_physics,
    rou_physics_source,
)  # noqa: F401

__all__ = ["rou_physics", "rou_physics_source"]
