"""Teacher PD DLT source — merged OIDE + PDST layer.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.

Combines the OIDE + PDST datasets into a single teacher-PD layer that
the `professional_learning_agent` can query.

Honors `USE_LOCAL_SCRAPES=true` (default).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import dlt

from .oide import OIDE_SUPPORT_PROGRAMMES, oide_support_programmes
from .pdst import PDST_RESOURCES, pdst_resources

logger = logging.getLogger(__name__)


@dlt.resource(name="teacher_pd_combined", write_disposition="replace", primary_key=["programme_id"])
def teacher_pd_combined() -> Iterator[dict]:
    """Merged OIDE + PDST teacher-PD layer.

    Yields one row per programme, tagged with `source_provider`
    (`oide` | `pdst`) so the BAML extraction can disambiguate.
    """
    for row in OIDE_SUPPORT_PROGRAMMES:
        yield {**row, "source_provider": "oide"}
    for row in PDST_RESOURCES:
        yield {
            **row,
            "source_provider": "pdst",
            "name_en": f"PDST Resource: {row['subject']}",
            "name_ga": f"Acmhainn PDST: {row['subject']}",
            "programme_id": row["resource_id"],
        }


@dlt.source(name="teacher_pd")
def teacher_pd_source():
    return teacher_pd_combined()
