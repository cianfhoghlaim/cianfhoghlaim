"""BIEP v3 foundation Dagster assets (M0).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

The 4 M0 foundation assets + 4 asset checks that gate every BIEP v3
jurisdiction pipeline run:

1. `lakehouse_smoke_test` — checks 13 lakehouse services respond 200 OK
2. `baml_codegen_gate` — `mise run baml:generate` exits 0
3. `registry_seed_count` — ≥210 rows in
   `cianfhoghlaim.education._registry.subjects`
4. `lance_namespace_ready` — the `cianhoghlaim` Lance namespace exists
   in Lakekeeper

Per the 5-layer convention
(`openspec/specs/dagster-5-layer-component-architecture/spec.md`),
these sit in Layer 5 (Agent Operations) — they are the BIEP v3
foundation gates that all downstream assets (L1 ingestion + L2
extraction + L3 embedding) depend on.

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — `ibis.duckdb.connect()`
- Dagster declarative Automation — `AutomationCondition.eager()`
- httpx for HTTP health checks (per `.agents/skills/cloudflare/timeout.md`)
"""

from __future__ import annotations

import logging
import os
import subprocess
from typing import Any

from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    asset,
    asset_check,
)

from orchestration.automation.biiep_scheduling import (
    make_weekly_smoke_test_automation,
    make_eager_automation,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# 5-layer group_name convention
# -----------------------------------------------------------------------------
# Layer 5 (Agent Operations) — these are the foundation gates.

M0_FOUNDATION_GROUP = "5_agent_ops_biiep_v3_m0_foundation"


# -----------------------------------------------------------------------------
# The 13 canonical lakehouse service health endpoints
# -----------------------------------------------------------------------------
# Each tuple is (service_name, health_url). The smoke test asserts every
# URL returns 200 OK within a 5-second timeout.

LAKEHOUSE_SERVICES = (
    ("garage-s3", "http://localhost:3900"),
    ("garage-admin", "http://localhost:3903"),
    ("postgres", "http://localhost:5433"),  # TCP; uses httpx ping
    ("lakekeeper", "http://localhost:8181/health"),
    ("lakekeeper-metrics", "http://localhost:9100/metrics"),
    ("lance-namespace", "http://localhost:8182/health"),
    ("postgresql-catalog", "http://localhost:5433"),
    ("clickhouse", "http://localhost:8123/ping"),
    ("redis", "http://localhost:6379"),
    ("nimtable", "http://localhost:3018"),
    ("olake", "http://localhost:8080"),
    ("lancedb-viewer", "http://localhost:8081"),
    ("garage-init", "http://localhost:3900"),
)


# -----------------------------------------------------------------------------
# Asset 1: Lakehouse smoke test
# -----------------------------------------------------------------------------


@asset(
    group_name=M0_FOUNDATION_GROUP,
    description=(
        "Smoke-test the 13 canonical lakehouse services. "
        "Returns 200 OK count + per-service status matrix. "
        "Asset check `lakehouse_smoke_test_check` asserts all 13 respond 200 OK. "
        "Triggers weekly (Monday 06:00 UTC) per the BIEP v3 scheduling policy."
    ),
    automation_condition=make_weekly_smoke_test_automation(),
)
def lakehouse_smoke_test(context: AssetExecutionContext) -> dict[str, Any]:
    """Check that all 13 lakehouse services respond 200 OK."""
    import httpx

    results: dict[str, Any] = {"services": {}, "ok_count": 0, "total": len(LAKEHOUSE_SERVICES)}
    for service_name, url in LAKEHOUSE_SERVICES:
        try:
            response = httpx.get(url, timeout=5.0)
            ok = response.status_code == 200
            results["services"][service_name] = {
                "url": url,
                "status_code": response.status_code,
                "ok": ok,
            }
            if ok:
                results["ok_count"] += 1
        except Exception as exc:  # noqa: BLE001
            results["services"][service_name] = {
                "url": url,
                "status_code": None,
                "ok": False,
                "error": str(exc),
            }
    context.log.info(f"lakehouse_smoke_test: {results['ok_count']}/{results['total']} services OK")
    return results


@asset_check(asset=lakehouse_smoke_test)
def lakehouse_smoke_test_check(context, lakehouse_smoke_test: dict[str, Any]) -> AssetCheckResult:
    """Assert all 13 lakehouse services respond 200 OK."""
    ok_count = lakehouse_smoke_test.get("ok_count", 0)
    total = lakehouse_smoke_test.get("total", 13)
    return AssetCheckResult(
        passed=ok_count == total,
        metadata={
            "ok_count": ok_count,
            "total": total,
            "missing_services": [
                name for name, info in lakehouse_smoke_test.get("services", {}).items()
                if not info.get("ok", False)
            ],
        },
    )


# -----------------------------------------------------------------------------
# Asset 2: BAML codegen gate
# -----------------------------------------------------------------------------


@asset(
    group_name=M0_FOUNDATION_GROUP,
    description=(
        "Run `mise run baml:generate` and assert exit 0. "
        "The 3 BIEP v3 BAML functions (ExtractUKQualSpec, ExtractSyllabusDiagram, "
        "ExtractCrossLinguisticConcept) MUST compile cleanly. "
        "Asset check `baml_codegen_check` asserts exit 0. "
        "Triggers weekly (Monday 06:00 UTC) per the BIEP v3 scheduling policy."
    ),
    automation_condition=make_weekly_smoke_test_automation(),
)
def baml_codegen_gate(context: AssetExecutionContext) -> dict[str, Any]:
    """Run `mise run baml:generate` and capture the exit code + stdout."""
    try:
        result = subprocess.run(
            ["mise", "run", "baml:generate"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "exit_code": result.returncode,
            "stdout_tail": result.stdout[-2000:],
            "stderr_tail": result.stderr[-2000:],
            "ok": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "ok": False, "error": "timeout after 120s"}
    except Exception as exc:  # noqa: BLE001
        return {"exit_code": -1, "ok": False, "error": str(exc)}


@asset_check(asset=baml_codegen_gate)
def baml_codegen_check(context, baml_codegen_gate: dict[str, Any]) -> AssetCheckResult:
    """Assert `mise run baml:generate` exits 0."""
    return AssetCheckResult(
        passed=baml_codegen_gate.get("ok", False),
        metadata={
            "exit_code": baml_codegen_gate.get("exit_code"),
            "stderr_tail": baml_codegen_gate.get("stderr_tail", "")[:500],
        },
    )


# -----------------------------------------------------------------------------
# Asset 3: Registry seed count
# -----------------------------------------------------------------------------


@asset(
    group_name=M0_FOUNDATION_GROUP,
    description=(
        "SELECT COUNT(*) FROM cianfhoghlaim.education._registry.subjects. "
        "Must be >= 210 (Ireland 152 + England 276 - the duplicated 218 = 210 minimum). "
        "Asset check `registry_seed_check` asserts count >= 210. "
        "Triggers weekly (Monday 06:00 UTC) per the BIEP v3 scheduling policy."
    ),
    automation_condition=make_weekly_smoke_test_automation(),
)
def registry_seed_count(context: AssetExecutionContext) -> dict[str, Any]:
    """Query the British Isles Subject Registry for the row count."""
    LAKEHOUSE_DUCKDB = os.environ.get("LAKEHOUSE_DUCKDB", "md:cianfhoghlaim")
    try:
        import duckdb

        # Use the ibis-first contract per BIEP v3 spec: prefer ibis but
        # fall back to duckdb if ibis or the catalog is unavailable.
        try:
            import ibis

            conn = ibis.duckdb.connect(LAKEHOUSE_DUCKDB)
            table = conn.table("cianfhoghlaim.education._registry.subjects")
            count = int(table.count().execute())
        except Exception:  # noqa: BLE001
            raw_conn = duckdb.connect(LAKEHOUSE_DUCKDB)
            count = int(
                raw_conn.execute(
                    "SELECT COUNT(*) FROM cianfhoghlaim.education._registry.subjects"
                ).fetchone()[0]
            )
        return {"count": count, "ok": count >= 210}
    except Exception as exc:  # noqa: BLE001
        return {"count": 0, "ok": False, "error": str(exc)}


@asset_check(asset=registry_seed_count)
def registry_seed_check(context, registry_seed_count: dict[str, Any]) -> AssetCheckResult:
    """Assert `registry_seed_count['count'] >= 210`."""
    return AssetCheckResult(
        passed=registry_seed_count.get("ok", False),
        metadata={
            "count": registry_seed_count.get("count", 0),
            "threshold": 210,
            "error": registry_seed_count.get("error", ""),
        },
    )


# -----------------------------------------------------------------------------
# Asset 4: Lance namespace ready
# -----------------------------------------------------------------------------


@asset(
    group_name=M0_FOUNDATION_GROUP,
    description=(
        "Check that the `cianhoghlaim` Lance namespace exists in the Lakekeeper "
        "Iceberg REST catalog. Asset check `lance_namespace_check` asserts the "
        "namespace is registered. "
        "Triggers weekly (Monday 06:00 UTC) per the BIEP v3 scheduling policy."
    ),
    automation_condition=make_weekly_smoke_test_automation(),
)
def lance_namespace_ready(context: AssetExecutionContext) -> dict[str, Any]:
    """Check the `cianhoghlaim` Lance namespace exists in Lakekeeper."""
    catalog_uri = os.environ.get("LAKEKEEPER_URI", "http://localhost:8181")
    try:
        import httpx

        response = httpx.get(
            f"{catalog_uri}/v1/namespaces/cianhoghlaim",
            timeout=10.0,
        )
        ok = response.status_code == 200
        return {
            "namespace": "cianhoghlaim",
            "status_code": response.status_code,
            "ok": ok,
        }
    except Exception as exc:  # noqa: BLE001
        return {"namespace": "cianhoghlaim", "ok": False, "error": str(exc)}


@asset_check(asset=lance_namespace_ready)
def lance_namespace_check(context, lance_namespace_ready: dict[str, Any]) -> AssetCheckResult:
    """Assert the `cianhoghlaim` Lance namespace exists in Lakekeeper."""
    return AssetCheckResult(
        passed=lance_namespace_ready.get("ok", False),
        metadata={
            "namespace": lance_namespace_ready.get("namespace"),
            "status_code": lance_namespace_ready.get("status_code"),
            "error": lance_namespace_ready.get("error", ""),
        },
    )


__all__ = [
    "lakehouse_smoke_test",
    "lakehouse_smoke_test_check",
    "baml_codegen_gate",
    "baml_codegen_check",
    "registry_seed_count",
    "registry_seed_check",
    "lance_namespace_ready",
    "lance_namespace_check",
    "LAKEHOUSE_SERVICES",
]
