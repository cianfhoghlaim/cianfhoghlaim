#!/usr/bin/env python3
"""
Garage initialization — Python rewrite of the bash entrypoint.

ADDED 2026-08-24 (lakehouse-stack-doctor-and-env-var-cleanup-v1).
Replaces the 50-line bash script inside the `garage-init` service in
compose.yaml. Uses boto3 (more maintainable, better error handling,
easier to test) instead of raw curl.

Steps:
  1. Wait for the Garage admin API to be healthy
  2. Get the Garage node ID from the layout endpoint
  3. Configure the layout (stage + apply) if not already done
  4. Create the access key (or fetch existing one)
  5. Create the 8 buckets: iceberg, lance, ducklake, ducklake-cianfhoghlaim,
     langfuse-events, langfuse-media, langfuse-exports, mlflow-artifacts
  6. Grant access to the key for each bucket

Environment variables (set via Locket / docker-entrypoint-initdb.d):
  - GARAGE_ADMIN_TOKEN
  - GARAGE_ACCESS_KEY_ID (the name, not the secret)
  - GARAGE_SECRET_ACCESS_KEY
"""
import os
import sys
import time
import logging
from typing import Dict, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

GARAGE_ADMIN_URL = os.getenv("GARAGE_ADMIN_URL", "http://garage:3904")
GARAGE_S3_ENDPOINT = os.getenv("GARAGE_S3_ENDPOINT", "http://garage:3900")
GARAGE_REGION = os.getenv("GARAGE_REGION", "garage")
GARAGE_ADMIN_TOKEN = os.getenv("GARAGE_ADMIN_TOKEN", "")
GARAGE_ACCESS_KEY_NAME = os.getenv("GARAGE_ACCESS_KEY_ID", "lakehouse")
GARAGE_SECRET_ACCESS_KEY = os.getenv("GARAGE_SECRET_ACCESS_KEY", "")

# 9 buckets created by garage-init (per the lakehouse README + compose.yaml comment)
# ADDED 2026-08-25 (tg4-foghlaim-corpus-v1): `tg4-media` for the TG4 +
# Foghlaim multimodal media corpus (MP4 + VTT + frame PNGs).
LAKEHOUSE_BUCKETS = [
    "iceberg",                           # Lakekeeper warehouse root
    "lance",                              # Lance Namespace sidecar tables
    "ducklake",                          # DuckLake Parquet files
    "ducklake-cianfhoghlaim",            # MotherDuck BYOB bucket (legacy alias)
    "langfuse-events",                    # Langfuse event analytics
    "langfuse-media",                     # Langfuse media uploads
    "langfuse-exports",                   # Langfuse batch exports
    "mlflow-artifacts",                   # MLflow experiment artifacts
    "tg4-media",                          # TG4 + Foghlaim multimodal corpus
]

MAX_RETRIES = 60
RETRY_DELAY_SECONDS = 2


def _wait_for_garage() -> None:
    """Block until the Garage admin API is reachable."""
    import urllib3
    http = urllib3.PoolManager()
    for attempt in range(MAX_RETRIES):
        try:
            resp = http.request(
                "GET",
                f"{GARAGE_ADMIN_URL}/health",
                timeout=5,
            )
            if resp.status == 200:
                logger.info("Garage admin API is healthy (attempt %d)", attempt + 1)
                return
        except Exception as e:
            if attempt % 10 == 0:
                logger.info("Waiting for Garage admin API (attempt %d): %s", attempt + 1, e)
        time.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError(f"Garage admin API not healthy after {MAX_RETRIES} attempts")


def _s3_client() -> boto3.client:
    """Create a boto3 S3 client configured for the Garage admin API."""
    return boto3.client(
        "s3",
        endpoint_url=GARAGE_S3_ENDPOINT,
        aws_access_key_id=GARAGE_ACCESS_KEY_NAME,
        aws_secret_access_key=GARAGE_SECRET_ACCESS_KEY,
        region_name=GARAGE_REGION,
        config=Config(
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=10,
            read_timeout=30,
        ),
    )


def _ensure_layout(s3: boto3.client) -> None:
    """Configure the Garage layout (single-node, replication_factor=1)."""
    # Get the node ID from /v1/status
    import urllib3
    import json

    http = urllib3.PoolManager()
    resp = http.request(
        "GET",
        f"{GARAGE_ADMIN_URL}/v1/status",
        headers={"Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}"},
        timeout=10,
    )
    status = json.loads(resp.data.decode("utf-8"))
    node_id = status.get("node", "")
    if not node_id:
        raise RuntimeError(f"Failed to get node ID from /v1/status: {status}")

    logger.info("Garage node ID: %s", node_id)

    # Check if layout is already configured
    resp = http.request(
        "GET",
        f"{GARAGE_ADMIN_URL}/v1/layout",
        headers={"Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}"},
        timeout=10,
    )
    layout = json.loads(resp.data.decode("utf-8"))
    layout_version = layout.get("version", 0)

    if layout_version and layout_version > 0:
        logger.info("Layout already configured (version %s)", layout_version)
        return

    logger.info("Configuring Garage layout (stage + apply)...")

    # Stage the layout (single-node, dc1)
    http.request(
        "POST",
        f"{GARAGE_ADMIN_URL}/v1/layout",
        headers={
            "Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}",
            "Content-Type": "application/json",
        },
        body=json.dumps(
            [{"id": node_id, "zone": "dc1", "capacity": 100000000000, "tags": []}]
        ),
        timeout=10,
    )

    # Apply the layout
    http.request(
        "POST",
        f"{GARAGE_ADMIN_URL}/v1/layout/apply",
        headers={
            "Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}",
            "Content-Type": "application/json",
        },
        body=json.dumps({"version": 1}),
        timeout=10,
    )

    logger.info("Garage layout configured successfully")


