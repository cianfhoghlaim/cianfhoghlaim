"""Credential Assets — Cianfhoghlaim Educational MMO.

Dagster assets for the daily credential Merkle anchor:

1. `daily_credential_anchor` — runs at 02:00 UTC daily, computes the
   Merkle root of new badges and publishes to Base L2.

Reference:
    openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D4)
    cianfhoghlaim/badges/anchor.py (the actual publish logic)
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import dagster as dg
import structlog

logger = structlog.get_logger(__name__)


@dg.asset(
    group_name="credentials",
    description="Daily Merkle anchor of SkillTreeBadges to Base L2",
    compute_kind="anchor",
)
def daily_credential_anchor(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Run the daily credential anchor.

    1. Fetch all badges minted since the last anchor
    2. Compute the Merkle root
    3. Publish to Base L2 via `CredAnchor.publish(root, batchId)`
    4. Write the `tx_hash` back into each badge row in Convex
    """
    from cianfhoghlaim.badges import anchor as anchor_mod
    from cianfhoghlaim.badges.ledger import fetch_badges_since

    # 1. Read the last-anchor timestamp from the Dagster cursor
    last_anchor_path = os.environ.get(
        "CIANFHOGHLAIM_CREDENTIAL_CURSOR_PATH",
        "./data/credential_anchor_cursor.txt",
    )
    last_anchor_iso = "1970-01-01T00:00:00+00:00"
    if os.path.exists(last_anchor_path):
        with open(last_anchor_path) as f:
            last_anchor_iso = f.read().strip()

    # 2. Fetch new badges since the last anchor
    new_badges = []
    try:
        import asyncio

        new_badges = asyncio.run(fetch_badges_since(last_anchor_iso))
    except Exception as exc:
        logger.warning("fetch_badges_since_failed", error=str(exc))

    # 3. If no new badges, no-op
    if not new_badges:
        return dg.MaterializeResult(metadata={"leaf_count": 0, "merkle_root": None})

    # 4. Publish the anchor
    today = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    batch = asyncio.run(anchor_mod.publish_anchor(new_badges, today))

    # 5. Update the cursor
    with open(last_anchor_path, "w") as f:
        f.write(datetime.now(tz=timezone.utc).isoformat())

    return dg.MaterializeResult(
        metadata={
            "batch_id": batch.id,
            "batch_date": batch.batch_date,
            "merkle_root": batch.merkle_root,
            "leaf_count": batch.leaf_count,
            "tx_hash": batch.tx_hash,
        }
    )