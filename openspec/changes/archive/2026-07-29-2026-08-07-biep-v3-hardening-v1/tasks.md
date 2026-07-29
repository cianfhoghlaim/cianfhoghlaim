# 2026-08-07-biep-v3-hardening-v1 — Tasks

## Pre-implementation
- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1

## Stage 1 — Canonical BAML clients
- [ ] Create `baml_src/clients_biep_v3.baml`
- [ ] Update all 67+ active BAML functions to use the 3 canonical clients

## Stage 2 — BAML codegen CI gate
- [ ] Fix `.github/workflows/baml-test.yaml:33-50`
- [ ] Add `baml-cli generate` + `baml-cli check` + drift check
- [ ] Update `.gitignore`
- [ ] Add 8 golden tests

## Stage 3 — 3 missing sensors + 1 S3 sensor
- [ ] Create `orchestration/sensors/jersey_registry_sensor.py`
- [ ] Create `orchestration/sensors/guernsey_registry_sensor.py`
- [ ] Create `orchestration/sensors/isle_of_man_registry_sensor.py`
- [ ] Create `orchestration/sensors/garage_pdf_arrival_sensor.py`

## Stage 4 — Hoist 4 pipelines to a base class
- [ ] Create `dlt/british_isles/_cross/jurisdiction_pipeline_base.py`
- [ ] Refactor 4 jurisdiction pipeline files to use the base class

## Stage 5 — Connection pool + DuckLake time-travel helper
- [ ] Add `DuckLakeConnectionPool` to `dlt/common/ducklake_options.py`
- [ ] Add `time_travel_query` helper

## Stage 6 — mode + tenant + iceberg flags
- [ ] Edit `dlt/common/destinations_cianfhoghlaim.py:188-225` — add the 3 flags

## Stage 7 — Iceberg write path
- [ ] Create `dlt/common/iceberg_options.py`
- [ ] Add `_build_iceberg_local_destination()` to destinations factory

## Stage 8 — Snapshots + Shares for MotherDuck
- [ ] Add `snapshot_database()`, `create_share()`, `attach_share()`, `compute_size` to `dlt/common/motherduck_options.py`

## Stage 9 — Spec delta + validation
- [ ] Write spec delta to `openspec/changes/2026-08-07-biep-v3-hardening-v1/specs/infrastructure-stacks/spec.md`
- [ ] `openspec validate 2026-08-07-biep-v3-hardening-v1 --strict`
- [ ] Commit + push
- [ ] Archive after merge

## Post-implementation
- [ ] File any remaining bugs
- [ ] Run `./scripts/sync_agent_docs.sh`