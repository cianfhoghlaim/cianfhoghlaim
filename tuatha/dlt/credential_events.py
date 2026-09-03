"""DLT source: auth + quest-completion credential events.

One row per in-game credential event (login, badge unlock, quest completion,
payment, customisation). The `event_type` column captures the type;
the `langfuse_trace_id` + `mlflow_run_id` columns are populated when the
event also triggers a tutor-NPC call that gets traced (RAGAS-evaluated
power-user of Langfuse + MLflow).

Run with:
    python3 -m tuatha.dlt.credential_events

The `payload_json` column holds the JSON-encoded event-specific body
(spawn coords for asset-spawn events, quest hash for quest-completion, etc.).
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path
from typing import Any, Iterator

import dlt

from ._shared import (
    REPO_ROOT,
    build_pipeline,
    credential_events_table,
    ms_now,
    new_uuid7_like,
    observer_for,
    use_local_scrapes,
)

PIPELINE_NAME = "tuatha.credential_events"
TABLE = credential_events_table()

_EVENT_TYPES = (
    "login",
    "logout",
    "badge_unlock",
    "quest_complete",
    "asset_spawn",
    "payment",
    "language_switch",
)

_LANGUAGE_PAIRS = ("ga-en", "en-ga")
_LC_TOPICS = (
    "lc_biology.ecosystems",
    "lc_chemistry.combustion",
    "lc_geography.geomorphology",
    "lc_english.poetry",
    "lc_history.early_medieval_ireland",
    "lc_physics.stellar_evolution",
    "lc_irish.grammar.gender",
)

FIXTURE_DIR = REPO_ROOT / "stedding" / "dev" / "sruth" / "tuath" / "fixtures"


def _rows_from_local_fixtures() -> Iterator[dict[str, Any]]:
    """Yield events from bundled fixtures (offline path)."""
    fixture_file = FIXTURE_DIR / "credential_events.jsonl"
    if fixture_file.exists():
        with fixture_file.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line:
                    yield json.loads(line)
        return

    # Synthesise 100 deterministic events from the corpus
    rng = random.Random(43)
    for i in range(100):
        kind = _EVENT_TYPES[i % len(_EVENT_TYPES)]
        yield {
            "event_id": new_uuid7_like(),
            "player_id": f"player_{i % 25:04d}",  # 25 distinct players cycling
            "event_type": kind,
            "mc_lc_topic": rng.choice(_LC_TOPICS) if rng.random() > 0.2 else None,
            "occurred_at": ms_now() - rng.randint(0, 86_400_000),  # last 24h
            "langfuse_trace_id": f"trace-{new_uuid7_like()[:12]}" if kind == "badge_unlock" else None,
            "mlflow_run_id": f"run-{new_uuid7_like()[:12]}" if kind == "badge_unlock" else None,
            "payload_json": json.dumps({"i": i, "kind": kind}, sort_keys=True),
        }


def _rows_from_event_stream() -> Iterator[dict[str, Any]]:
    """Tail the SpacetimeDB credential_events subscription."""
    from spacetimedb_sdk import connect  # type: ignore  # noqa: F401

    import os

    url = os.environ.get("SPACETIMEDB_URL", "ws://localhost:3000")
    conn = connect(url)
    table = conn.db.credential_events  # type: ignore[attr-defined]
    for row in table.iter():
        yield {
            "event_id": row.event_id,
            "player_id": row.player_id,
            "event_type": row.event_type,
            "mc_lc_topic": row.mc_lc_topic,
            "occurred_at": int(row.occurred_at),
            "langfuse_trace_id": row.langfuse_trace_id,
            "mlflow_run_id": row.mlflow_run_id,
            "payload_json": row.payload_json,
        }


@dlt.resource(
    name=TABLE,
    write_disposition="merge",
    primary_key="event_id",
)
def credential_events_source(
    use_local: bool | None = None,
    player_ids: list[str] | None = None,
) -> Iterator[dict[str, Any]]:
    """DLT resource: per-event credential ledger."""
    if use_local is None:
        use_local = use_local_scrapes()

    if use_local:
        rows = _rows_from_local_fixtures()
    else:
        rows = _rows_from_event_stream()

    if player_ids:
        rows = (r for r in rows if r["player_id"] in set(player_ids))

    for r in rows:
        yield r


@dlt.source
def credential_events() -> Any:
    """DLT source grouping the credential_events resource."""
    return credential_events_source()


def run() -> int:
    """CLI entrypoint: load credential_events via DLT, return row count."""
    pipeline = build_pipeline(PIPELINE_NAME)
    with observer_for(PIPELINE_NAME, TABLE) as observer:
        load_info = pipeline.run(credential_events_source())
        receipt = observer.record(row_count=0, load_info=load_info)
        try:
            counts = dict(load_info.metrics or {})
            receipt = observer.record(
                row_count=int(counts.get("loaded_items_count", 0)),
                load_info=load_info,
            )
        except Exception:  # pragma: no cover
            pass

    print(json.dumps({"status": "ok", "table": TABLE, "receipt": receipt.__dict__}, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
