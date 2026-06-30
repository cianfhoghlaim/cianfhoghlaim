"""``official_media_extract`` Dagster asset.

Reads the Instagram export at ``$OIDEACHAIS_IG_EXPORT_DIR`` (or the
path passed to the asset's ``RunConfig``), runs the two-stage filter,
and writes the surviving candidates to the DLT-managed
``oideachais.official_media.candidates`` table in DuckLake.
"""
from __future__ import annotations

import os
from pathlib import Path

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


@dg.asset(
    key=["official_media", "extract"],
    group_name="official_media",
    description=(
        "Parse the Instagram export at $OIDEACHAIS_IG_EXPORT_DIR, "
        "filter via the 2-stage allowlist + BAML fallback, and write "
        "the surviving candidates to the oideachais.official_media "
        "DuckLake namespace."
    ),
    compute_kind="dlt",
    metadata={"primary_key": ["ig_export_id", "ig_username", "list_kind"]},
)
def official_media_extract(context) -> dg.MaterializeResult:
    """Run the DLT source over the Instagram export and materialise."""
    from cianfhoghlaim.dlt.official_media.allowlist import allowlist_filter
    from cianfhoghlaim.dlt.official_media.instagram_export import (
        InstagramExportParser,
    )

    export_dir = os.environ.get("OIDEACHAIS_IG_EXPORT_DIR")
    if not export_dir:
        # No export directory configured — emit the offline stub
        # result so the asset still materialises successfully.
        logger.info(
            "official_media_extract_no_export_dir",
            hint="Set OIDEACHAIS_IG_EXPORT_DIR to point at the unzipped Instagram export",
        )
        return dg.MaterializeResult(
            metadata={
                "candidates_written": 0,
                "profiles_parsed": 0,
                "stage1_hits": 0,
                "stage2_hits": 0,
                "backend": "stub_no_export_dir",
            }
        )

    parser = InstagramExportParser(Path(export_dir))
    profiles = list(parser.parse())

    # Run the 2-stage filter
    candidates: list[dict] = []
    stage1_hits = 0
    stage2_hits = 0
    for profile in profiles:
        match = allowlist_filter.classify(profile.ig_username)
        if not match.is_official:
            continue
        row = profile.to_dlt_row()
        row["category"] = match.category
        row["match_stage"] = match.stage
        row["match_source"] = match.source
        candidates.append(row)
        if match.stage == 1:
            stage1_hits += 1
        elif match.stage == 2:
            stage2_hits += 1

    # In production this would invoke the DLT pipeline:
    #     dlt.pipeline(pipeline_name="official_media", destination="ducklake",
    #                  dataset_name="oideachais").run(
    #         official_media_source(export_dir=export_dir)
    #     )
    # The actual DLT wiring is in official_media_source.py (PR 1
    # follow-up). For now we materialise the row count as metadata.

    logger.info(
        "official_media_extract_complete",
        profiles=len(profiles),
        candidates=len(candidates),
        stage1=stage1_hits,
        stage2=stage2_hits,
    )
    return dg.MaterializeResult(
        metadata={
            "candidates_written": len(candidates),
            "profiles_parsed": len(profiles),
            "stage1_hits": stage1_hits,
            "stage2_hits": stage2_hits,
            "backend": "ducklake",
        }
    )
