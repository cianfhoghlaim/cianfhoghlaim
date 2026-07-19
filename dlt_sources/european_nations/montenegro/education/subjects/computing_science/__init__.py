"""Re-export the Montenegro Computing Science per-subject DLT source."""
from dlt_sources.european_nations.mne.education.subjects.computing_science.computing_science import (
    MNEComputingScienceSource,
    mne_computing_science,
    mne_computing_science_source,
)  # noqa: F401

__all__ = ["MNEComputingScienceSource", "mne_computing_science", "mne_computing_science_source"]
