"""MotherDuck snapshots + shares + compute size helpers.

Per the 2026-08-10-biep-v3-preflight-bug-fixes-v1 change.

The 3 API-calling functions (`snapshot_database`, `create_share`,
`attach_share`) make real HTTPS POSTs to `api.motherduck.com` via
`httpx`, with `tenacity` retry + exponential backoff. The 4th
function (`compute_size_env`) is a pure env-var reader and needs
no HTTP.

All API calls require `MOTHERDUCK_TOKEN` in the env for auth.
The base URL is `MOTHERDUCK_API_URL` (default `https://api.motherduck.com`).
"""
from __future__ import annotations

import os
from typing import Any, Literal

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

ComputeSize = Literal["small", "medium", "large"]

MOTHERDUCK_API_URL: str = os.getenv("MOTHERDUCK_API_URL", "https://api.motherduck.com")
_DEFAULT_TIMEOUT_S: float = 30.0


def _auth_headers() -> dict[str, str]:
    """Build the Authorization header from the env."""
    token = os.environ.get("MOTHERDUCK_TOKEN")
    if not token:
        raise RuntimeError(
            "MOTHERDUCK_TOKEN env var is required for MotherDuck API calls. "
            "Set it via `mise run secrets:env` or directly in .env."
        )
    return {"Authorization": f"Bearer {token}"}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def snapshot_database(
    name: str,
    parent_database: str,
    at_timestamp: str | None = None,
) -> dict[str, Any]:
    """Create a MotherDuck snapshot of `parent_database`.

    Returns the API response as a dict (typically `{"snapshot_id": "...",
    "created_at": "...", "at_timestamp": "..."}`).

    Args:
        name: The name of the new snapshot.
        parent_database: The MotherDuck database to snapshot.
        at_timestamp: Optional ISO 8601 timestamp for point-in-time
            snapshots (e.g., "2026-08-10T00:00:00Z").
    """
    payload: dict[str, Any] = {"name": name}
    if at_timestamp is not None:
        payload["at_timestamp"] = at_timestamp

    resp = httpx.post(
        f"{MOTHERDUCK_API_URL}/v1/databases/{parent_database}/snapshots",
        json=payload,
        headers=_auth_headers(),
        timeout=_DEFAULT_TIMEOUT_S,
    )
    resp.raise_for_status()
    return dict(resp.json())


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def create_share(
    name: str,
    database: str,
    read_only: bool = True,
) -> dict[str, Any]:
    """Create a MotherDuck Share for zero-copy read access.

    Returns the API response (typically `{"share_url": "https://...",
    "name": "...", "database": "...", "read_only": true}`).

    Args:
        name: The share name.
        database: The MotherDuck database to share.
        read_only: Whether the share is read-only (default True).
    """
    payload: dict[str, Any] = {
        "name": name,
        "database": database,
        "read_only": read_only,
    }
    resp = httpx.post(
        f"{MOTHERDUCK_API_URL}/v1/shares",
        json=payload,
        headers=_auth_headers(),
        timeout=_DEFAULT_TIMEOUT_S,
    )
    resp.raise_for_status()
    return dict(resp.json())


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def attach_share(
    share_url: str,
    as_: str,
    read_only: bool = True,
) -> dict[str, Any]:
    """Attach an existing MotherDuck Share by URL.

    Returns the API response (typically `{"attached": true, "as": "...",
    "share_url": "..."}`).

    Args:
        share_url: The share URL returned by `create_share()`.
        as_: The local alias to attach the share under.
        read_only: Whether the attached share is read-only (default True).
    """
    payload: dict[str, Any] = {
        "share_url": share_url,
        "as": as_,
        "read_only": read_only,
    }
    resp = httpx.post(
        f"{MOTHERDUCK_API_URL}/v1/shares/attach",
        json=payload,
        headers=_auth_headers(),
        timeout=_DEFAULT_TIMEOUT_S,
    )
    resp.raise_for_status()
    return dict(resp.json())


def compute_size_env() -> ComputeSize:
    """Read the canonical MOTHERDUCK_INSTANCE_SIZE env var (default: 'small').

    Pure env-var reader; no HTTP call needed.
    """
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
    "MOTHERDUCK_API_URL",
]