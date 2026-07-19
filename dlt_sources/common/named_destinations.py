"""
Named dlt destinations — the canonical KCG pattern.

The named destination registry decouples DLT sources from the
physical destination backend. A source declares its destination
by name (e.g. `warehouse`, `lakehouse`, `local_duckdb`); the
factory resolves the name to a concrete `@dlt.destination`
function at runtime.

Per the british-isles-education-pipeline (BIEP) v1 spec, the
6 BIEP v1 LC subjects (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) write their per-subject
NCCA syllabus resources to the `warehouse` named destination
on the remote runtime, with a local DuckDB fallback for dev.

Usage:

    from cianfhoghlaim.dlt.common.named_destinations import (
        named_destination,
        DESTINATIONS,
    )

    @dlt.resource(
        name="mathematics_syllabus",
        write_disposition="merge",
        primary_key=["url"],
        destination=named_destination("warehouse"),
    )
    def mathematics_syllabus(): ...

Reference: openspec/changes/2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1/
"""
from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

import dlt

# ============================================================================
# Named destination registry
# ============================================================================
#
# A named destination is a tuple of (callable, env_marker):
# - `callable` returns a configured `@dlt.destination(...)` factory
# - `env_marker` is the env var that activates the named destination
#   (when unset, the named destination falls back to local DuckDB)

DESTINATIONS: dict[str, dict[str, Any]] = {
    # The canonical BIEP v1 NCCA destination — the remote "warehouse"
    # is the MotherDuck `oideachais` database (md:oideachais); when
    # `USE_LOCAL_SCRAPES=true` or `MOTHERDUCK_TOKEN` is unset we
    # transparently fall back to a local DuckDB at
    # `cianfhoghlaim.warehouse.duckdb`.
    "warehouse": {
        "callable": "_warehouse_destination",
        "env_marker": "MOTHERDUCK_TOKEN",
        "default_backend": "duckdb",
    },
    # The Lakehouse (DuckLake on Garage S3 + Postgres catalog) —
    # the production write target for any source that needs
    # transactional ACID across object storage.
    "lakehouse": {
        "callable": "_lakehouse_destination",
        "env_marker": "DUCKLAKE_CATALOG_URL",
        "default_backend": "duckdb",
    },
    # Local-only DuckDB (used by all unit tests + dev runs).
    "local_duckdb": {
        "callable": "_local_duckdb_destination",
        "env_marker": None,
        "default_backend": "duckdb",
    },
}


def _warehouse_destination() -> Any:
    """Return the configured warehouse destination.

    Honours `USE_LOCAL_SCRAPES=true` and the absence of
    `MOTHERDUCK_TOKEN` by falling back to a local DuckDB.
    """
    use_local = os.getenv("USE_LOCAL_SCRAPES", "false").lower() in {"1", "true", "yes"}
    motherduck_token = os.getenv("MOTHERDUCK_TOKEN")
    if use_local or not motherduck_token:
        return dlt.destinations.duckdb(
            credentials=":local:",
            dataset_name="cianfhoghlaim.leaving_cert",
        )
    return dlt.destinations.motherduck(
        credentials=f"md:oideachais?motherduck_token={motherduck_token}",
        dataset_name="leaving_cert",
    )


def _lakehouse_destination() -> Any:
    """Return the DuckLake destination (production write target)."""
    catalog_url = os.getenv("DUCKLAKE_CATALOG_URL")
    if not catalog_url:
        return dlt.destinations.duckdb(
            credentials=":local:",
            dataset_name="cianfhoghlaim.lakehouse",
        )
    return dlt.destinations.ducklake(
        credentials=catalog_url,
        dataset_name="cianfhoghlaim",
    )


def _local_duckdb_destination() -> Any:
    """Return a local-only DuckDB (always local)."""
    return dlt.destinations.duckdb(
        credentials=":local:",
        dataset_name="cianfhoghlaim.dev",
    )


_CALLABLES: dict[str, Callable[[], Any]] = {
    "_warehouse_destination": _warehouse_destination,
    "_lakehouse_destination": _lakehouse_destination,
    "_local_duckdb_destination": _local_duckdb_destination,
}


def named_destination(name: str) -> Any:
    """Resolve a named destination to a concrete dlt destination.

    Args:
        name: The destination name (one of `DESTINATIONS`).

    Returns:
        A configured `@dlt.destination` factory.

    Raises:
        ValueError: If `name` is not registered.
    """
    if name not in DESTINATIONS:
        raise ValueError(
            f"unknown destination {name!r}; "
            f"valid: {sorted(DESTINATIONS.keys())}"
        )
    spec = DESTINATIONS[name]
    factory = _CALLABLES[spec["callable"]]
    return factory()


__all__ = [
    "DESTINATIONS",
    "named_destination",
]
