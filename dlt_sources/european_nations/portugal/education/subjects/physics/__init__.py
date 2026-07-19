"""Re-export the Portugal Physics per-subject DLT source."""
from dlt_sources.european_nations.prt.education.subjects.physics import (
    prt_physics,
    prt_physics_source,
)  # noqa: F401

__all__ = ["prt_physics", "prt_physics_source"]
