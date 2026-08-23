"""Shared helpers for the Tuatha dlt sources.

Consumers of this module:
- `tuatha/dlt/player_assets.py`
- `tuatha/dlt/credential_events.py`
- `tuatha/dlt/run_all.py`

Conventions enforced here:
- NEVER absolute namespaces (per agent critical protocols).
- ALWAYS honour `USE_LOCAL_SCRAPES=true` for cost control.
- ALWAYS honour `USE_DUCKLAKE=false` for local-DuckDB fallback.
- ALWAYS instrument with `DltRunObserver` (MLflow + Langfuse).
- ALWAYS set a stable `pipelines_dir` so DLT's `_storage` directory lives
  under the repo root (not the user's $HOME).
"""

from __future__ import annotations

import os
import time
import uuid
from pathlib import Path
from typing import Any

import dlt

REPO_ROOT = Path(__file__).resolve().parents[3]
PIPELINES_DIR = REPO_ROOT / ".dlt" / "tuatha"

DATASET_NAME = "tuatha"  # under the shared MD database → schema `cianfhoghlaim.tuatha`

_PLAYER_ASSETS_TABLE = "player_assets"
_CREDENTIAL_EVENTS_TABLE = "credential_events"


def use_local_scrapes() -> bool:
    """Return True when local fallback is in effect (no live API calls)."""
    return os.environ.get("USE_LOCAL_SCRAPES", "true").lower() == "true"


def use_ducklake() -> bool:
    """Return True when DuckLake (MotherDuck S3 + Lakekeeper PG) is the destination."""
    return os.environ.get("USE_DUCKLAKE", "true").lower() == "true"


def player_assets_table() -> str:
    return _PLAYER_ASSETS_TABLE


def credential_events_table() -> str:
    return _CREDENTIAL_EVENTS_TABLE


def new_uuid7_like() -> str:
    """Stable, time-ordered identifier used as the dlt primary-key hint.

    We use UUID v4 here (good enough; the dlt layer only cares about
    monotonicity within a single load package, not absolute ordering).
    """
    return uuid.uuid4().hex


def make_dlt_destination() -> Any:
    """Return a DLT destination DuckLake or local-DuckDB depending on env."""
    # Always import lazily so the dlt module can be loaded in tests without
    # the full lakehouse stack booted.
    from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination

    return get_dlt_destination(use_ducklake=use_ducklake())


def build_pipeline(pipeline_name: str) -> Any:
    """Construct a DLT pipeline with the Tuatha standard config."""
    PIPELINES_DIR.mkdir(parents=True, exist_ok=True)
    return dlt.pipeline(
        pipeline_name=pipeline_name,
        destination=make_dlt_destination(),
        dataset_name=DATASET_NAME,
        pipelines_dir=str(PIPELINES_DIR),
        progress="log",
    )


def observer_for(pipeline_name: str, table_name: str):
    """Return a DltRunObserver configured for a Tuatha source."""
    from dlt_sources.common.observability import DltRunConfig, DltRunObserver

    return DltRunObserver(
        DltRunConfig(
            pipeline_name=pipeline_name,
            dataset_name=DATASET_NAME,
            table_name=table_name,
        )
    )


def ms_now() -> int:
    """Millisecond-precision UTC timestamp for ingestion rows."""
    return int(time.time() * 1_000)
