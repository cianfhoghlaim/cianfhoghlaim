"""DEPRECATED — backwards-compatibility shim for the legacy
``NationSource`` API (per the
2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 §11 change).

The legacy ``NationSource`` dataclass has been **merged** into
``JurisdictionPipelineBase`` at
``dlt_sources.british_isles._cross.jurisdiction_pipeline_base``. The
merged class supports the legacy NationSource construction pattern
via the ``country_code=...`` / ``domain=...`` / ``source_slug=...``
/ ``supported_languages=...`` / ``document_type=...`` /
``extra_metadata=...`` keyword-only path (see the §11 docstring on
``JurisdictionPipelineBase.__init__``).

This module re-exports the merged symbols under their legacy names
so the 51 per-nation source files that still
``from dlt_sources.european_nations._shared.nation_source import
NationSource, row_from_cache, use_local_scrapes`` continue to
function unchanged for one release before the bulk-rewrite sweep.

Migration path::

    # BEFORE
    from dlt_sources.european_nations._shared.nation_source import (
        NationSource, row_from_cache, use_local_scrapes,
    )
    class AustraliaGovernmentSource(JurisdictionPipelineBase):
        def __init__(self) -> None:
            super().__init__(
                country_code="aus",
                domain="government",
                source_slug="gov_au",
                ...
            )

    # AFTER (canonical, no deprecation warning)
    from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import (
        JurisdictionPipelineBase, row_from_cache, use_local_scrapes,
    )
    class AustraliaGovernmentSource(JurisdictionPipelineBase):
        def __init__(self) -> None:
            super().__init__(
                country_code="aus",
                domain="government",
                source_slug="gov_au",
                ...
            )

``NationSource`` is exposed here as an alias of
``JurisdictionPipelineBase`` so the only difference in the rewritten
importer is the import path + the base-class name. The constructor
signature is unchanged.
"""
from __future__ import annotations

import warnings

# Emit a DeprecationWarning every time the legacy path is imported.
# stacklevel=2 so the warning points at the importer (the canonical
# Python convention — see PEP 562 + warnings.warn docs).
warnings.warn(
    "dlt_sources.european_nations._shared.nation_source is deprecated; "
    "use dlt_sources.british_isles._cross.jurisdiction_pipeline_base "
    "(JurisdictionPipelineBase in NationSource mode via "
    "country_code=... / domain=... / source_slug=... kwargs) instead. "
    "See the §11 change in "
    "openspec/changes/2026-08-24-dlt-sources-to-multi-repo-scaffold-v1/.",
    DeprecationWarning,
    stacklevel=2,
)

from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import (  # noqa: E402
    EU_NATIONS_CACHE_ROOT,
    JurisdictionPipelineBase as NationSource,
    row_from_cache,
    use_local_scrapes,
)

__all__ = [
    "EU_NATIONS_CACHE_ROOT",
    "NationSource",
    "row_from_cache",
    "use_local_scrapes",
]
