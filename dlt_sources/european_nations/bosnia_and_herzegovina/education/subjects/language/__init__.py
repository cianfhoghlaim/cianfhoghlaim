"""Re-export the Bosnia and Herzegovina Language per-subject DLT source."""
from dlt_sources.european_nations.bih.education.subjects.language.language import (
    BIHLanguageSource,
    bih_language,
    bih_language_source,
)  # noqa: F401

__all__ = ["BIHLanguageSource", "bih_language", "bih_language_source"]
