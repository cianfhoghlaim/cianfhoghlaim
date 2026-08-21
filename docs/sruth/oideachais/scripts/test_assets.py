#!/usr/bin/env python
"""
Test asset materialization programmatically via Dagster GraphQL API.

Usage:
    # Materialize single asset
    python scripts/test_assets.py ireland education seed_data

    # Materialize with custom endpoint
    python scripts/test_assets.py --url http://localhost:3000/graphql celtic duchas pages

    # List all assets
    python scripts/test_assets.py --list

    # Check backfill status
    python scripts/test_assets.py --status <backfill_id>

    # Wait for completion
    python scripts/test_assets.py --wait ireland education seed_data
"""

import argparse
import json
import os
import sys
import time
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: uv pip install requests")
    sys.exit(1)


class DagsterClient:
    """Simple client for Dagster GraphQL API."""

    def __init__(self, url: str = None):
        self.url = url or os.getenv("DAGSTER_URL", "http://localhost:64583/graphql")

    def _query(self, query: str, variables: dict = None) -> dict:
        """Execute a GraphQL query."""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        resp = requests.post(self.url, json=payload)
        data = resp.json()
        if "errors" in data:
            raise Exception(f"GraphQL errors: {data['errors']}")
        return data["data"]

    def list_assets(self) -> list[dict]:
        """List all available assets."""
        query = """
        {
            assetsOrError {
                ... on AssetConnection {
                    nodes {
                        key { path }
                        definition { description }
                    }
                }
            }
        }
        """
        return self._query(query)["assetsOrError"]["nodes"]

    def materialize_asset(self, asset_path: list[str]) -> str:
        """
        Materialize an asset via GraphQL backfill and return backfill ID.

        Uses launchPartitionBackfill which works for both partitioned
        and unpartitioned assets.
        """
        query = """
        mutation MaterializeAsset($assetSelection: [AssetKeyInput!]!) {
            launchPartitionBackfill(backfillParams: {
                assetSelection: $assetSelection
                allPartitions: true
            }) {
                ... on LaunchBackfillSuccess { backfillId }
                ... on PythonError { message stack }
                ... on InvalidOutputError { stepKey invalidOutputName }
                ... on UnauthorizedError { message }
                ... on PartitionKeysNotFoundError { message }
            }
        }
        """
        variables = {"assetSelection": [{"path": asset_path}]}
        result = self._query(query, variables)["launchPartitionBackfill"]

        if "message" in result:
            raise Exception(f"Error: {result['message']}")
        if "backfillId" not in result:
            raise Exception(f"Unexpected result: {result}")

        return result["backfillId"]

    def check_backfill_status(self, backfill_id: str) -> dict:
        """Check status of a backfill."""
        query = """
        query CheckBackfill($backfillId: String!) {
            partitionBackfillOrError(backfillId: $backfillId) {
                ... on PartitionBackfill {
                    id
                    status
                    numPartitions
                    assetBackfillData {
                        assetBackfillStatuses {
                            ... on UnpartitionedAssetStatus {
                                assetKey { path }
                                materialized
                                failed
                                inProgress
                            }
                            ... on AssetPartitionsStatusCounts {
                                assetKey { path }
                                numPartitionsTargeted
                                numPartitionsMaterialized
                                numPartitionsFailed
                            }
                        }
                    }
                }
                ... on PythonError { message }
                ... on BackfillNotFoundError { message }
            }
        }
        """
        return self._query(query, {"backfillId": backfill_id})["partitionBackfillOrError"]

    def wait_for_completion(
        self, backfill_id: str, timeout: int = 300, poll_interval: int = 2
    ) -> dict:
        """Wait for backfill to complete."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.check_backfill_status(backfill_id)

            if "message" in status:
                raise Exception(status["message"])

            backfill_status = status.get("status")
            if backfill_status in ("COMPLETED", "COMPLETED_FAILED", "FAILED", "CANCELED"):
                return status

            # Check individual asset statuses
            asset_statuses = status.get("assetBackfillData", {}).get("assetBackfillStatuses", [])
            all_done = all(
                s.get("materialized", False) or s.get("failed", False)
                for s in asset_statuses
                if "materialized" in s  # UnpartitionedAssetStatus
            )
            if all_done and asset_statuses:
                return status

            time.sleep(poll_interval)

        raise TimeoutError(f"Backfill {backfill_id} did not complete within {timeout}s")


def main():
    parser = argparse.ArgumentParser(
        description="Test Dagster asset materialization via GraphQL API"
    )
    parser.add_argument(
        "asset_path", nargs="*", help="Asset path components (e.g., ireland education seed_data)"
    )
    parser.add_argument("--list", "-l", action="store_true", help="List all available assets")
    parser.add_argument("--status", "-s", metavar="BACKFILL_ID", help="Check status of a backfill")
    parser.add_argument(
        "--wait", "-w", action="store_true", help="Wait for materialization to complete"
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=300,
        help="Timeout in seconds when waiting (default: 300)",
    )
    parser.add_argument(
        "--url", "-u", help="Dagster GraphQL URL (default: http://localhost:64583/graphql)"
    )

    args = parser.parse_args()
    client = DagsterClient(url=args.url)

    try:
        if args.list:
            assets = client.list_assets()
            print(f"Found {len(assets)} assets:\n")
            for asset in assets:
                path = "/".join(asset["key"]["path"])
                definition = asset.get("definition") or {}
                desc = (definition.get("description") or "")[:60]
                print(f"  {path}")
                if desc:
                    print(f"    {desc}...")
            return

        if args.status:
            status = client.check_backfill_status(args.status)
            print(json.dumps(status, indent=2))
            return

        if not args.asset_path:
            # Default asset for testing
            args.asset_path = ["ireland", "education", "seed_data"]
            print(f"No asset specified, using default: {'/'.join(args.asset_path)}")

        asset_path = args.asset_path
        print(f"Materializing: {'/'.join(asset_path)}")

        backfill_id = client.materialize_asset(asset_path)
        print(f"Backfill ID: {backfill_id}")

        if args.wait:
            print(f"Waiting for completion (timeout: {args.timeout}s)...")
            status = client.wait_for_completion(backfill_id, timeout=args.timeout)
            print(f"\nFinal status:")
            print(json.dumps(status, indent=2))
        else:
            # Quick status check
            time.sleep(2)
            status = client.check_backfill_status(backfill_id)
            print(f"Status: {status.get('status', 'unknown')}")

            # Show asset-level status
            asset_statuses = status.get("assetBackfillData", {}).get("assetBackfillStatuses", [])
            for s in asset_statuses:
                if "materialized" in s:
                    path = "/".join(s["assetKey"]["path"])
                    state = (
                        "materialized"
                        if s["materialized"]
                        else "failed"
                        if s["failed"]
                        else "in_progress"
                    )
                    print(f"  {path}: {state}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
