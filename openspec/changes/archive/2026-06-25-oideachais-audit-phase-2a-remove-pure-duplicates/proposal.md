# Change: oideachais-audit-phase-2a-remove-pure-duplicates

## Why

Round 11 cross-quadrant sprawl audit (2026-06-25) identified 5 duplicate surface pairs in `sruth/oideachais/`. Three pairs are **pure byte-identical duplicates** (zero risk, zero importers) and one pair has a **single deprecated stub file** that requires 1 test-import update.

These four surfaces survived the `137ad7b9a refactor: move meaisinfhoghlaim to sruth/ + complete oideachais refactor` commit because their canonical homes (`api/routes/`, `dagster_defs/sensors/`, `api/middleware/`) were renamed/restructured but the old top-level dirs were never `git rm`'d.

Removing them now closes the "where does X live?" ambiguity surfaced in agent_observability + change_detection scans (cross-quadrant duplicates consume ~5,500 LOC that drift independently from the canonical surfaces).

## What Changes

### `git rm -r sruth/oideachais/routes/` (5 .py + README, 2,836 LOC)

100% byte-identical to `sruth/oideachais/api/routes/`. Zero importers outside the directory itself. Canonical already has 3 additional files (`cross_archive_graph.py`, `leaving_cert.py`, `official_media.py`) the duplicate lacks.

### `git rm -r sruth/oideachais/sensors/` (2 .py + __init__ + README, 994 LOC)

`curriculum_freshness.py` (509 LOC) and `domain_sensors.py` (451 LOC) are byte-identical to canonical `dagster_defs/sensors/`. The duplicate `__init__.py` is STALE — only loads 2 of the 5 canonical sensor groups (missing `author_archive_sensors`, `cognee_cron_sensor`, `leabharlann_sensors`). Zero importers outside the directory itself.

### `git rm -r sruth/oideachais/middleware/` (6 files + README, 1,668 LOC)

100% byte-identical to `sruth/oideachais/api/middleware/`. Zero importers outside the directory itself. Cleanest 100% byte-identical duplicate in the entire investigation.

### `git rm sruth/oideachais/storage/serial_executor.py` (29 LOC, 1 importer)

The file self-declares deprecated (`DeprecationWarning`) and re-exports from `sruth.oideachais.core.storage.serial_executor`. Only importer is `sruth/oideachais/tests/conftest.py:244` which must be updated to import from canonical.

## Impact

- **LOC removed:** 5,527 (2,836 + 994 + 1,668 + 29)
- **Files removed:** 17 (11 .py + 4 README + 2 __init__)
- **Imports updated:** 1 (test)
- **Risk:** zero — verified pre-flight grep across all of `sruth/`, `infrastructure/`, `apps/`, `web/`, `tests/`, `openspec/` confirms zero importers for `routes/`, `sensors/`, `middleware/` and exactly 1 test-only importer for `storage/serial_executor.py`
- **Atomic:** yes — all 4 deletions are independent, but consolidating them reduces PR noise (4 separate deletions vs 1 commit)

## Phase 5 / #2B Follow-ups

The remaining duplicates are NOT in this change:

- **`dagster_assets/`** (2,179 LOC, mixed): migrate 2 active modules (`model_conversion.py`, `asset_generation.py`) → `dagster_defs/assets/`, then `git rm` the rest
- **`storage/` (excluding `serial_executor.py`)** (5,557 LOC, mostly unique): migrate 9 unique files (`config.py`, `connections.py`, `ducklake.py`, `ducklake_client.py`, `ducklake_filesystem.py`, `init_schemas.py`, `lance_iceberg.py`, `lancedb_cloud.py`, `curriculum_vectors.py`) → `core/storage/{clients,config,schemas}/`, then `git rm`

These will land in the follow-up openspec change `oideachais-audit-phase-2b-migrate-legacy-storage-and-dagster-assets`.

## Validation Gates

```bash
openspec validate oideachais-audit-phase-2a-remove-pure-duplicates --strict
python -c "import sruth.oideachais; print('OK')"
# python -c "from sruth.oideachais.api.routes import agent, curriculum, search, geospatial, tts, cross_archive_graph, leaving_cert, official_media"  # all 8 routers still importable
# python -c "from sruth.oideachais.dagster_defs.sensors import all_sensors; print(len(all_sensors))"  # 5 sensor groups registered
# python -c "from sruth.oideachais.api.middleware import AuthMiddleware"  # middleware still importable
# python -c "from sruth.oideachais.core.storage import SerialDatabaseExecutor"  # canonical replaces deprecated stub
```

## References

- `AGENTS.md:97-105` — canonical surface routing table
- `dg.toml:15` — Dagster module_name points at `dagster_defs/`, never `dagster_assets/`
- `api/main.py:137,146-160` — sole wiring sites for middleware + 6 routers
- `dagster_defs/definitions.py:294` — sole wiring site for `all_sensors`
- `core/storage/__init__.py:13-18` — sole authoritative storage re-export
- `storage/serial_executor.py:11-23` — self-declares deprecated
- `tests/conftest.py:244` — sole test importer of deprecated stub
- Investigation report: `openspec/changes/oideachais-audit-phase-1-delete-dead-code/proposal.md` audit §"Pair 2/3/4/5a"
