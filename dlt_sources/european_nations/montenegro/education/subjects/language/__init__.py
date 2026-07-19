"""Re-export the Montenegro Language per-subject DLT source."""
from dlt_sources.european_nations.mne.education.subjects.language.language import (
    MNELanguageSource,
    mne_language,
    mne_language_source,
)  # noqa: F401

__all__ = ["MNELanguageSource", "mne_language", "mne_language_source"]
