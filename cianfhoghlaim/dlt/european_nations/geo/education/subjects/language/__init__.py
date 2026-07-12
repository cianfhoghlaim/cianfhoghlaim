"""Re-export the Georgia Language per-subject DLT source."""
from cianfhoghlaim.dlt.european_nations.geo.education.subjects.language.language import (
    GEOLanguageSource,
    geo_language,
    geo_language_source,
)  # noqa: F401

__all__ = ["GEOLanguageSource", "geo_language", "geo_language_source"]
