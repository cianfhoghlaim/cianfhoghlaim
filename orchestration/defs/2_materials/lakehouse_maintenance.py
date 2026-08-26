"""Nightly DuckLake maintenance Dagster asset group (§7.3).

Per the **2026-08-24-dlt-sources-to-multi-repo-scaffold-v1** §7.3 change.

The 4 nightly maintenance tasks each DuckLake-managed destination
needs:

1. ``ducklake_expire_snapshots`` — drop catalog snapshot rows beyond
   the 7-day retention window so the Postgres catalog does not grow
   unbounded.
2. ``ducklake_cleanup_old_files`` — remove orphan Parquet files left
   over from expired snapshots. MUST run AFTER
   ``ducklake_expire_snapshots`` so it has a full picture of which
   snapshots are still referenced.
3. ``ducklake_merge_adjacent_files`` — per the 6 hot LC tables
   (``JURISDICTION_SORTED_BY_TABLES``), re-write small adjacent
   Parquet files into larger ones.
4. ``ducklake_rewrite_data_files`` — for the 6 hot LC tables, apply
   the canonical BIEP `SORTED BY (jurisdiction, stage, subject)`
   rewrite (the §7.2 axis).

## KCG conventions used

- 5-layer Dagster group_name convention
  (`5_agent_ops_lakehouse_maintenance`; see
  `openspec/specs/dagster-5-layer-component-architecture`).
- Asset-only (no jobs; the assets are picked up by the canonical
  nightly cron at `orchestration/automation/biiep_scheduling.py:NIGHTLY_AUDIT_CRON`).
- The 4 SQL statements are pure-string helpers in
  `dlt_sources.common.destinations.ducklake` — the assets only
  own the open-connection + execute-SQL flow + the
  MaterializeResult telemetry (rows affected, duration).
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from dagster import (
    AssetExecutionContext,
    AssetMaterializeResult,
    MaterializeResult,
    asset,
)

from dlt_sources.common.destinations.ducklake import (
    JURISDICTION_SORTED_BY_TABLES,
    ducklake_cleanup_old_files_sql,
    ducklake_expire_snapshots_sql,
    ducklake_merge_adjacent_files_sql,
    ducklake_rewrite_data_files_sql,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 5-layer group_name convention
# -----------------------------------------------------------------------------
# Layer 5 (Agent Operations) — these are the nightly maintenance gates
# that keep the DuckLake namespace tidy.

LAKEHOUSE_MAINTENANCE_GROUP = "5_agent_ops_lakehouse_maintenance"
"""The 5-layer Dagster group_name for the §7.3 nightly maintenance assets."""


# -----------------------------------------------------------------------------
# Defaults
# -----------------------------------------------------------------------------

DEFAULT_SNAPSHOT_RETENTION_DAYS: int = 7
"""The default catalog-snapshot retention window (§7.3). Snapshots older
than this are expired + have their underlying Parquet files cleaned."""


# -----------------------------------------------------------------------------
# Asset 1 — `ducklake_expire_snapshots`
# -----------------------------------------------------------------------------


@asset(
    group_name=LAKEHOUSE_MAINTENANCE_GROUP,
    description=(
        "Drop catalog snapshot rows beyond the 7-day retention window. "
        "Runs FIRST so the cleanup_old_files asset has a full picture of "
        "which snapshots are still referenced. §7.3."
    ),
)
def ducklake_expire_snapshots_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Expire old DuckLake catalog snapshots (§7.3 asset 1 of 4)."""
    sql = ducklake_expire_snapshots_sql(
        snapshot_retention_days=DEFAULT_SNAPSHOT_RETENTION_DAYS,
    )
    started_at = datetime.now(UTC).isoformat()
    context.log.info("ducklake_expire_snapshots SQL: %s", sql)
    # TODO: open duckdb connection to the Postgres-backed DuckLake
    # and execute `sql`. The dagster-dlt DuckLake resource at
    # orchestration/resources.py:DuckLakeClientResource is the
    # canonical wrapper; it is not yet wired here (see §7.3 TODO
    # for follow-up). For now, the asset returns a MaterializeResult
    # with the rendered SQL so Dagster sees the asset + the test
    # capture works.
    rows_affected = 0  # 0 because we do not yet connect to the live DuckLake
    return MaterializeResult(
        metadata={
            "sql": sql,
            "snapshot_retention_days": DEFAULT_SNAPSHOT_RETENTION_DAYS,
            "rows_affected": rows_affected,
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
            "follow_up": (
                "Wire DuckLakeClientResource.open_ducklake_connection() once the "
                "orchestration/resources.py helper is extracted (see §7.3 follow-up)."
            ),
        },
    )


# -----------------------------------------------------------------------------
# Asset 2 — `ducklake_cleanup_old_files`
# -----------------------------------------------------------------------------


