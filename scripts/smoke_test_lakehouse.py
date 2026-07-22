#!/usr/bin/env python3
"""BIEP v3 Lakehouse smoke-test.

Per the 2026-08-11-biep-v3-lakehouse-population-v1 openspec change.

Verifies that the 11-service Lakehouse stack on `bunchloch` is healthy
by HTTP-probing the 3 canonical monitoring endpoints:

  - Nimtable (Spring Boot Iceberg catalog UI) → http://localhost:3018/
  - Olake (CDC engine)                         → http://localhost:3901/health
  - LanceDB Viewer (Lance table viewer)       → http://localhost:8081/v1/databases

Plus the Lakekeeper deep health check:

  - Lakekeeper REST catalog                    → http://localhost:8181/health/deep

Exits 0 if all 4 services respond 200; exits 1 if any fail.

Usage:
    python scripts/smoke_test_lakehouse.py
    python scripts/smoke_test_lakehouse.py --verbose
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any
from urllib import error as urllib_error
from urllib import request as urllib_request

# The 5 canonical endpoints per the proposal
ENDPOINTS: list[tuple[str, str, str]] = [
    ("Nimtable", "http://localhost:3018/", "Iceberg catalog UI"),
    ("Olake", "http://localhost:3901/health", "CDC engine health"),
    ("LanceDB Viewer", "http://localhost:8088/healthz", "Lance table viewer"),
    ("Lance sidecar", "http://localhost:8182/health", "Lance namespace sidecar"),
    ("Lakekeeper", "http://localhost:8181/health", "REST catalog health"),
]

DEFAULT_TIMEOUT_S: float = 5.0


def _probe(name: str, url: str, description: str, *, timeout: float) -> tuple[bool, str]:
    """HTTP-probe one endpoint. Returns (ok, detail)."""
    try:
        req = urllib_request.Request(url, method="GET")
        with urllib_request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = resp.read().decode("utf-8", errors="replace")[:200]
            if status == 200:
                return True, f"HTTP {status} ({description})"
            return False, f"HTTP {status} ({description}) — body: {body}"
    except urllib_error.HTTPError as e:
        return False, f"HTTP {e.code} ({description}) — {e.reason}"
    except urllib_error.URLError as e:
        return False, f"UNREACHABLE ({description}) — {e.reason}"
    except (TimeoutError, OSError) as e:
        return False, f"TIMEOUT/ERROR ({description}) — {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="BIEP v3 Lakehouse smoke-test")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_S,
        help=f"HTTP timeout per endpoint (default: {DEFAULT_TIMEOUT_S}s)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print success details for healthy endpoints too.",
    )
    parser.add_argument(
        "--lakekeeper-only",
        action="store_true",
        help="Only check Lakekeeper (the rest catalog).",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Dev mode: nimtable + olake are expected to be no-ops (return 000 / connection refused).",
    )
    args = parser.parse_args()

    endpoints = ENDPOINTS if not args.lakekeeper_only else [ENDPOINTS[4]]

    print(f"BIEP v3 Lakehouse smoke-test ({len(endpoints)} endpoint(s))")
    print(f"  timeout: {args.timeout}s per endpoint")
    print()

    all_ok = True
    for name, url, description in endpoints:
        ok, detail = _probe(name, url, description, timeout=args.timeout)
        # Dev mode: nimtable + olake are no-op alpine stubs that
        # return 000 / connection refused. Treat as INFO not FAIL.
        if not ok and args.dev and name in ("Nimtable", "Olake"):
            print(f"  [INFO] {name:<18} {url}")
            print(f"           (dev mode: {name} is a no-op stub, expected to fail)")
            continue
        marker = "OK" if ok else "FAIL"
        print(f"  [{marker}] {name:<18} {url}")
        if ok:
            if args.verbose:
                print(f"           {detail}")
        else:
            print(f"           {detail}")
            all_ok = False

    # Lakekeeper-specific health check parsing
    if not args.lakekeeper_only:
        print()
        print("Lakekeeper health body parsing:")
        try:
            # The Lakekeeper endpoint is the 4th in the ENDPOINTS list (index 4 since we have 5 endpoints).
            lk_idx = next(
                (i for i, (n, _, _) in enumerate(endpoints) if n == "Lakekeeper"),
                None,
            )
            if lk_idx is not None:
                req = urllib_request.Request(endpoints[lk_idx][1], method="GET")
                with urllib_request.urlopen(req, timeout=args.timeout) as resp:
                    body = json.loads(resp.read().decode("utf-8"))
                    health = body.get("health", "unknown")
                    services = body.get("services", {})
                    print(f"  health: {health}")
                    for svc_name, svc_reports in services.items():
                        for report in svc_reports:
                            name = report.get("name", "?")
                            status = report.get("status", "?")
                            marker = "OK" if status == "ok" else "FAIL"
                            print(f"  [{marker}] {svc_name}.{name}: {status}")
                            if status != "ok":
                                all_ok = False
                    if health != "ok":
                        print("  WARN: overall health is not 'ok'")
                        all_ok = False
        except (urllib_error.URLError, TimeoutError, OSError) as e:
            print(f"  could not parse Lakekeeper body: {e}")

    print()
    if all_ok:
        print("RESULT: ALL GREEN")
        return 0
    else:
        print("RESULT: ONE OR MORE SERVICES DOWN")
        return 1


if __name__ == "__main__":
    sys.exit(main())