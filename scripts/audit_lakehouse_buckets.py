#!/usr/bin/env python3
"""Audit the 8 canonical Garage S3 buckets in the lakehouse.

Per the 2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1
openspec change.

The 8 buckets are created by the `garage-init` 1-shot service in
`bonneagar/stacks/lakehouse/compose.yaml` (lines 155-180). They are:

  - iceberg, lance, ducklake, ducklake-cianfhoghlaim
  - langfuse-events, langfuse-media, langfuse-exports
  - mlflow-artifacts

This helper uses urllib3 (NOT awscli) so it works on the dev box
without the AWS CLI tooling installed. It hits the Garage admin API
at `http://localhost:3904/v1/bucket` with the configured admin token
(`GARAGE_ADMIN_TOKEN` env var) and parses the JSON response.

Usage:
    python3 scripts/audit_lakehouse_buckets.py
    python3 scripts/audit_lakehouse_buckets.py --endpoint http://lakehouse-garage:3904
    python3 scripts/audit_lakehouse_buckets.py --json

Exits 0 if all 8 expected buckets exist; exits 1 if any are missing.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import urllib3

# The 8 canonical buckets (created by garage-init on first docker compose up).
EXPECTED_BUCKETS: tuple[str, ...] = (
    "iceberg",
    "lance",
    "ducklake",
    "ducklake-cianfhoghlaim",
    "langfuse-events",
    "langfuse-media",
    "langfuse-exports",
    "mlflow-artifacts",
)


def list_buckets(endpoint: str, admin_token: str, timeout: float = 5.0) -> list[dict[str, Any]]:
    """GET /v1/bucket from the Garage admin API. Returns the bucket list."""
    http = urllib3.PoolManager(retries=urllib3.Retry(total=2, backoff_factor=0.3))
    url = f"{endpoint.rstrip('/')}/v1/bucket"
    resp = http.request(
        "GET",
        url,
        headers={"Authorization": f"Bearer {admin_token}"},
        timeout=timeout,
    )
    if resp.status != 200:
        raise RuntimeError(
            f"Garage admin API returned HTTP {resp.status}: {resp.data[:200].decode('utf-8', errors='replace')}"
        )
    return json.loads(resp.data.decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the 8 canonical Garage S3 buckets")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("GARAGE_ADMIN_URL", "http://localhost:3904"),
        help="Garage admin API endpoint (default: $GARAGE_ADMIN_URL or http://localhost:3904)",
    )
    parser.add_argument(
        "--admin-token",
        default=os.environ.get("GARAGE_ADMIN_TOKEN", ""),
        help="Garage admin token (default: $GARAGE_ADMIN_TOKEN — required for the admin API)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="HTTP timeout per request (default: 5s)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON to stdout (machine-readable)",
    )
    args = parser.parse_args()

    if not args.admin_token:
        if args.json:
            print(json.dumps({"error": "GARAGE_ADMIN_TOKEN not set", "missing": list(EXPECTED_BUCKETS)}))
        else:
            print("ERROR: GARAGE_ADMIN_TOKEN not set in env (lakehouse/secrets.env or .env)")
            print("  Set it via `mise run secrets:init` or `.infisical.env`")
        return 2

    try:
        buckets = list_buckets(args.endpoint, args.admin_token, args.timeout)
    except Exception as e:
        if args.json:
            print(json.dumps({"error": f"bucket_list_failed: {e}"}))
        else:
            print(f"ERROR: {e}")
        return 2

    actual_names = {b.get("name") for b in buckets if b.get("name")}
    missing = [name for name in EXPECTED_BUCKETS if name not in actual_names]
    extra = sorted(actual_names - set(EXPECTED_BUCKETS))

    if args.json:
        print(
            json.dumps(
                {
                    "endpoint": args.endpoint,
                    "expected": list(EXPECTED_BUCKETS),
                    "actual": sorted(actual_names),
                    "missing": missing,
                    "extra": extra,
                    "ok": not missing,
                },
                indent=2,
            )
        )
    else:
        print(f"Garage buckets at {args.endpoint}: {len(actual_names)} total")
        for name in EXPECTED_BUCKETS:
            mark = "✓" if name in actual_names else "✗"
            print(f"  {mark} {name}")
        if extra:
            print(f"  (extra buckets not in expected set: {extra})")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())