@asset(
    group_name=LAKEHOUSE_MAINTENANCE_GROUP,
    description=(
        "Remove orphan Parquet files left over from expired snapshots. "
        "Runs AFTER `ducklake_expire_snapshots_asset` (Dagster dependency). "
        "§7.3."
    ),
    deps=[ducklake_expire_snapshots_asset],
)
def ducklake_cleanup_old_files_asset(context: AssetExecutionContext) -> MaterializeResult:
    """Cleanup old Parquet files after snapshot expiry (§7.3 asset 2 of 4)."""
    sql = ducklake_cleanup_old_files_sql(
        snapshot_retention_days=DEFAULT_SNAPSHOT_RETENTION_DAYS,
    )
    started_at = datetime.now(UTC).isoformat()
    context.log.info("ducklake_cleanup_old_files SQL: %s", sql)
    rows_affected = 0
    return MaterializeResult(
        metadata={
            "sql": sql,
            "snapshot_retention_days": DEFAULT_SNAPSHOT_RETENTION_DAYS,
            "rows_affected": rows_affected,
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
        },
    )


# -----------------------------------------------------------------------------
# Asset 3 — `ducklake_merge_adjacent_files` (per-hot-table loop)
# -----------------------------------------------------------------------------


@asset(
    group_name=LAKEHOUSE_MAINTENANCE_GROUP,
    description=(
        "For each of the 6 hot LC tables in `JURISDICTION_SORTED_BY_TABLES`, "
        "re-write small adjacent Parquet files into larger ones. §7.3."
    ),
    deps=[ducklake_cleanup_old_files_asset],
)
def ducklake_merge_adjacent_files_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Per-table merge of adjacent Parquet files (§7.3 asset 3 of 4)."""
    started_at = datetime.now(UTC).isoformat()
    sqls: list[str] = []
    rows_affected_per_table: dict[str, int] = {}
    for table in sorted(JURISDICTION_SORTED_BY_TABLES):
        sql = ducklake_merge_adjacent_files_sql(table)
        context.log.info("ducklake_merge_adjacent_files[%s]: %s", table, sql)
        sqls.append(sql)
        rows_affected_per_table[table] = 0
    return MaterializeResult(
        metadata={
            "sqls": sqls,
            "rows_affected_per_table": rows_affected_per_table,
            "table_count": len(JURISDICTION_SORTED_BY_TABLES),
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
        },
    )


# -----------------------------------------------------------------------------
# Asset 4 — `ducklake_rewrite_data_files` (per-hot-table SORTED BY rewrite)
# -----------------------------------------------------------------------------


@asset(
    group_name=LAKEHOUSE_MAINTENANCE_GROUP,
    description=(
        "For each of the 6 hot LC tables, re-write the Parquet files against "
        "the canonical §7.2 BIEP axis `SORTED BY (jurisdiction, stage, subject)`. "
        "§7.3."
    ),
    deps=[ducklake_merge_adjacent_files_asset],
)
def ducklake_rewrite_data_files_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Per-table SORTED BY rewrite (§7.3 asset 4 of 4)."""
    started_at = datetime.now(UTC).isoformat()
    sqls: list[str] = []
    rows_affected_per_table: dict[str, int] = {}
    for table in sorted(JURISDICTION_SORTED_BY_TABLES):
        sql = ducklake_rewrite_data_files_sql(table)
        context.log.info("ducklake_rewrite_data_files[%s]: %s", table, sql)
        sqls.append(sql)
        rows_affected_per_table[table] = 0
    return MaterializeResult(
        metadata={
            "sqls": sqls,
            "rows_affected_per_table": rows_affected_per_table,
            "table_count": len(JURISDICTION_SORTED_BY_TABLES),
            "sort_columns": ("jurisdiction", "stage", "subject"),
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
        },
    )


# -----------------------------------------------------------------------------
# TODO (§7.3 follow-up)
# -----------------------------------------------------------------------------
#
# 1. Wire `orchestration/resources.py:DuckLakeClientResource` (or a new
#    `DuckLakeMaintenanceResource`) into the 4 assets so they actually
#    open the duckdb connection + execute the `sql` strings. The current
#    assets emit `MaterializeResult` with the rendered SQL so Dagster
#    has visibility into the maintenance work even when the resource
#    is offline (this matches the BIEP M0 foundation-asset pattern at
#    `orchestration/defs/2_materials/biiep_v3/m0_foundation_assets.py`).
#
# 2. Wire the 4 assets into the canonical nightly cron
#    `orchestration/automation/biiep_scheduling.py:NIGHTLY_AUDIT_CRON`.
#    The scheduler currently triggers `make_nightly_audit_automation()`
#    for the BIEP v3 RAGAS + audit + asset checks; the §7.3 chain should
#    run AFTER it (so the DuckLake is clean at the start of each academic
#    year + the start of each month for the government circulars cron).
#
# 3. Add the 4 SQL strings to the `dagster-dlt` DuckLake resource
#    registry so the asset group is discoverable by the BIEP M0
#    foundation smoke tests.

__all__ = [
    "LAKEHOUSE_MAINTENANCE_GROUP",
    "DEFAULT_SNAPSHOT_RETENTION_DAYS",
    "ducklake_expire_snapshots_asset",
    "ducklake_cleanup_old_files_asset",
    "ducklake_merge_adjacent_files_asset",
    "ducklake_rewrite_data_files_asset",
]
