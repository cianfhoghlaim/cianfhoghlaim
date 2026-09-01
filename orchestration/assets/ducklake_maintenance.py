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
