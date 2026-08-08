"""Dagster asset + schedule for the daily educational-credential anchor.

Per `2026-08-08-learn-to-earn-x402-credential-pipeline-v1`: this asset
was referenced (as living at `dagster/assets/credential_assets.py`) in
the docstrings of `tuatha/badges/ledger.py`, `tuatha/badges/anchor.py`,
and `tuatha/contracts/cred_anchor.py`, but never actually defined
anywhere in the codebase — the "quest complete → badge → daily on-chain
anchor" pipeline had no scheduler at all. This file is the real
implementation, at the path this repo's live convention actually uses
(`orchestration/defs/<layer>/` — the 5-layer component architecture's
"Agent Operations" layer — not the legacy `dagster/assets/` path the
docstrings named).

Computes and publishes one Merkle batch per day over every
`SkillTreeBadge` minted since the last run, via
`tuatha/badges/anchor.py::publish_anchor()`. Educational, not financial
— see `tuatha/contracts/CredAnchor.sol`.
"""

from datetime import datetime, timedelta, timezone

from dagster import AssetExecutionContext, AssetSelection, RunRequest, asset, define_asset_job, schedule


@asset(
    group_name="credentials",
    description=(
        "Publishes the daily Merkle root of SkillTreeBadges minted in the "
        "last 24h to the CredAnchor contract on Base L2, and writes the "
        "resulting tx_hash back into each badge's on_chain_anchor field."
    ),
)
def daily_credential_anchor(context: AssetExecutionContext) -> dict[str, object]:
    """Materialise one daily Merkle-anchor batch.

    Fetches every badge minted since 24h before this run, computes their
    Merkle root, and publishes it via
    `tuatha.badges.anchor.publish_anchor()`. No-ops (0 leaves) is a valid,
    expected outcome on a quiet day — it still publishes an empty-root
    batch so the daily cadence is unbroken and auditable.
    """
    import asyncio

    from tuatha.badges.anchor import publish_anchor
    from tuatha.badges.ledger import fetch_badges_since

    since = datetime.now(tz=timezone.utc) - timedelta(hours=24)
    batch_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    async def _run() -> dict[str, object]:
        badges = await fetch_badges_since(since.isoformat())
        context.log.info(f"daily_credential_anchor: {len(badges)} badges since {since.isoformat()}")
        batch = await publish_anchor(badges, batch_date)
        return {
            "batch_id": batch.id,
            "batch_date": batch.batch_date,
            "merkle_root": batch.merkle_root,
            "leaf_count": batch.leaf_count,
            "tx_hash": batch.tx_hash,
        }

    return asyncio.run(_run())


# Explicit job wrapping the single asset — mirrors the proven pattern in
# `orchestration/automation/sync_schedules.py` (job=<JobDefinition>, not
# the asset function directly).
daily_credential_anchor_job = define_asset_job(
    name="daily_credential_anchor_job",
    selection=AssetSelection.assets(daily_credential_anchor),
)


@schedule(
    cron_schedule="0 2 * * *",  # 02:00 UTC daily, per anchor.py's own docstring intent
    job=daily_credential_anchor_job,
    execution_timezone="UTC",
    description=(
        "Materialises daily_credential_anchor every day at 02:00 UTC — "
        "the scheduler that was referenced but never implemented anywhere "
        "in the codebase prior to "
        "2026-08-08-learn-to-earn-x402-credential-pipeline-v1."
    ),
)
def daily_credential_anchor_at_2am(context) -> RunRequest:
    """Cron entry-point that triggers the daily_credential_anchor asset."""
    return RunRequest(
        run_key=f"daily_credential_anchor_{context.scheduled_execution_time.isoformat()}"
    )


__all__ = [
    "daily_credential_anchor",
    "daily_credential_anchor_job",
    "daily_credential_anchor_at_2am",
]
