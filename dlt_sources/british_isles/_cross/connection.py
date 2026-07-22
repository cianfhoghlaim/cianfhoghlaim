"""Common connection helpers for the BIEP v3 registry.

Per the 2026-08-13 BIEP v3 lakehouse full activation plan (Phase 2):

When connecting to a DuckLake URI (`ducklake:postgres:...`), the
underlying DuckDB instance must have its S3 secret configured BEFORE
any queries that touch S3 storage (otherwise DuckLake tries to use
the default `s3.amazonaws.com` endpoint and fails).

This module provides a `connect_ducklake()` helper that handles this
uniformly across the registry_loader + registry_api paths.
"""
from __future__ import annotations

import os
from typing import Any


def _setup_s3_secret(conn: Any) -> None:
    """Configure the S3 secret on a DuckDB connection for Garage/MinIO.

    Reads (idempotent — only creates the secret if not already set).
    No-op if `AWS_ENDPOINT_URL` is unset (the MotherDuck path uses
    DuckDB's built-in AWS endpoints).
    """
    import duckdb  # type: ignore[import-not-found]

    endpoint = os.getenv("AWS_ENDPOINT_URL")
    if not endpoint:
        return
    key_id = os.getenv("AWS_ACCESS_KEY_ID")
    secret = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION", "garage")
    if not key_id or not secret:
        return
    # DuckLake's CREATE SECRET requires ENDPOINT WITHOUT `http://` prefix
    endpoint_no_scheme = endpoint.replace("http://", "").replace("https://", "")
    try:
        conn.execute(
            f"""
            CREATE OR REPLACE SECRET gs3 (
                TYPE S3, PROVIDER config,
                KEY_ID '{key_id}',
                SECRET '{secret}',
                REGION '{region}',
                ENDPOINT '{endpoint_no_scheme}',
                USE_SSL false, URL_STYLE 'path'
            )
            """
        )
    except duckdb.Error:
        # httpfs extension not installed — skip
        pass


def connect_ducklake(
    uri: str,
    *,
    read_only: bool = False,
    use_catalog: str | None = None,
) -> Any:
    """Open a DuckDB connection to a DuckLake URI + configure S3 secret.

    Args:
        uri: The DuckLake URI (e.g., `ducklake:postgres:dbname=...`)
        read_only: Whether to open in read-only mode (default False).
        use_catalog: If set, runs `USE <catalog>;` after attach (this
            is required for `education.subjects` (no catalog prefix) to
            resolve to `lakehouse.education.subjects`).

    Returns:
        A duckdb connection with the S3 secret configured.
    """
    import duckdb  # type: ignore[import-not-found]

    conn = duckdb.connect(uri, read_only=read_only)
    if uri.startswith("ducklake:"):
        _setup_s3_secret(conn)
    if use_catalog:
        try:
            conn.execute(f"USE {use_catalog};")
        except duckdb.Error:
            pass
    return conn


__all__ = ["connect_ducklake", "_setup_s3_secret"]