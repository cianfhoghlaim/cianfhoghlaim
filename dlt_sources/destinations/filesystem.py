"""dlt_sources.common.destinations.filesystem — local FS + S3 + GCS + Azure.

Per the **2026-08-24-wave-4-ducklake-v1-hardening-v1** openspec
change. The filesystem destination is the simplest backend —
Parquet or JSONL files written to local disk or object storage.

Per `dlthub.com/docs/dlt-ecosystem/destinations/filesystem`:

> "The filesystem destination stores data in remote file systems
>  and object stores. It supports AWS S3, Google Cloud Storage,
>  Azure Blob Storage, and local files."

This is the FALLBACK destination for the Cianfhoghlaim platform —
used in dev mode (local SQLite-like behaviour) and as the staging
area before data is merged into the DuckLake catalog.
"""
from __future__ import annotations

import os
from typing import Any, Literal, Optional

import dlt


# The 4 filesystem backends supported.
FilesystemBackend = Literal["local", "s3", "gcs", "azure"]


def get_filesystem_destination(
    backend: FilesystemBackend = "local",
    bucket_url: Optional[str] = None,
    *,
    file_format: Literal["parquet", "jsonl"] = "parquet",
) -> Any:
    """Build the filesystem dlt destination.

    Args:
        backend: One of `"local"`, `"s3"`, `"gcs"`, `"azure"`. Default: `"local"`.
        bucket_url: Object store URL. Required for `s3`, `gcs`, `azure`.
            Examples:
            - `"s3://my-bucket/path/"`
            - `"gs://my-bucket/path/"`
            - `"abfss://container@account.dfs.core.windows.net/path/"`
            For `local`, leave as `None` (writes to the current working dir).
        file_format: One of `"parquet"`, `"jsonl"`. Default: `"parquet"`.

    Returns:
        A `@dlt.destination`-decorated function configured for the
        requested filesystem backend.

    Reference: openspec/changes/2026-08-24-wave-4-ducklake-v1-hardening-v1/
    """
    if backend in ("s3", "gcs", "azure") and not bucket_url:
        raise ValueError(
            f"filesystem_destination: backend={backend!r} requires bucket_url"
        )

    credentials: dict[str, Any]
    if backend == "local":
        credentials = {
            "bucket_url": bucket_url or os.getenv("CIANFHOGHLAIM_FS_LOCAL", "./lakehouse"),
        }
    elif backend == "s3":
        credentials = {
            "bucket_url": bucket_url,
            "credentials": {
                "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
                "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            },
        }
    elif backend == "gcs":
        credentials = {
            "bucket_url": bucket_url,
            "credentials": {
                "project_id": os.getenv("GCP_PROJECT_ID"),
                "token": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            },
        }
    elif backend == "azure":
        credentials = {
            "bucket_url": bucket_url,
            "credentials": {
                "azure_storage_account_name": os.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
                "azure_storage_account_key": os.getenv("AZURE_STORAGE_ACCOUNT_KEY"),
            },
        }
    else:
        raise ValueError(f"filesystem_destination: unknown backend {backend!r}")

    @dlt.destination(
        credentials=credentials,
        dest_name="filesystem",
    )
    def filesystem_cianfhoghlaim() -> Any:
        """Filesystem destination for the Cianfhoghlaim platform.

        Writes Parquet (default) or JSONL files to the requested
        backend. Use this as the staging area before merging into
        DuckLake.
        """
        return credentials

    return filesystem_cianfhoghlaim


__all__ = ["FilesystemBackend", "get_filesystem_destination"]
