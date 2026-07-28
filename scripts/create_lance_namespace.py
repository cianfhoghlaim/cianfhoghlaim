"""Create the `cianhoghlaim` Lance namespace in the Lakekeeper catalog.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This script is invoked by `mise run biep:v3:m0` (step 5 of the M0
foundation unblock). It POSTs to the Lakekeeper REST endpoint
`/v1/namespaces/` to create the `cianhoghlaim` namespace (idempotent —
the endpoint returns 409 if the namespace already exists, which we
silently accept).
"""

from __future__ import annotations

import logging
import os
import sys

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("create_lance_namespace")


NAMESPACE_NAME = "cianhoghlaim"


def main() -> int:
    """Create the `cianhoghlaim` Lance namespace in Lakekeeper (idempotent)."""
    catalog_uri = os.environ.get("LAKEKEEPER_URI", "http://localhost:8181")
    logger.info(f"Creating Lance namespace {NAMESPACE_NAME!r} at {catalog_uri}")

    # Try the Iceberg REST namespace endpoint
    endpoints = [
        f"{catalog_uri}/v1/namespaces/",
        f"{catalog_uri}/v1/namespaces",
    ]
    for endpoint in endpoints:
        try:
            response = httpx.post(
                endpoint,
                json={"namespace": [NAMESPACE_NAME], "properties": {}},
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
            if response.status_code in (200, 201, 204):
                logger.info(f"Created Lance namespace {NAMESPACE_NAME!r} via {endpoint}")
                return 0
            if response.status_code == 409:
                logger.info(f"Lance namespace {NAMESPACE_NAME!r} already exists (409).")
                return 0
            logger.warning(f"Endpoint {endpoint} returned {response.status_code}: {response.text[:200]}")
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Endpoint {endpoint} failed: {exc}")

    logger.error(f"Failed to create Lance namespace {NAMESPACE_NAME!r}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
