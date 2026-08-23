"""orchestration.defs.uog_exam — the 5-asset group for the
University of Galway past-exam-papers pipeline (M.Sc. AI thesis).

Mounts:
  - `dlt_sources.british_isles.ireland.education.university.exam_papers.uog_exam_assets`
    (5 assets: login_health, module_discovery, papers_download,
    papers_ocr_extract, los_map)

Reference: openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
"""

from __future__ import annotations

import datetime

from dagster import (
    DefaultScheduleStatus,
    ScheduleDefinition,
    define_asset_job,
)

from dlt_sources.british_isles.ireland.education.university.exam_papers import (
    GROUP_NAME,
    uog_exam_assets,
)

# Asset-level imports resolve the names from the package.
(
    uog_exam_login_health,
    uog_exam_module_discovery,
    uog_exam_papers_download,
    uog_exam_papers_ocr_extract,
    uog_exam_los_map,
) = uog_exam_assets


# --------------------------------------------------------------------------- #
# Asset job — one asset_job per group, materialised nightly
# --------------------------------------------------------------------------- #

_uog_exam_papers_job = define_asset_job(
    name="uog_exam_papers_job",
    selection=uog_exam_assets,
    description=(
        "Materialise every UoG exam-papers asset in order: login health → "
        "module discovery → paper download → BAML extract → LO map."
    ),
)


# --------------------------------------------------------------------------- #
# Nightly schedule (UTC). Daily at 02:00 = off-peak for the UoG portal.
# --------------------------------------------------------------------------- #

uog_exam_papers_nightly = ScheduleDefinition(
    job=_uog_exam_papers_job,
    cron_schedule="0 2 * * *",
    execution_timezone="UTC",
    default_status=DefaultScheduleStatus.STOPPED,
    description=(
        "Nightly UoG exam-papers materialisation. STOPPED by default; "
        "enable once you have set INFISICAL_TOKEN + OOG_STUDENT_PASSWORD."
    ),
)


# --------------------------------------------------------------------------- #
# Definitions export
# --------------------------------------------------------------------------- #


def build_uog_exam_definitions():
    """Build a Dagster Definitions object containing the uog_exam_papers group.

    Used by `orchestration/definitions.py` and by `dg list defs`.
    """
    from dagster import Definitions

    return Definitions(
        assets=uog_exam_assets,
        jobs=[_uog_exam_papers_job],
        schedules=[uog_exam_papers_nightly],
    )


__all__ = [
    "GROUP_NAME",
    "uog_exam_assets",
    "uog_exam_login_health",
    "uog_exam_module_discovery",
    "uog_exam_papers_download",
    "uog_exam_papers_ocr_extract",
    "uog_exam_los_map",
    "uog_exam_papers_nightly",
    "build_uog_exam_definitions",
]
