"""crown_dependencies — BIEP v3 Crown Dependencies pipeline re-export shim.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
the 3 deferred Crown Dependencies (Jersey + Guernsey + Isle of Man) have
been **promoted to proper per-jurisdiction directories**. The canonical
jurisdiction pipeline files are now:

- `dlt_sources.education.jersey.british_isles.education.jersey_jurisdiction_pipeline`
  — `JerseyJurisdictionPipeline` (BIEP v3)
- `dlt_sources.education.guernsey.british_isles.education.guernsey_jurisdiction_pipeline`
  — `GuernseyJurisdictionPipeline` (BIEP v3)
- `dlt_sources.education.isle_of_man.british_isles.education.isle_of_man_jurisdiction_pipeline`
  — `IsleOfManJurisdictionPipeline` (BIEP v3)

This file is kept as a **re-export shim** for backward compatibility
with the BIEP v3 deferred openspec change
`2026-07-31-biep-v3-crown-dependencies-v1/` and the BIEP v3
orchestration assets
(`orchestration/defs/2_materials/crown_dependencies_education/` + the
MotherDuck Flight
`motherduck/flights/crown_dependencies_flight.py`) that may still
import from `dlt_sources.education.crown_dependencies.british_isles.education`.

The `crown_dependencies_jurisdiction_pipeline()` function is a canonical
**multi-jurisdiction factory** that returns the per-jurisdiction
JurisdictionPipeline instance (NOT a new CrownDependenciesJurisdictionPipeline).

Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/
Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
from __future__ import annotations

from dlt_sources.education.guernsey.british_isles.education.guernsey_jurisdiction_pipeline import (
    GuernseyJurisdictionPipeline,
    guernsey_jurisdiction_pipeline,
)
from dlt_sources.education.isle_of_man.british_isles.education.isle_of_man_jurisdiction_pipeline import (
    IsleOfManJurisdictionPipeline,
    isle_of_man_jurisdiction_pipeline,
)
from dlt_sources.education.jersey.british_isles.education.jersey_jurisdiction_pipeline import (
    JerseyJurisdictionPipeline,
    jersey_jurisdiction_pipeline,
)

# The 3 jurisdictions covered by this multi-jurisdiction factory
CROWN_DEPENDENCIES: tuple[str, ...] = ("jersey", "guernsey", "isle_of_man")


# Per-jurisdiction pre-built instances (for backward compat with the
# BIEP v3 orchestration assets that imported them as
# `crown_jersey_pipeline` etc.)
crown_jersey_pipeline = jersey_jurisdiction_pipeline
crown_guernsey_pipeline = guernsey_jurisdiction_pipeline
crown_isle_of_man_pipeline = isle_of_man_jurisdiction_pipeline


# Backward-compat alias (the legacy class name)
CrownDependenciesJurisdictionPipeline = JerseyJurisdictionPipeline


def crown_dependencies_jurisdiction_pipeline(
    jurisdiction: str,
    dataset_name: str | None = None,
    use_md: bool = True,
):
    """The canonical generic Crown Dependencies DLT pipeline factory.

    Returns the pre-built per-jurisdiction JurisdictionPipelineBase
    subclass instance (NOT a new CrownDependenciesJurisdictionPipeline) so
    callers that compare against the canonical per-jurisdiction instance
    work correctly.
    """
    if jurisdiction == "jersey":
        return jersey_jurisdiction_pipeline
    if jurisdiction == "guernsey":
        return guernsey_jurisdiction_pipeline
    if jurisdiction == "isle_of_man":
        return isle_of_man_jurisdiction_pipeline
    raise ValueError(
        f"jurisdiction={jurisdiction!r} not in {CROWN_DEPENDENCIES!r}"
    )


__all__ = [
    "crown_dependencies_jurisdiction_pipeline",
    "crown_jersey_pipeline",
    "crown_guernsey_pipeline",
    "crown_isle_of_man_pipeline",
    "CrownDependenciesJurisdictionPipeline",
    "CROWN_DEPENDENCIES",
    "JerseyJurisdictionPipeline",
    "GuernseyJurisdictionPipeline",
    "IsleOfManJurisdictionPipeline",
    "jersey_jurisdiction_pipeline",
    "guernsey_jurisdiction_pipeline",
    "isle_of_man_jurisdiction_pipeline",
]
