"""Re-export the Moldova Language per-subject DLT source."""
from dlt_sources.european_nations.mda.education.subjects.language.language import (
    MDALanguageSource,
    mda_language,
    mda_language_source,
)  # noqa: F401

__all__ = ["MDALanguageSource", "mda_language", "mda_language_source"]
