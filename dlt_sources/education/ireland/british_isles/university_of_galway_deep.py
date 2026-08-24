"""
University of Galway — DLT source (the case-study wrapper).

Thin wrapper around the reusable
`cianfhoghlaim.dlt._university_deep_factory.create_university_deep_extraction_source`
configured for the University of Galway (case study + template).

This is the *website* side of the University of Galway pipeline. The
*personal-archive* side (the user's own `leabharlann/ollscoil_na_gaillimhe/`
files) lives at `dlt_sources/leabharlann/university_of_galway.py` and is
unaffected by this change. The two are joined by the new Cognee
cross-archive edge `UoGArtifact-MATCHES-CourseDescriptor` (see
`cianfhoghlaim/cognify/rules/university_cross_archive.py`).

Reference: openspec/changes/university-of-galway-deep-extraction/
"""
from __future__ import annotations

import dlt_sources

# The bare `dlt_sources` import is the convention used by the
# existing `_cianfhoghlaim_dlt_sources` builder; the actual module
# lives at `cianfhoghlaim.pipelines.ingest._cianfhoghlaim_dlt_sources`.
# We try both names so this works in CI (where `dlt_sources` is the
# editable install) and in the monorepo (where the long path is
# the canonical import).
try:
    from dlt_sources._university_deep_factory import (
        UniversityDeepExtractionConfig,
        create_university_deep_extraction_source,
    )
except ImportError:
    from dlt_sources._university_deep_factory import (  # type: ignore[no-redef]
        UniversityDeepExtractionConfig,
        create_university_deep_extraction_source,
    )

# Canonical University of Galway configuration.
# Mirror the config in the `sources.yaml` entry `ie.university.galway`
# (which uses `kind: university_deep_extraction` per the
# `cianfhoghlaim-university-deep-extraction` spec).
UOG_CONFIG = UniversityDeepExtractionConfig(
    university_id="ie-university-galway",
    institution_name="University of Galway",
    base_url="https://www.universityofgalway.ie",
    catalogue_paths=[
        "/courses/**",
        "/programmes/**",
    ],
    school_subdomain_paths=[
        "/colleges/science-engineering/**",
        "/schools/computer-science/**",
        "/schools/mathematical-science/**",
        "/schools/education/**",
    ],
    handbook_root_path="/handbooks/2025-26/",
    academic_year=2025,
    programme_code_regex=r"[A-Z]{2,4}\d{3,4}",
    ects_field_label="ECTS",
    prefer_free_browser=True,
)


def university_of_galway_deep_source(
    config: UniversityDeepExtractionConfig | None = None,
):
    """Return the canonical University of Galway DLT source.

    Pass a custom `UniversityDeepExtractionConfig` to override the
    default (e.g. for testing with a different `academic_year` or a
    different `catalogue_paths`).
    """
    cfg = config or UOG_CONFIG
    return create_university_deep_extraction_source(cfg)


# Re-export under the legacy naming convention (the personal-archive
# UoG source uses `university_of_galway_source`; we use a `_deep_`
# suffix to disambiguate the website side).
university_of_galway_deep_source.__doc__ = (
    "University of Galway deep extraction source. Yields 5 resources: "
    "course_pages, module_pages, programme_pages, handbook_pdfs, lecturer_pages. "
    "Routes through the canonical BackendRouter (Crawl4AI primary, "
    "Firecrawl paid fallback, CreditBudget guard)."
)

# The dlt.source name is set by the factory. Provide a property for
# callers who want to introspect the source name without invoking the
# source builder.
UOG_SOURCE_NAME = f"university_{UOG_CONFIG.university_id}_deep"


def get_uog_source_name() -> str:
    """Return the dlt source name (`university_ie-university-galway_deep`).

    Exists for tests + asset key derivation.
    """
    return UOG_SOURCE_NAME


__all__ = [
    "UOG_CONFIG",
    "UOG_SOURCE_NAME",
    "university_of_galway_deep_source",
    "get_uog_source_name",
]
