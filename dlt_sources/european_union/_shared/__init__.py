"""EU institutional pipeline — shared helpers + registries."""
from __future__ import annotations

from cianfhoghlaim.dlt.european_union._shared.registries import (
    EU_CACHE_ROOT,
    EU_DEFAULT_LANGUAGE,
    EU_INSTITUTIONS,
    EU_LANGUAGES,
    EUInstitutionalSource,
    use_local_scrapes,
)

__all__ = [
    "EU_CACHE_ROOT",
    "EU_DEFAULT_LANGUAGE",
    "EU_INSTITUTIONS",
    "EU_LANGUAGES",
    "EUInstitutionalSource",
    "use_local_scrapes",
]
