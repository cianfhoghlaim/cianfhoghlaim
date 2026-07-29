# Tuatha — Educational MMO + Celtic Curriculum Game World

> Irish: *tuatha* = "tribe / people". The educational Massive Multiplayer Online
> layer of the Cianfhoghlaim platform. Where Croílár (internal) and
> Cianfhoghlaim (curriculum data) are read/write platforms for staff, Tuatha is
> the **public face** — a 3D Celtic game world where students pilot avatars
> through procedurally-generated landscapes, learn Irish (Gaeilge) vocabulary
> in context, and run quests tied to the BIEP Leaving Certificate syllabus.

```
┌──────────────────────────────────────────────────────────────────┐
│  Tuatha — Web-Public Game + Curriculum + Observability Stack     │
├──────────────────────────────────────────────────────────────────┤
│ web/apps/tuatha-ui/         — TanStack Start dashboard (admin)   │
│ web/apps/tuatha-demo/       — Babylon.js client demo            │
│ stedding/research/mmo/tuatha — research corpora (Celtic names)  │
│ stedding/dev/sruth/tuath/   — dev fixtures + contracts          │
│ tuatha/asset_generation/    — Procedural Celtic badge factory   │
│ tuatha/badges/              — Knowledge graph → UI badge model  │
│ tuatha/contracts/           — SpacetimeDB + API dataclasses     │
│ tuatha/geospatial/          — MapLibre / geoJSON overlay        │
│ tuatha/cocoindex_subject_registry.py — BIEP ↔ Tuatha ontology   │
│ tuatha/dlt/                 — THIS package — dlt → MotherDuck    │
└──────────────────────────────────────────────────────────────────┘
```

## What is in this directory

This is the **bianary entrypoint** for the educational MMO stack. It
does NOT own:

- The Babylon.js game client (lives under `web/apps/tuatha-demo/`)
- The TanStack dashboard UI (lives under `web/apps/tuatha-ui/`)
- The IaC stack config (lives under `bonneagar/stacks/tuatha/`)

It DOES own:

- **Procedural asset generation** — `asset_generation/` synthesises Celtic
  badging, fertility icons, ring fort layouts, Ogham-named avatars
- **Knowledge-graph badges** — `badges/` maps BIEP curriculum concepts to
  in-game unlockable badges (cross-graph for Graphiti/Cognee ↔ LanceDB)
- **Cross-service contracts** — `contracts/` holds Pydantic v2 types shared
  with SpacetimeDB reducers + the FastAPI surface
- **Geospatial layer** — `geospatial/` computes Celtic place-name clusters
  + MapLibre overlay tiles
- **CocoIndex subject registry** — `cocoindex_subject_registry.py` keeps the
  BIEP subject index in sync with Tuatha's in-game quest taxonomy
- **DLT sources** — `dlt/` ships 2 sources into the cianfhoghlaim lakehouse

## DLT sources in this package

| Source | Table | Schema | Purpose |
|:--|:--|:--|:--|
| `player_assets` | `cianfhoghlaim.tuatha.player_assets` | `(asset_id, player_id, asset_kind, world_x, world_y, world_z, created_at, curriculum_hook, celtic_token_ga, celtic_token_en)` | Per-player procedural asset ledger (1 row per spawned tree/rune/badge/ring-fort) with the Celtic name pair and the BIEP subject it reinforces |
| `credential_events` | `cianfhoghlaim.tuatha.credential_events` | `(event_id, player_id, event_type, mc_lc_topic, occurred_at, langfuse_trace_id, mlflow_run_id, payload_json)` | Auth + quest-completion events with sidecar MLflow + Langfuse trace IDs (powers the RAGAS eval of the tutor NPC) |

Both sources use the shared `dlt_sources.common.observability.DltRunObserver`
for MLflow + Langfuse traces, and the shared
`dlt_sources.common.destinations_cianfhoghlaim.get_dlt_destination()` for
the DuckLake / MotherDuck destination.

## Quick start

```bash
# 1. One-command local dev (builds api/ui/game containers, runs migrations,
#    seeds SpacetimeDB reducer, runs both dlt sources against a local DuckDB)
./scripts/bootstrap.sh

# 2. Play the game
open http://localhost:8080         # Babylon.js game client
open http://localhost:3010         # TanStack Start dashboard
open http://localhost:8002/healthz # FastAPI healthcheck

# 3. Inspect the MotherDuck mirror
python3 -c "import duckdb; duckdb.connect('md:cianfhoghlaim').execute('SHOW TABLES FROM cianfhoghlaim.tuatha').df()"
```

## Run the dlt pipelines in isolation

```bash
# Player assets only (uses local fallback by default — no API credits burned)
USE_LOCAL_SCRAPES=true python3 -m tuatha.dlt.player_assets

# Credential events only
USE_LOCAL_SCRAPES=true python3 -m tuatha.dlt.credential_events

# Both — uses DUCKLAKE for prod, DuckDB local for dev
USE_DUCKLAKE=false python3 -m tuatha.dlt.run_all

# MLflow UI
mlflow ui --backend-store-uri sqlite:///mlflow.db
# Langfuse UI
docker compose -f ../bonneagar/stacks/langfuse/compose.yaml up -d
```

## Smoke tests

```bash
python3 -m pytest tuatha/tests/test_smoke.py -v
```

This verifies:

- Both dlt source modules import without error
- Schema is stable (the 8 named columns per source)
- `DltRunObserver.record()` yields a valid receipt
- `get_dlt_destination()` returns a destination in BOTH modes
  (DuckLake + DuckDB fallback)

## Operational notes

- **Public exposure**: Tuatha is the **only** publicly-reachable stack in the
  Cianfhoghlaim platform. The `tuath.cianfhoghlaim.ie` route is rate-limited;
  `tuath-api` and `tuath-ui` are TinyAuth passkey-gated via Pocket ID.
- **Cost control**: set `USE_LOCAL_SCRAPES=true` for dlt, and the pipeline
  reads from `stedding/ingest_queue/` instead of hitting OpenAI / Coursera.
- **Rotation**: client secrets rotate every 90 days via
  `./scripts/rotate-tuatha-secrets.sh --install-cron`.
- **Resource cost**: 1× Apple M4 CPU + 8 GB RAM per pod. SpacetimeDB is the
  hot path; LanceDB tables live in tmpfs in dev, S3-backed in prod.

## Sub-module READMEs

- [`asset_generation/`](./asset_generation/) — procedural badge/icon generation
- [`badges/`](./badges/) — BIEP concept → unlockable badge model
- [`contracts/`](./contracts/) — shared Pydantic v2 types (SpacetimeDB + FastAPI)
- [`geospatial/`](./geospatial/) — Celtic place-name clusters + MapLibre tiles
- [`dlt/`](./dlt/) — dlt sources (player_assets, credential_events)
