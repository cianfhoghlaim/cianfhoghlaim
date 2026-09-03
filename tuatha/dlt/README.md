# tuatha/dlt — dlt sources for the Tuatha game world

```python
# Run a single source as a Python module
python3 -m tuatha.dlt.player_assets
python3 -m tuatha.dlt.credential_events

# Run both sources in one go
python3 -m tuatha.dlt.run_all
```

The 2 dlt sources emit rows into the `cianfhoghlaim.tuatha.*` schema under
the shared `md:cianfhoghlaim` MotherDuck + DuckLake database.

## Files

- `player_assets.py` — Per-player procedural asset ledger (trees, runes, badges, ring forts)
- `credential_events.py` — Auth + quest-completion events with sidecar MLflow + Langfuse
- `_shared.py` — Common helpers (observer factory, breadcrumbs, table-name constants)
- `run_all.py` — Orchestrator that runs both sources sequentially with shared observability
- `__init__.py` — Re-exports `player_assets_source` and `credential_events_source`

## Conventions

- **NEVER** use absolute namespaces — imports stay relative to this package.
- **ALWAYS** set `pipelines_dir` so DLT's `_storage` directory lives under the
  repo root (not the user's $HOME).
- **ALWAYS** honour `USE_LOCAL_SCRAPES=true` for the read path (the game
  emits into a local SpacetimeDB instance in dev).
- **ALWAYS** honour `USE_DUCKLAKE=false` to fall back to local DuckDB.
- **ALWAYS** instrument runs with `DltRunObserver` (MLflow + Langfuse).
- **ALWAYS** include `event_id` / `asset_id` as a primary-key hint for dlt
  merge keys.
