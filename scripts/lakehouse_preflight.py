#!/usr/bin/env python3
"""Lakehouse preflight — CI-friendly health check for the bunchloch lakehouse.

Per the 2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1
openspec change. Validates:

  1. The 5 REQUIRED endpoints (all must respond 200):
     - Nimtable (Iceberg catalog UI)        → http://localhost:3018/
     - Olake (CDC engine)                   → http://localhost:3901/health
     - LanceDB Viewer                       → http://localhost:8081/healthz
     - Lance namespace sidecar             → http://localhost:8182/v1/info
     - Lakekeeper (REST catalog)            → http://localhost:8181/health

  2. The 12 POSTGRES databases (created by init-db.sql):
     - ducklake_{cianfhoghlaim,crypteolas,aleyum,croilar,tuath,meaisinfhoghlaim}
     - dagster_local, olake_state, nimtable
     - langfuse, mlflow, litellm

  3. The 8 GARAGE buckets (created by garage-init):
     - iceberg, lance, ducklake, ducklake-cianfhoghlaim
     - langfuse-events, langfuse-media, langfuse-exports
     - mlflow-artifacts

  4. The 5 OPTIONAL memory backends (graceful skip when not deployed):
     - cognee      → http://localhost:8100/health
     - graphiti    → http://localhost:8000/healthcheck
     - falkordb    → redis-cli -h falkordb ping
     - memgraph    → http://localhost:7687 (Bolt endpoint)
     - lancedb     → the lance-namespace sidecar (already in #1)

The cognify probe is REQUIRED only when BIEP M5+ (cognify) is on the
bringup list. For M1-M4 (Ireland LC + JC, England A-Level + GCSE),
it's OPTIONAL — operators run the preflight without the cognify stack.

Exit codes:
  0 = all required probes passed (cognify probes may be skipped)
  1 = at least one required probe failed (actionable error)
  2 = script error (missing env vars, docker not running)

Usage:
  mise run lakehouse:preflight                          # human-readable
  mise run lakehouse:preflight --json                   # machine-readable
  mise run lakehouse:preflight --strict-cognify        # require cognify too
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request


# 5 required lakehouse endpoints
REQUIRED_ENDPOINTS: list[tuple[str, str, str, str]] = [
    (
        "Nimtable",
        "http://localhost:3018/",
        "Iceberg catalog UI",
        "GET /",
    ),
    (
        "Olake",
        "http://localhost:3901/health",
        "CDC engine",
        "GET /health",
    ),
    (
        "LanceDB Viewer",
        "http://localhost:8081/healthz",
        "Lance table viewer",
        "GET /healthz",
    ),
    (
        "Lance namespace sidecar",
        "http://localhost:8182/v1/info",
        "Lance namespace (Iceberg bridge)",
        "GET /v1/info",
    ),
    (
        "Lakekeeper",
        "http://localhost:8181/health",
        "Iceberg REST catalog",
        "GET /health",
    ),
]

# 12 expected postgres databases
EXPECTED_DATABASES: tuple[str, ...] = (
    "ducklake_cianfhoghlaim",
    "ducklake_crypteolas",
    "ducklake_aleyum",
    "ducklake_croilar",
    "ducklake_tuath",
    "ducklake_meaisinfhoghlaim",
    "dagster_local",
    "olake_state",
    "nimtable",
    "langfuse",
    "mlflow",
    "litellm",
)

# 5 optional (cognify) memory backends — probed but skipped when not deployed
OPTIONAL_COGNIFY: list[tuple[str, str, str, str]] = [
    (
        "cognee",
        "http://cognee:8000/health",
        "Structured KG",
        "GET /health",
    ),
    (
        "graphiti",
        "http://graphiti:8000/healthcheck",
        "Temporal KG",
        "GET /healthcheck",
    ),
    (
        "falkordb",
        "falkordb:6379",
        "Vector+graph hybrid (vector.so)",
        "TCP probe",
    ),
    (
        "memgraph",
        "memgraph:7687",
        "Production graph (Cypher + MAGE)",
        "TCP probe",
    ),
]


DEFAULT_TIMEOUT_S: float = 5.0


def _http_probe(url: str, timeout: float) -> tuple[bool, str]:
    """HTTP GET probe. Returns (ok, detail)."""
    try:
        req = urllib_request.Request(url, method="GET")
        with urllib_request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")[:120]
            if status == 200:
                return True, f"HTTP 200 ({body[:80]})"
            return False, f"HTTP {status} — body: {body}"
    except urllib_error.HTTPError as e:
        return False, f"HTTP {e.code} — {e.reason}"
    except urllib_error.URLError as e:
        return False, f"UNREACHABLE — {e.reason}"
    except (TimeoutError, OSError) as e:
        return False, f"TIMEOUT — {e}"


def _tcp_probe(hostport: str, timeout: float) -> tuple[bool, str]:
    """TCP-connect probe. Returns (ok, detail)."""
    try:
        host, port_s = hostport.split(":")
        with socket.create_connection((host, int(port_s)), timeout=timeout):
            pass
        return True, "TCP connect OK"
    except (OSError, socket.timeout) as e:
        return False, f"TCP unreachable — {e}"


def _list_databases() -> tuple[set[str] | None, str]:
    """Probe the postgres container for the 12 expected databases.
    Uses `docker exec lakehouse-postgres psql -lAqt` if available.
    Returns (set of db names, error)."""
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "lakehouse-postgres",
                "psql",
                "-U",
                "lakekeeper",
                "-d",
                "postgres",
                "-lAqt",
                "-c",
                "SELECT datname FROM pg_database WHERE datistemplate = false;",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None, f"psql failed: {result.stderr.strip()}"
        db_names = {line.strip() for line in result.stdout.splitlines() if line.strip()}
        return db_names, ""
    except subprocess.TimeoutExpired:
        return None, "psql timeout"
    except FileNotFoundError:
        return None, "docker CLI not found"


def _check_buckets() -> tuple[set[str], str]:
    """Delegate to scripts/audit_lakehouse_buckets.py for the Garage bucket probe."""
    try:
        result = subprocess.run(
            [sys.executable, "scripts/audit_lakehouse_buckets.py", "--json"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode not in (0, 1):
            return set(), f"bucket audit failed: {result.stderr.strip()}"
        data = json.loads(result.stdout)
        if "actual" not in data:
            return set(), f"bucket audit error: {data.get('error', 'unknown')}"
        return set(data["actual"]), ""
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError) as e:
        return set(), f"bucket audit error: {e}"


def _probe_section(
    label: str,
    items: list[tuple[str, str, str, str]],
    probe_fn,
    timeout: float,
) -> list[dict[str, Any]]:
    """Probe a section of endpoints + return per-item status dicts."""
    results: list[dict[str, Any]] = []
    for name, url, purpose, verb in items:
        started = time.monotonic()
        ok, detail = probe_fn(url, timeout)
        elapsed_ms = round((time.monotonic() - started) * 1000, 1)
        results.append(
            {
                "name": name,
                "url": url,
                "purpose": purpose,
                "verb": verb,
                "status": "healthy" if ok else "not_healthy",
                "latency_ms": elapsed_ms,
                "detail": detail,
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Lakehouse preflight (local-bunchloch)")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_S,
        help=f"Per-probe timeout in seconds (default: {DEFAULT_TIMEOUT_S}s)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON to stdout (machine-readable)",
    )
    parser.add_argument(
        "--strict-cognify",
        action="store_true",
        help="REQUIRE the cognify backends (default: skip if unreachable)",
    )
    parser.add_argument(
        "--skip-buckets",
        action="store_true",
        help="Skip the Garage bucket audit (faster preflight)",
    )
    parser.add_argument(
        "--skip-databases",
        action="store_true",
        help="Skip the postgres database audit",
    )
    args = parser.parse_args()

    summary: dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "required": [],
        "databases": [],
        "buckets": [],
        "cognify": [],
    }

    # 1. Required endpoints
    summary["required"] = _probe_section(
        "required",
        REQUIRED_ENDPOINTS,
        _http_probe,
        args.timeout,
    )

    # 2. Postgres databases
    if not args.skip_databases:
        db_actual, db_error = _list_databases()
        if db_actual is None:
            summary["databases"] = [
                {"status": "error", "error": db_error, "expected": list(EXPECTED_DATABASES)}
            ]
        else:
            db_results = []
            for db_name in EXPECTED_DATABASES:
                db_results.append(
                    {
                        "name": db_name,
                        "status": "present" if db_name in db_actual else "missing",
                    }
                )
            summary["databases"] = db_results

    # 3. Garage buckets
    if not args.skip_buckets:
        bucket_actual, bucket_error = _check_buckets()
        if bucket_error and not bucket_actual:
            summary["buckets"] = [{"status": "error", "error": bucket_error}]
        else:
            from scripts.audit_lakehouse_buckets import EXPECTED_BUCKETS

            bucket_results = []
            for name in EXPECTED_BUCKETS:
                bucket_results.append(
                    {
                        "name": name,
                        "status": "present" if name in bucket_actual else "missing",
                    }
                )
            summary["buckets"] = bucket_results

    # 4. Optional cognify backends
    cognify_results: list[dict[str, Any]] = []
    for name, target, purpose, verb in OPTIONAL_COGNIFY:
        started = time.monotonic()
        if target.startswith("http"):
            ok, detail = _http_probe(target, args.timeout)
        else:
            ok, detail = _tcp_probe(target, args.timeout)
        elapsed_ms = round((time.monotonic() - started) * 1000, 1)
        cognify_results.append(
            {
                "name": name,
                "url": target,
                "purpose": purpose,
                "verb": verb,
                "status": "healthy" if ok else "skipped",
                "latency_ms": elapsed_ms,
                "detail": detail,
            }
        )
    summary["cognify"] = cognify_results

    # Compute overall status
    required_failed = [r for r in summary["required"] if r["status"] != "healthy"]
    db_missing = (
        [r for r in summary["databases"] if r.get("status") == "missing"]
        if isinstance(summary["databases"], list)
        else []
    )
    bucket_missing = (
        [r for r in summary["buckets"] if r.get("status") == "missing"]
        if isinstance(summary["buckets"], list)
        else []
    )
    cognify_failed = (
        [r for r in cognify_results if r["status"] != "healthy"]
        if args.strict_cognify
        else []
    )

    summary["summary"] = {
        "required_total": len(summary["required"]),
        "required_healthy": len(summary["required"]) - len(required_failed),
        "databases_missing": len(db_missing),
        "buckets_missing": len(bucket_missing),
        "cognify_skipped": len(
            [r for r in cognify_results if r["status"] == "skipped"]
        ),
        "cognify_healthy": len(
            [r for r in cognify_results if r["status"] == "healthy"]
        ),
        "ok": not required_failed and not db_missing and not bucket_missing and not cognify_failed,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"=== Lakehouse preflight ({time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}) ===\n")
        # Required
        print(f"REQUIRED endpoints ({summary['summary']['required_healthy']}/{summary['summary']['required_total']} healthy):")
        for r in summary["required"]:
            mark = "✓" if r["status"] == "healthy" else "✗"
            print(f"  {mark} {r['name']:30} ({r['latency_ms']}ms) — {r['detail']}")
        # Databases
        if not args.skip_databases and isinstance(summary["databases"], list) and summary["databases"]:
            print(f"\nPOSTGRES databases ({12 - summary['summary']['databases_missing']}/12 present):")
            if isinstance(summary["databases"][0], dict) and "error" in summary["databases"][0]:
                print(f"  ✗ {summary['databases'][0]['error']}")
            else:
                for r in summary["databases"]:
                    mark = "✓" if r["status"] == "present" else "✗"
                    print(f"  {mark} {r['name']}")
        # Buckets
        if not args.skip_buckets and isinstance(summary["buckets"], list) and summary["buckets"]:
            print(f"\nGARAGE buckets ({8 - summary['summary']['buckets_missing']}/8 present):")
            if isinstance(summary["buckets"][0], dict) and "error" in summary["buckets"][0]:
                print(f"  ✗ {summary['buckets'][0]['error']}")
            else:
                for r in summary["buckets"]:
                    mark = "✓" if r["status"] == "present" else "✗"
                    print(f"  {mark} {r['name']}")
        # Cognify
        print(f"\nCOGNIFY stack ({summary['summary']['cognify_healthy']}/{len(OPTIONAL_COGNIFY)} reachable, skipped = {summary['summary']['cognify_skipped']}):")
        for r in cognify_results:
            mark = "✓" if r["status"] == "healthy" else ("⊘" if r["status"] == "skipped" else "✗")
            print(f"  {mark} {r['name']:14} ({r['url']}) — {r['detail']}")
        # Summary
        ok = summary["summary"]["ok"]
        print(f"\n{'✓ OK' if ok else '✗ FAILED'}: preflight {('succeeded' if ok else 'failed')}")

    return 0 if summary["summary"]["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())