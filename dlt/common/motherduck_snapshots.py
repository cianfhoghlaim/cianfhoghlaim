"""MotherDuck snapshots + shares + compute size helpers.

Per the 2026-08-07-biep-v3-hardening-v1 change.
"""
from __future__ import annotations

import os
from typing import Any, Literal

ComputeSize = Literal["small", "medium", "large"]


def snapshot_database(
    name: str,
    parent_database: str,
    at_timestamp: str | None = None,
) -> dict[str, str]:
    """Create a MotherDuck snapshot of an existing database.

    Returns the snapshot metadata dict (passed to MotherDuck's API).
    """
    return {
        "name": name,
        "parent_database": parent_database,
        "at_timestamp": at_timestamp,
        "kind": "snapshot",
    }


def create_share(
    name: str,
    database: str,
    read_only: bool = True,
) -> dict[str, str]:
    """Create a MotherDuck Share for zero-copy read access.

    Returns the share metadata dict (passed to MotherDuck's API).
    """
    return {
        "name": name,
        "database": database,
        "read_only": read_only,
        "kind": "share",
    }


def attach_share(
    share_url: str,
    as_: str,
    read_only: bool = True,
) -> dict[str, str]:
    """Attach an existing MotherDuck Share by URL."""
    return {
        "share_url": share_url,
        "as": as_,
        "read_only": read_only,
        "kind": "share_attach",
    }


def compute_size_env() -> ComputeSize:
    """Read the canonical MOTHERDUCK_INSTANCE_SIZE env var (default: 'small')."""
    size = os.environ.get("MOTHERDUCK_INSTANCE_SIZE", "small").lower()
    if size not in ("small", "medium", "large"):
        size = "small"
    return size  # type: ignore[return-value]


__all__ = [
    "snapshot_database",
    "create_share",
    "attach_share",
    "compute_size_env",
    "ComputeSize",
]