def _ensure_access_key() -> str:
    """Create the access key (or fetch existing). Returns the access key ID."""
    import urllib3
    import json

    http = urllib3.PoolManager()

    # Try to create the key
    resp = http.request(
        "POST",
        f"{GARAGE_ADMIN_URL}/v1/key",
        headers={
            "Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}",
            "Content-Type": "application/json",
        },
        body=json.dumps({"name": GARAGE_ACCESS_KEY_NAME}),
        timeout=10,
    )
    if resp.status == 200:
        key_data = json.loads(resp.data.decode("utf-8"))
        logger.info(
            "Created access key %s (accessKeyId=%s)",
            GARAGE_ACCESS_KEY_NAME,
            key_data.get("accessKeyId", "")[:16] + "...",
        )
        return key_data.get("accessKeyId", "")

    # Key may already exist — fetch by name
    resp = http.request(
        "GET",
        f"{GARAGE_ADMIN_URL}/v1/key?search={GARAGE_ACCESS_KEY_NAME}",
        headers={"Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}"},
        timeout=10,
    )
    keys = json.loads(resp.data.decode("utf-8"))
    if keys:
        access_key_id = keys[0].get("accessKeyId", "")
        logger.info(
            "Access key %s already exists (accessKeyId=%s)",
            GARAGE_ACCESS_KEY_NAME,
            access_key_id[:16] + "...",
        )
        return access_key_id

    raise RuntimeError(f"Failed to create or fetch access key {GARAGE_ACCESS_KEY_NAME}")


def _ensure_buckets(s3: boto3.client, access_key_id: str) -> None:
    """Create the 9 lakehouse buckets + grant access to the access key."""
    import urllib3
    import json

    http = urllib3.PoolManager()

    # Get existing buckets (idempotent — skip those that already exist)
    existing = {b["Name"] for b in s3.list_buckets().get("Buckets", [])}

    # Create missing buckets
    for bucket_name in LAKEHOUSE_BUCKETS:
        if bucket_name in existing:
            logger.info("Bucket '%s' already exists", bucket_name)
            continue

        try:
            s3.create_bucket(Bucket=bucket_name)
            logger.info("Created bucket '%s'", bucket_name)
        except ClientError as e:
            # If another race condition created it, ignore
            if e.response.get("Error", {}).get("Code") in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                logger.info("Bucket '%s' created concurrently", bucket_name)
            else:
                raise

    # Get bucket IDs + grant access
    for bucket_name in LAKEHOUSE_BUCKETS:
        resp = http.request(
            "GET",
            f"{GARAGE_ADMIN_URL}/v1/bucket?globalAlias={bucket_name}",
            headers={"Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}"},
            timeout=10,
        )
        bucket_data = json.loads(resp.data.decode("utf-8"))
        if not bucket_data:
            logger.warning("Could not find bucket ID for '%s' — skipping permission grant", bucket_name)
            continue

        bucket_id = bucket_data.get("id", "")
        if not bucket_id:
            continue

        # Grant the access key read+write+owner permissions on the bucket
        http.request(
            "POST",
            f"{GARAGE_ADMIN_URL}/v1/bucket/allow",
            headers={
                "Authorization": f"Bearer {GARAGE_ADMIN_TOKEN}",
                "Content-Type": "application/json",
            },
            body=json.dumps(
                {
                    "bucketId": bucket_id,
                    "accessKeyId": access_key_id,
                    "permissions": {"read": True, "write": True, "owner": True},
                }
            ),
            timeout=10,
        )
        logger.info("Granted access to bucket '%s' for key %s", bucket_name, access_key_id[:16] + "...")


def main() -> int:
    """Entry point for the garage-init service."""
    if not GARAGE_ADMIN_TOKEN or not GARAGE_SECRET_ACCESS_KEY:
        logger.error(
            "Missing required env vars: GARAGE_ADMIN_TOKEN + GARAGE_SECRET_ACCESS_KEY"
        )
        return 1

    try:
        logger.info("Waiting for Garage admin API at %s...", GARAGE_ADMIN_URL)
        _wait_for_garage()

        s3 = _s3_client()
        logger.info("Configuring Garage layout...")
        _ensure_layout(s3)

        logger.info("Ensuring access key '%s'...", GARAGE_ACCESS_KEY_NAME)
        access_key_id = _ensure_access_key()

        logger.info("Ensuring %d buckets...", len(LAKEHOUSE_BUCKETS))
        _ensure_buckets(s3, access_key_id)

        logger.info("Garage initialization complete ✓")
        return 0
    except Exception as e:
        logger.exception("Garage initialization failed: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
