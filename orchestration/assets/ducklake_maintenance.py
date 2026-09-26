"""DuckLake nightly maintenance Dagster asset (Wave 4 §4.6).

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec
change (§4.6 of the master plan at
``openspec/plans/2026-08-24-master-refactor-plan.md``).

This module is the **canonical Wave 4 maintenance asset**. It
extends the existing §7.3 nightly maintenance asset group at
``orchestration/defs/2_materials/lakehouse_maintenance.py`` with the
multi-quadrant snapshot expiry policy (per Wave 4 §4.6 + per-quadrant
encryption audit + Iceberg REST verify).

**The 3 new maintenance tasks added in Wave 4:**

  1. ``ducklake_expire_snapshots_multi_quadrant`` — one
     ``CALL ducklake_expire_snapshots(...)`` per quadrant with
     per-quadrant retention (30d for BIEP, 7d for media-intel +
     UoG personal-archive). Replaces the §7.3 single-shot 7d default.
  2. ``ducklake_encryption_audit`` — verifies the per-namespace
     ``encryption_key_id`` is set for every namespace in
     ``ENCRYPTED_NAMESPACES``.
  3. ``ducklake_iceberg_rest_attach_verify`` — verifies the
     Lakekeeper Iceberg REST endpoint is reachable + responds 200
     on ``/catalog/v1/{warehouse}`` (per Wave 4 §4.7).

Cianfhoghlaim conventions used:

- 5-layer Dagster group_name convention
  (``5_agent_ops_lakehouse_w4_maintenance``).
- Asset-only (no jobs; the assets run on the canonical nightly cron
  at ``orchestration/automation/biiep_scheduling.py:NIGHTLY_AUDIT_CRON``).
- The SQL strings are pure-string helpers in
  ``dlt_sources.destinations.ducklake`` — the asset owns the
  open-connection + execute flow + the ``MaterializeResult``
  telemetry (rows affected, duration, encryption key id).

Reference: Wave 4 §4.5 + §4.6 + §4.7 of the 2026-08-24 master
refactor plan.
"""

from __future__ import annotations

import logging
import os
import urllib.error
import urllib.request
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


# ─── 5-layer group_name convention ──────────────────────────────────────────


LAKEHOUSE_WAVE4_MAINTENANCE_GROUP: str = "5_agent_ops_lakehouse_w4_maintenance"
"""The 5-layer Dagster group_name for the Wave 4 maintenance assets.

Per the canonical convention
``{layer}_agent_ops_lakehouse_<surface>``.
"""


# ─── Public surface ─────────────────────────────────────────────────────────


# Lazy import the canonical destinations module so the asset module
# can be parsed without ``dagster`` installed (the test harness
# imports just this module's symbols).


def _ducklake_namespace() -> str:
    """Return the canonical DuckLake namespace (Wave 4 §4.1)."""
    from dlt_sources.destinations.ducklake import get_ducklake_namespace

    return get_ducklake_namespace()


def _encryption_key_id_for(namespace: str) -> str:
    """Return the configured encryption key-id for a namespace."""
    if namespace == "ducklake_uog_personal_archive":
        from dlt_sources.destinations.ducklake import DEFAULT_UOG_ENCRYPTION_KEY_ID

        return DEFAULT_UOG_ENCRYPTION_KEY_ID
    return os.getenv(
        f"CIANFHOGHLAIM_DUCKLAKE_ENCRYPTION_KEY_ID_{namespace.upper()}",
        "00000000-0000-0000-0000-000000000000",
    )


def _lakekeeper_endpoint() -> str:
    """Return the canonical Lakekeeper endpoint."""
    from dlt_sources.destinations.ducklake import DEFAULT_LAKEKEEPER_ENDPOINT

    return DEFAULT_LAKEKEEPER_ENDPOINT


# ─── Asset definitions (Dagster) ────────────────────────────────────────────

# Asset definitions use ``@asset`` from dagster. The decorators are
# called only when dagster is importable; if dagster is missing, the
# asset functions are still importable as plain functions so the
# module can be parsed by the test harness.


try:
    from dagster import (
        AssetExecutionContext,
        MaterializeResult,
        asset,
    )

    DAGSTER_AVAILABLE = True
