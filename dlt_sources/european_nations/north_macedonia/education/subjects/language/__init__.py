"""Re-export the North Macedonia Language per-subject DLT source."""
from dlt_sources.european_nations.mkd.education.subjects.language.language import (
    MKDLanguageSource,
    mkd_language,
    mkd_language_source,
)  # noqa: F401

__all__ = ["MKDLanguageSource", "mkd_language", "mkd_language_source"]
