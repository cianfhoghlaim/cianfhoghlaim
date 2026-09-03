"""Re-export the Albania Language per-subject DLT source."""
from dlt_sources.european_nations.alb.education.subjects.language.language import (
    ALBLanguageSource,
    alb_language,
    alb_language_source,
)  # noqa: F401

__all__ = ["ALBLanguageSource", "alb_language", "alb_language_source"]