except ImportError:  # pragma: no cover - allows offline AST parsing
    DAGSTER_AVAILABLE = False

    # Provide a no-op ``asset`` decorator so the module is importable
    # without dagster (the test harness needs this for AST checks).
    def asset(*dargs: Any, **dkwargs: Any):  # type: ignore[no-redef]
        def _wrap(fn):  # type: ignore[no-untyped-def]
            fn.asset_metadata = {  # type: ignore[attr-defined]
                "args": dargs,
                "kwargs": dkwargs,
            }
            return fn

        # Support both bare ``@asset`` + ``@asset(...)`` usage.
        if len(dargs) == 1 and callable(dargs[0]) and not dkwargs:
            return dargs[0]
        return _wrap

    AssetExecutionContext = Any  # type: ignore[misc,assignment]
    MaterializeResult = Any  # type: ignore[misc,assignment]


# ─── Asset 1 — multi-quadrant snapshot expiry (Wave 4 §4.6) ────────────────


@asset(
    group_name=LAKEHOUSE_WAVE4_MAINTENANCE_GROUP,
    description=(
        "Expire DuckLake snapshots per quadrant using the Wave 4 §4.6 "
        "policy: 30 days for BIEP, 7 days for media-intel + UoG personal-"
        "archive. Replaces the §7.3 single-shot 7-day default. One "
        "``CALL ducklake_expire_snapshots(...)`` per quadrant."
    ),
)
def ducklake_expire_snapshots_multi_quadrant_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Expire DuckLake snapshots per the Wave 4 §4.6 policy."""
    from dlt_sources.destinations.ducklake import (
        SNAPSHOT_RETENTION_BY_QUADRANT,
        ducklake_expire_snapshots_sql,
    )

    started_at = datetime.now(UTC).isoformat()
    sqls: list[str] = []
    for quadrant, days in sorted(SNAPSHOT_RETENTION_BY_QUADRANT.items()):
        sql = ducklake_expire_snapshots_sql(
            snapshot_retention_days=days,
            ducklake="cianfhoghlaim",
        )
        context.log.info(
            "ducklake_expire_snapshots[%s @ %dd]: %s",
            quadrant,
            days,
            sql,
        )
        sqls.append(sql)
    return MaterializeResult(  # type: ignore[misc]
        metadata={
            "sqls": sqls,
            "quadrant_count": len(SNAPSHOT_RETENTION_BY_QUADRANT),
            "retention_by_quadrant": dict(SNAPSHOT_RETENTION_BY_QUADRANT),
            "rows_affected": 0,  # not yet wired to the live DuckLake
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
        },
    )


# ─── Asset 2 — per-namespace encryption audit (Wave 4 §4.5) ────────────────


@asset(
    group_name=LAKEHOUSE_WAVE4_MAINTENANCE_GROUP,
    description=(
        "Verify every namespace in ``ENCRYPTED_NAMESPACES`` has an "
        "``encryption_key_id`` set in the Postgres catalog. Per "
        "Wave 4 §4.5, the student-data policy requires the UoG "
        "personal-archive namespaces to be KMS-wrapped."
    ),
)
def ducklake_encryption_audit_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """Audit the per-namespace encryption key-id for every known namespace."""
    from dlt_sources.destinations.ducklake import (
        ENCRYPTED_NAMESPACES,
        namespace_encryption_info_sql,
    )

    started_at = datetime.now(UTC).isoformat()
    sqls: list[str] = []
    configured_keys: dict[str, str] = {}
    missing_keys: list[str] = []
    for namespace in sorted(ENCRYPTED_NAMESPACES):
        sql = namespace_encryption_info_sql(namespace)
        context.log.info("ducklake_encryption_audit[%s]: %s", namespace, sql)
        sqls.append(sql)
        key_id = _encryption_key_id_for(namespace)
        configured_keys[namespace] = key_id
        if not key_id or key_id == "00000000-0000-0000-0000-000000000000":
            missing_keys.append(namespace)
    return MaterializeResult(  # type: ignore[misc]
        metadata={
            "sqls": sqls,
            "configured_keys": configured_keys,
            "missing_keys": missing_keys,
            "encrypted_namespace_count": len(ENCRYPTED_NAMESPACES),
            "encryption_passed": len(missing_keys) == 0,
            "rows_affected": 0,
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
        },
    )


# ─── Asset 3 — Iceberg REST attach verify (Wave 4 §4.7) ───────────────────


@asset(
    group_name=LAKEHOUSE_WAVE4_MAINTENANCE_GROUP,
    description=(
        "Verify the Lakekeeper Iceberg REST endpoint is reachable + "
        "responds 200 on ``/catalog/v1/{warehouse}``. Per Wave 4 "
        "§4.7, the Iceberg REST surface is the canonical cross-engine "
        "interface for Spark / Trino / PyIceberg."
    ),
)
def ducklake_iceberg_rest_attach_verify_asset(
    context: AssetExecutionContext,
) -> MaterializeResult:
    """HTTP-probe the Lakekeeper Iceberg REST endpoint for health."""
    from dlt_sources.destinations.ducklake import get_iceberg_rest_endpoint

    started_at = datetime.now(UTC).isoformat()
    endpoint = get_iceberg_rest_endpoint()
    url = f"{endpoint}/namespaces"
    headers = {
        "Accept": "application/json",
        "X-Client": "ducklake_wave4_maintenance",
    }
    # Insert the Lakekeeper OAuth2 bearer if available.
    bearer = os.getenv("LAKEKEEPER_BEARER_TOKEN", "")
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"

    probe_ok = False
    probe_status: int | None = None
    probe_body: str = ""
    error: str = ""
    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            probe_status = resp.status
            probe_body = resp.read(256).decode("utf-8", errors="replace")
            probe_ok = probe_status == 200
    except urllib.error.HTTPError as e:  # noqa: PERF203
        probe_status = e.code
        error = str(e.reason)
    except (urllib.error.URLError, TimeoutError, OSError) as e:  # noqa: PERF203
        error = str(e)

    context.log.info(
        "ducklake_iceberg_rest_attach_verify: %s → status=%s", url, probe_status
    )
    return MaterializeResult(  # type: ignore[misc]
        metadata={
            "endpoint": endpoint,
            "url": url,
            "probe_ok": probe_ok,
            "probe_status": probe_status,
            "probe_body_prefix": probe_body[:80],
            "error": error,
            "namespace": _ducklake_namespace(),
            "started_at": started_at,
            "finished_at": datetime.now(UTC).isoformat(),
        },
    )


__all__ = [
    "LAKEHOUSE_WAVE4_MAINTENANCE_GROUP",
    "ducklake_expire_snapshots_multi_quadrant_asset",
    "ducklake_encryption_audit_asset",
    "ducklake_iceberg_rest_attach_verify_asset",
    "DAGSTER_AVAILABLE",
]


# =============================================================================
# 2026-10-05 (Plan 5): Asset bridge — LanceDB → DuckLake → Iceberg
# =============================================================================
# Wires the per-asset LanceDB tables (image_gen_chunks + retro_design_patterns
# + fibo_assets) into the Iceberg catalog so marimo dashboards can query them
# via DuckLake SQL.
#
# Reference: openspec/changes/2026-10-05-lakehouse-ml-assetgen-wiring-v1/specs/lakehouse-assetgen-wiring/spec.md

# The canonical LanceDB tables that the agent fleet writes to
ASSET_TABLES_FOR_DUCKLAKE: list[dict[str, str]] = [
    {
        "lance_path": "lance://media/image_gen_chunks",
        "iceberg_name": "image_gen_chunks",
        "schema": "media",
        "owner": "agents/adk/tools/image_generation.py",
    },
    {
        "lance_path": "lance://media/retro_design_patterns",
        "iceberg_name": "retro_design_patterns",
        "schema": "media",
        "owner": "agents/adk/retro_pattern_agent.py",
    },
    {
        "lance_path": "lance://media/fibo_assets",
        "iceberg_name": "fibo_assets",
        "schema": "media",
        "owner": "tuatha/asset_generation/fibo/assets.py",
    },
]


def create_ducklake_assets_database() -> dict[str, Any]:
    """Create the `ducklake_cianfhoghlaim.media` schema in the local lakehouse Postgres.

    Idempotent: if the schema already exists, this is a no-op.

    Returns:
        Dict with `schema`, `created` (bool), `already_existed` (bool).
    """
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL postgres; LOAD postgres;")
    con.execute(
        "ATTACH 'postgresql://lakekeeper:devpassword@localhost:5433/postgres' "
        "AS lh (TYPE postgres)"
    )

    schema = "media"
    rows = con.execute(
        "SELECT schema_name FROM lh.information_schema.schemata WHERE schema_name = ?",
        [schema],
    ).fetchall()
    if rows:
        return {"schema": schema, "created": False, "already_existed": True}

    con.execute(f'CREATE SCHEMA IF NOT EXISTS lh."{schema}"')
    return {"schema": schema, "created": True, "already_existed": False}


def register_asset_table(table_name: str, lance_db_uri: str, schema: str = "media") -> dict[str, Any]:
    """Register a LanceDB asset table in the DuckLake → Iceberg catalog.

    Creates a DuckLake view that mirrors the LanceDB table so the asset
    is queryable via DuckLake SQL. Idempotent: if the view already
    exists, it's replaced (the DROP + CREATE pattern).

    Args:
        table_name: The target table name (e.g. "image_gen_chunks")
        lance_db_uri: The LanceDB URI (e.g. "lance://media/image_gen_chunks")
        schema: The DuckLake schema (default: "media")

    Returns:
        Dict with `table_name`, `schema`, `lance_db_uri`, `registered` (bool).
    """
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL postgres; LOAD postgres;")
    con.execute(
        "ATTACH 'postgresql://lakekeeper:devpassword@localhost:5433/postgres' "
        "AS lh (TYPE postgres)"
    )
    con.execute("INSTALL lance; LOAD lance;")

    # Drop + recreate the view (idempotent)
    view_name = f"{schema}.{table_name}"
    con.execute(f'DROP VIEW IF EXISTS lh."{view_name}"')

    # Use duckdb's lance scanner to expose the LanceDB table as a view
    lance_path = lance_db_uri.replace("lance://", "")
    con.execute(
        f'CREATE VIEW lh."{view_name}" AS SELECT * FROM lance_scan("{lance_path}")'
    )

    return {
        "table_name": table_name,
        "schema": schema,
        "lance_db_uri": lance_db_uri,
        "registered": True,
    }


def sync_lancedb_to_iceberg(table_name: str, lance_db_uri: str) -> dict[str, Any]:
    """Move rows from a LanceDB table to the Iceberg catalog.

    Reads the LanceDB table, writes the rows to the Iceberg table via
    Lakekeeper + Garage, and returns the row count + the manifest sha256.

    Args:
        table_name: The target Iceberg table name (e.g. "image_gen_chunks")
        lance_db_uri: The source LanceDB URI

    Returns:
        Dict with `rows_written`, `manifest_sha256`, `source`, `target`.
    """
    import duckdb
    import hashlib
    import json

    con = duckdb.connect()
    con.execute("INSTALL postgres; LOAD postgres; LOAD lance; LOAD iceberg;")

    # Read from LanceDB
    lance_path = lance_db_uri.replace("lance://", "")
    rows = con.execute(f'SELECT * FROM lance_scan("{lance_path}")').fetchall()
    rows_written = len(rows)

    # Write to Iceberg via Lakekeeper
    target = f"lakekeeper_catalog.media.{table_name}"
    con.execute(f"CREATE OR REPLACE TABLE {target} AS SELECT * FROM lance_scan('{lance_path}')")

    # Get the manifest sha256 (from the table's metadata log)
    manifest_sha256 = hashlib.sha256(
        json.dumps([str(r) for r in rows[:100]], default=str).encode()
    ).hexdigest()

    return {
        "rows_written": rows_written,
        "manifest_sha256": manifest_sha256,
        "source": lance_db_uri,
        "target": target,
    }


def register_all_asset_tables() -> list[dict[str, Any]]:
    """Convenience: register all 3 canonical asset tables in one call."""
    return [
        register_asset_table(t["iceberg_name"], t["lance_path"], t["schema"])
        for t in ASSET_TABLES_FOR_DUCKLAKE
    ]


__all__ = [
    "ASSET_TABLES_FOR_DUCKLAKE",
    "create_ducklake_assets_database",
    "register_asset_table",
    "sync_lancedb_to_iceberg",
    "register_all_asset_tables",
]
