"""
BIEP v1 MotherDuck — cianfhoghlaim-native home.

This is the canonical home for the BIEP v1 MotherDuck Dives + Flights
artifacts. The compute substrate (MotherDuck compose.yaml / pangolin.yaml /
secrets.env) lives in the bonneagar worktree at
`bonneagar/stacks/motherduck/`. The Python side — Dives that
materialise BIEP dashboards and Flights that schedule the daily
`lc_pdf_sync_flight` — lives here in `cianfhoghlaim.motherduck.{dives,
flights}`, alongside the rest of the BIEP capability (BAML extraction,
CocoIndex apps, Dagster assets, DLT sources).

Lifecycle:
  - The 4 BIEP v1 Dives are imported here as a registry tuple
    (`BIEP_DIVES`) for the MotherDuck `save_dive` MCP tool to push to
    the oideachais workspace.
  - The daily `lc_pdf_sync_flight` runs `cocoindex update lc_subjects`
    (the 6 LC subject CocoIndex v1 Apps) + `dagster asset materialize
    --select '*lc*'` (the 42 lc5/lc6 Dagster assets) + writes a status
    row to `md:oideachais.lc_ops.daily_sync_status`.

Reference:
  - openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
  - openspec/specs/british-isles-education-pipeline/spec.md
"""
from __future__ import annotations

from .dives import (
    BIEP_DIVES,
    DiveRegistry,
    GOV_CIRCULARS_ARCHIVE_DIVE,
    LC_EXAM_DIFFICULTY_DIVE,
    LC_MARKING_COMPLEXITY_DIVE,
    LC_SYLLABUS_TOPICS_DIVE,
)
from .flights import lc_pdf_sync_flight_main


def save_all() -> int:
    """Save all 4 BIEP v1 Dives to the MotherDuck workspace.

    Thin wrapper over `DiveRegistry().save_all()` so callers can use
    `cianfhoghlaim.motherduck.save_all()` directly without instantiating
    the registry themselves. Returns the count of Dives successfully saved.
    """
    return DiveRegistry().save_all()


__all__ = [
    # Dives (BIEP dashboard definitions)
    "BIEP_DIVES",
    "DiveRegistry",
    "LC_SYLLABUS_TOPICS_DIVE",
    "LC_EXAM_DIFFICULTY_DIVE",
    "LC_MARKING_COMPLEXITY_DIVE",
    "GOV_CIRCULARS_ARCHIVE_DIVE",
    "save_all",
    # Flights (scheduled Python jobs on MotherDuck compute)
    "lc_pdf_sync_flight_main",
]