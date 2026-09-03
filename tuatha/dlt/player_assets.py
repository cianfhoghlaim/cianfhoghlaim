"""DLT source: per-player procedural asset ledger.

One row per spawned asset (tree, rune, badge, ring fort, Ogham-named avatar).
The `celtic_token_ga` + `celtic_token_en` columns capture the dual-language
Celtic vocabulary card that the BIEP Leaving Certificate Gaeilge syllabus
links to. The `curriculum_hook` column names the BIEP concept the asset
reinforces (e.g. ``"lc_chemistry.electron_configuration"``).

Run with:
    python3 -m tuatha.dlt.player_assets

Read path honours ``USE_LOCAL_SCRAPES=true`` (default) — yields rows from
the bundled ``stedding/dev/sruth/tuath/fixtures/`` corpus; set to ``false``
to read live from the SpacetimeDB ``player_assets`` table.

Write path:
- ``USE_DUCKLAKE=true`` (default) → MotherDuck + DuckLake under
  ``cianfhoghlaim.tuatha.player_assets``
- ``USE_DUCKLAKE=false`` → local DuckDB at ``./tuatha.duckdb`` for dev

Observability:
- MLflow run logged under experiment ``tuatha`` → track ``dlt.rows_loaded``
- Langfuse trace emitted with attribute ``dlt.pipeline=tuatha.player_assets``
"""

from __future__ import annotations

import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Iterator

import dlt

from ._shared import (
    PIPELINES_DIR,
    REPO_ROOT,
    build_pipeline,
    ms_now,
    new_uuid7_like,
    observer_for,
    player_assets_table,
    use_local_scrapes,
)

PIPELINE_NAME = "tuatha.player_assets"
TABLE = player_assets_table()

# Celtic vocabulary corpus bundled in `stedding/dev/sruth/tuath/fixtures/`
# Each tuple = (gaelic, english, BIEP concept id)
_CELTIC_VOCAB: list[tuple[str, str, str]] = [
    ("crann", "tree", "lc_biology.ecosystems"),
    ("rún", "secret / rune", "lc_english.poetry"),
    ("dún", "fort", "lc_history.early_medieval_ireland"),
    ("bád", "boat", "lc_geography.coastal_morphology"),
    ("teine", "fire", "lc_chemistry.combustion"),
    ("sliabh", "mountain", "lc_geography.geomorphology"),
    ("abhainn", "river", "lc_geography.fluvial_processes"),
    ("grian", "sun", "lc_physics.electromagnetic_radiation"),
    ("gealach", "moon", "lc_physics.orbital_mechanics"),
    ("réalta", "star", "lc_physics.stellar_evolution"),
    ("talamh", "earth / soil", "lc_biology.pedogenesis"),
    ("gaoth", "wind", "lc_geography.atmospheric_circulation"),
    ("fear", "man", "lc_irish.grammar.gender"),
    ("bean", "woman", "lc_irish.grammar.gender"),
    ("capall", "horse", "lc_irish.vocabulary.animals"),
    ("madra", "dog", "lc_irish.vocabulary.animals"),
    ("cat", "cat", "lc_irish.vocabulary.animals"),
    ("iolair", "eagle", "lc_biology.predator_prey"),
    ("breac", "trout", "lc_biology.aquatic_systems"),
    ("iolar", "eagle", "lc_biology.predator_prey"),
]

_ASSET_KINDS = ("tree", "rune", "badge", "ring_fort", "ogham_stone", "sacred_well")
FIXTURE_DIR = REPO_ROOT / "stedding" / "dev" / "sruth" / "tuath" / "fixtures"


def _rows_from_local_fixtures() -> Iterator[dict[str, Any]]:
    """Yield rows from bundled fixtures (offline path)."""
    fixture_file = FIXTURE_DIR / "player_assets.jsonl"
    if fixture_file.exists():
        with fixture_file.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line:
                    yield json.loads(line)
        return

    # No fixture file → synthesise 50 deterministic rows from the Celtic corpus
    rng = random.Random(42)
    for i in range(50):
        token = _CELTIC_VOCAB[i % len(_CELTIC_VOCAB)]
        kind = _ASSET_KINDS[i % len(_ASSET_KINDS)]
        yield {
            "asset_id": new_uuid7_like(),
            "player_id": f"player_{i:04d}",
            "asset_kind": kind,
            "world_x": rng.uniform(-100.0, 100.0),
            "world_y": rng.uniform(0.0, 50.0),
            "world_z": rng.uniform(-100.0, 100.0),
            "created_at": ms_now(),
            "curriculum_hook": token[2],
            "celtic_token_ga": token[0],
            "celtic_token_en": token[1],
        }


def _rows_from_spacetimedb() -> Iterator[dict[str, Any]]:
    """Yield rows from the live SpacetimeDB `player_assets` table.

    Reads via the SpacetimeDB Python SDK (https://spacetimedb.com). Requires
    the SPACETIMEDB_URL env var (default ``ws://localhost:3000``).
    """
    # Defer the heavy import; only resolved when USE_LOCAL_SCRAPES=false.
    from spacetimedb_sdk import connect, query  # type: ignore  # noqa: F401

    url = os.environ.get("SPACETIMEDB_URL", "ws://localhost:3000")
    conn = connect(url)
    table = conn.db.player_assets  # type: ignore[attr-defined]
    for row in table.iter():
        yield {
            "asset_id": row.asset_id,
            "player_id": row.player_id,
            "asset_kind": row.asset_kind,
            "world_x": row.world_x,
            "world_y": row.world_y,
            "world_z": row.world_z,
            "created_at": int(row.created_at),
            "curriculum_hook": row.curriculum_hook,
            "celtic_token_ga": row.celtic_token_ga,
            "celtic_token_en": row.celtic_token_en,
        }


@dlt.resource(
    name=TABLE,
    write_disposition="merge",
    primary_key="asset_id",
)
def player_assets_source(
    use_local: bool | None = None,
    player_ids: list[str] | None = None,
) -> Iterator[dict[str, Any]]:
    """DLT resource: per-player procedural asset ledger."""
    if use_local is None:
        use_local = use_local_scrapes()

    if use_local:
        rows = _rows_from_local_fixtures()
    else:
        rows = _rows_from_spacetimedb()

    if player_ids:
        rows = (r for r in rows if r["player_id"] in set(player_ids))

    for r in rows:
        yield r


@dlt.source
def player_assets() -> Any:
    """DLT source grouping the player_assets resource."""
    return player_assets_source()


def run() -> int:
    """CLI entrypoint: load player_assets via DLT, return row count."""
    pipeline = build_pipeline(PIPELINE_NAME)
    with observer_for(PIPELINE_NAME, TABLE) as observer:
        load_info = pipeline.run(player_assets_source())
        receipt = observer.record(row_count=0, load_info=load_info)
        # Resync the row count from the load package
        try:
            counts = dict(load_info.metrics or {})
            receipt = observer.record(
                row_count=int(counts.get("loaded_items_count", 0)),
                load_info=load_info,
            )
        except Exception:  # pragma: no cover — best-effort row-count resync
            pass

    print(json.dumps({"status": "ok", "table": TABLE, "receipt": receipt.__dict__}, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(run())
