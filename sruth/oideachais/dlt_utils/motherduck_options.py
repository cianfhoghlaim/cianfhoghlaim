"""
MotherDuck hosting-option helpers.

The 2026-04-13 launch of DuckLake 1.0 on MotherDuck introduced 3
production hosting options per
`motherduck.com/blog/announcing-ducklake-1-0-on-motherduck`:

| Option  | Catalog      | Storage    | Compute     | Use When                           |
|---------|--------------|------------|-------------|------------------------------------|
| managed | MotherDuck   | MotherDuck | MotherDuck  | "I want a simple serverless option"|
| byob    | MotherDuck   | Self-hosted| MotherDuck  | "I want to own my own data"        |
| byoc    | MotherDuck   | Self-hosted| Self-hosted | "I want to use multiple engines"   |

The KCG default is **byob** (the "sweet spot" per the launch
post) — MotherDuck handles the catalog and compute (low ops),
but the data lives in our own Garage S3 bucket (data sovereignty).

Environment variables (read by `get_dlt_destination`):

- ``MOTHERDUCK_MODE`` — one of ``"managed"``, ``"byob"``, ``"byoc"``.
  Default ``"byob"``.
- ``MOTHERDUCK_TOKEN`` — the MotherDuck personal access token.
  Set via the Infisical `dev-baile` vault.
- ``MOTHERDUCK_DATABASE`` — the database name. Default ``"oideachais"``.
- ``MOTHERDUCK_S3_BUCKET`` — the S3 bucket for the BYOB option.
  Default ``"ducklake"``.
- ``MOTHERDUCK_S3_ENDPOINT`` — the S3 endpoint. Default
  ``"http://localhost:3900"`` (the local Garage stack).
"""
from __future__ import annotations

import os
from typing import Any, Literal

import dlt
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials

MotherDuckMode = Literal["managed", "byob", "byoc"]


def _resolve_mode() -> MotherDuckMode:
    """Read the ``MOTHERDUCK_MODE`` env var, defaulting to ``"byob"``."""
    raw = os.environ.get("MOTHERDUCK_MODE", "byob").lower()
    if raw not in {"managed", "byob", "byoc"}:
        # Default to byob on unknown values (the canonical default).
        return "byob"
    return raw  # type: ignore[return-value]


def fully_managed_destination() -> Any:
    """Return a MotherDuck managed destination.

    MotherDuck catalog + MotherDuck storage + MotherDuck compute.
    The simplest option; recommended for local development against
    the MotherDuck cloud.
    """
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    database = os.environ.get("MOTHERDUCK_DATABASE", "oideachais")
    credentials = DuckLakeCredentials(
        ducklake_name=database,
        catalog=f"motherduck:?motherduck_token={token}",
    )
    return dlt.destinations.ducklake(credentials=credentials)


def byob_destination() -> Any:
    """Return a MotherDuck BYOB destination.

    MotherDuck catalog + self-hosted S3 (Garage) + MotherDuck compute.
    The "sweet spot" for production deployments.
    """
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    database = os.environ.get("MOTHERDUCK_DATABASE", "oideachais")
    bucket = os.environ.get("MOTHERDUCK_S3_BUCKET", "ducklake")
    endpoint = os.environ.get("MOTHERDUCK_S3_ENDPOINT", "http://localhost:3900")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

    storage_config = {
        "bucket_url": f"s3://{bucket}/{database}/",
        "credentials": {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "endpoint_url": endpoint,
            "region_name": os.environ.get("AWS_REGION", "garage"),
        },
        "config_kwargs": {"s3": {"addressing_style": "path"}},
    }
    credentials = DuckLakeCredentials(
        ducklake_name=database,
        catalog=f"motherduck:?motherduck_token={token}",
        storage=storage_config,
    )
    return dlt.destinations.ducklake(credentials=credentials)


def byoc_destination() -> Any:
    """Return a MotherDuck BYOC destination.

    MotherDuck catalog + self-hosted S3 (Garage) + self-hosted
    compute (Trino, Spark, or DataFusion).

    The same storage as BYOB but the compute runs on-prem (the
    bunchloch MacBook or the cax41-hetzner server). The
    `motherduck.cianfhoghlaim.ie` endpoint is only used for
    metadata (catalog).
    """
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    database = os.environ.get("MOTHERDUCK_DATABASE", "oideachais")
    bucket = os.environ.get("MOTHERDUCK_S3_BUCKET", "ducklake")
    endpoint = os.environ.get("MOTHERDUCK_S3_ENDPOINT", "http://localhost:3900")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "")

    storage_config = {
        "bucket_url": f"s3://{bucket}/{database}/",
        "credentials": {
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
            "endpoint_url": endpoint,
            "region_name": os.environ.get("AWS_REGION", "garage"),
        },
        "config_kwargs": {"s3": {"addressing_style": "path"}},
    }
    credentials = DuckLakeCredentials(
        ducklake_name=database,
        # The catalog uses the MotherDuck endpoint for metadata only;
        # the actual queries hit the local DuckDB instance.
        catalog=f"motherduck:?motherduck_token={token}",
        storage=storage_config,
    )
    return dlt.destinations.ducklake(credentials=credentials)


def get_motherduck_destination() -> Any:
    """Return the MotherDuck destination for the configured hosting mode.

    Routes on the ``MOTHERDUCK_MODE`` env var:

    - ``"managed"`` → ``fully_managed_destination()``
    - ``"byob"`` (default) → ``byob_destination()``
    - ``"byoc"`` → ``byoc_destination()``
    """
    mode = _resolve_mode()
    if mode == "managed":
        return fully_managed_destination()
    if mode == "byoc":
        return byoc_destination()
    return byob_destination()


__all__ = [
    "MotherDuckMode",
    "fully_managed_destination",
    "byob_destination",
    "byoc_destination",
    "get_motherduck_destination",
]
