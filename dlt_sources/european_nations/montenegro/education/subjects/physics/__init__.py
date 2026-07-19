"""Re-export the Montenegro Physics per-subject DLT source."""
from dlt_sources.european_nations.mne.education.subjects.physics.physics import (
    MNEPhysicsSource,
    mne_physics,
    mne_physics_source,
)  # noqa: F401

__all__ = ["MNEPhysicsSource", "mne_physics", "mne_physics_source"]
