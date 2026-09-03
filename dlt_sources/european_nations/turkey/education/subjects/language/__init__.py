"""Re-export the Turkey Language per-subject DLT source."""
from dlt_sources.european_nations.tur.education.subjects.language.language import (
    TURLanguageSource,
    tur_language,
    tur_language_source,
)  # noqa: F401

__all__ = ["TURLanguageSource", "tur_language", "tur_language_source"]
