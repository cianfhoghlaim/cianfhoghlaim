#!/usr/bin/env python3
"""Wire testRuns.ingest to CI runners (closes GitHub issue #34).

Per the 2026-08-05-marimo-wasm-and-cigrunners-v1 change.

Every CI run on `main` calls the meaisinfhoghlaim agent fleet's
testRuns.ingest endpoint with the test counts and runtime. The
testRuns.ingest surfaces in the agent-platform-cluster dashboard.

Usage: python scripts/test_runs_ingest.py --dry-run
       python scripts/test_runs_ingest.py --passed=N --failed=M --runtime=R
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from typing import Any

# The canonical testRuns.ingest endpoint (meaisinfhoghlaim agent fleet)
TEST_RUNS_INGEST_URL = os.environ.get(
    "TEST_RUNS_INGEST_URL",
    "http://agents.cianfhoghlaim.ie/api/testRuns/ingest",
)


def build_payload(passed: int, failed: int, runtime: float) -> dict[str, Any]:
    """Build the testRuns.ingest payload."""
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "commit_sha": os.environ.get("GITHUB_SHA", "local"),
        "branch": os.environ.get("GITHUB_REF_NAME", "main"),
        "runner": os.environ.get("RUNNER_NAME", "local"),
        "passed": passed,
        "failed": failed,
        "runtime_seconds": runtime,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="testRuns.ingest to CI runners")
    parser.add_argument("--passed", type=int, default=0, help="Number of passed tests")
    parser.add_argument("--failed", type=int, default=0, help="Number of failed tests")
    parser.add_argument("--runtime", type=float, default=0.0, help="Runtime in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Print the payload without sending")
    args = parser.parse_args()

    payload = build_payload(args.passed, args.failed, args.runtime)
    print(json.dumps(payload, indent=2))

    if args.dry_run:
        print("\n(dry-run mode — payload NOT sent)")
        return 0

    # Real implementation: POST to the testRuns.ingest endpoint
    try:
        import urllib.request

        req = urllib.request.Request(
            TEST_RUNS_INGEST_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            print(f"\n✓ POSTed to {TEST_RUNS_INGEST_URL}: {resp.status}")
    except Exception as e:
        print(f"\nWARN: POST to {TEST_RUNS_INGEST_URL} failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
