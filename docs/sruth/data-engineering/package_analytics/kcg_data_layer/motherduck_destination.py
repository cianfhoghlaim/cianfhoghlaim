"""
spaces/data-engineering/package_analytics/kcg_data_layer/motherduck_destination.py

The KCG-canonical MotherDuck destination.

E2 of the spaces alignment plan. Replaces local DuckDB with
MotherDuck (the canonical lakehouse) via the
motherduck-data-modeling skill.

The destination is configured via the Infisical `dev-baile`
vault (MOTHERDUCK_TOKEN env var). In dev, the destination
falls back to a local DuckDB file (the KCG pattern).
"""

from __future__ import annotations

import os
from typing import Any

import dlt


def get_motherduck_destination() -> Any:
    """Return the KCG-canonical MotherDuck destination.

    Falls back to a local DuckDB file (the KCG pattern) when
    MOTHERDUCK_TOKEN is not set (dev / offline mode).
    """
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    if token:
        return dlt.destinations.motherduck(
            credentials=dlt.secrets.value(
                "motherduck.credentials",
                default={
                    "username": os.environ.get("MOTHERDUCK_USER", "cian"),
                    "password": token,
                    "database": os.environ.get("MOTHERDUCK_DATABASE", "oideachais"),
                },
            ),
        )

    # Local DuckDB fallback (the KCG pattern for dev)
    db_path = os.environ.get("DUCKDB_DATABASE", "./kcg_pypi.duckdb")
    return dlt.destinations.duckdb(credentials={"database": db_path})
