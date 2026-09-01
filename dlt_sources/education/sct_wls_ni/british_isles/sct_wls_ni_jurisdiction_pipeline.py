"""sct_wls_ni — BIEP v3 SCT + WLS + NI pipeline re-export shim.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
the 3 deferred "mainland" British Isles jurisdictions (Scotland + Wales +
Northern Ireland) have been **promoted to proper per-jurisdiction
directories**. The canonical jurisdiction pipeline files are now:

- `dlt_sources.education.scotland.british_isles.education.scotland_jurisdiction_pipeline`
  — `ScotlandJurisdictionPipeline` (BIEP v3)
- `dlt_sources.education.wales.british_isles.education.wales_jurisdiction_pipeline`
  — `WalesJurisdictionPipeline` (BIEP v3)
- `dlt_sources.education.northern_ireland.british_isles.education.northern_ireland_jurisdiction_pipeline`
  — `NorthernIrelandJurisdictionPipeline` (BIEP v3)

This file is kept as a **re-export shim** for backward compatibility
with the BIEP v3 deferred openspec change
`2026-07-30-biep-v3-sct-wls-ni-v1/` and the BIEP v3 orchestration assets
(`orchestration/defs/2_materials/sct_wls_ni_education/` + the MotherDuck
Flight `motherduck/flights/sct_wls_ni_flight.py`) that may still
import from `dlt_sources.british_isles.sct_wls_ni.education`.

The `sct_wls_ni_jurisdiction_pipeline()` function is a canonical
**multi-jurisdiction factory** that returns the per-jurisdiction
JurisdictionPipeline instance (NOT a new SctWlsNiJurisdictionPipeline).

Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/
Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
from __future__ import annotations

from dlt_sources.education.northern_ireland.british_isles.education.northern_ireland_jurisdiction_pipeline import (
    NorthernIrelandJurisdictionPipeline,
    northern_ireland_jurisdiction_pipeline,
)
from dlt_sources.education.scotland.british_isles.education.scotland_jurisdiction_pipeline import (
    ScotlandJurisdictionPipeline,
    scotland_jurisdiction_pipeline,
)
from dlt_sources.education.wales.british_isles.education.wales_jurisdiction_pipeline import (
    WalesJurisdictionPipeline,
    wales_jurisdiction_pipeline,
)

# The 3 jurisdictions covered by this multi-jurisdiction factory
SCT_WLS_NI_JURISDICTIONS: tuple[str, ...] = (
    "scotland", "wales", "northern_ireland",
)


# Per-jurisdiction pre-built instances (for backward compat with the
# BIEP v3 orchestration assets that imported them as
# `sct_wls_ni_scotland_pipeline` etc.)
sct_wls_ni_scotland_pipeline = scotland_jurisdiction_pipeline
sct_wls_ni_wales_pipeline = wales_jurisdiction_pipeline
sct_wls_ni_northern_ireland_pipeline = northern_ireland_jurisdiction_pipeline


# Backward-compat alias (the legacy class name; the canonical class
# names are ScotlandJurisdictionPipeline + WalesJurisdictionPipeline +
# NorthernIrelandJurisdictionPipeline)
SctWlsNiJurisdictionPipeline = ScotlandJurisdictionPipeline


def sct_wls_ni_jurisdiction_pipeline(
    jurisdiction: str,
    dataset_name: str | None = None,
    use_md: bool = True,
):
    """The canonical generic Scotland/Wales/NI DLT pipeline factory.

    This function is kept for backward compatibility with the BIEP v3
    deferred openspec change `2026-07-30-biep-v3-sct-wls-ni-v1/`. New
    code SHOULD import the per-jurisdiction pipelines directly:

        from dlt_sources.education.scotland.british_isles.education.scotland_jurisdiction_pipeline import (
            scotland_jurisdiction_pipeline,
        )

    Returns the pre-built per-jurisdiction JurisdictionPipelineBase
    subclass instance (NOT a new SctWlsNiJurisdictionPipeline) so callers
    that compare against the canonical per-jurisdiction instance work
    correctly.
    """
    if jurisdiction == "scotland":
        return scotland_jurisdiction_pipeline
    if jurisdiction == "wales":
        return wales_jurisdiction_pipeline
    if jurisdiction == "northern_ireland":
        return northern_ireland_jurisdiction_pipeline
    raise ValueError(
        f"jurisdiction={jurisdiction!r} not in {SCT_WLS_NI_JURISDICTIONS!r}"
    )


__all__ = [
    "sct_wls_ni_jurisdiction_pipeline",
    "sct_wls_ni_scotland_pipeline",
    "sct_wls_ni_wales_pipeline",
    "sct_wls_ni_northern_ireland_pipeline",
    "SctWlsNiJurisdictionPipeline",
    "SCT_WLS_NI_JURISDICTIONS",
    "ScotlandJurisdictionPipeline",
    "WalesJurisdictionPipeline",
    "NorthernIrelandJurisdictionPipeline",
    "scotland_jurisdiction_pipeline",
    "wales_jurisdiction_pipeline",
    "northern_ireland_jurisdiction_pipeline",
]
