"""Re-export the Serbia Language per-subject DLT source."""
from dlt_sources.european_nations.srb.education.subjects.language.language import (
    SRBLanguageSource,
    srb_language,
    srb_language_source,
)  # noqa: F401

__all__ = ["SRBLanguageSource", "srb_language", "srb_language_source"]
