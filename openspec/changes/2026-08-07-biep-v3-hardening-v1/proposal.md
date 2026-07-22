# 2026-08-07-biep-v3-hardening-v1

## Why

The P1 layer consolidates the BIEP v3 stack infrastructure:
canonical BAML clients, CI gates, jurisdiction pipeline base class,
DuckLake connection pool + time-travel helper, MotherDuck sizing +
snapshots + shares, Iceberg write path. 8 items.

Lives in the `cianfhoghlaim` repo.

## What changes

### 1. Canonical BAML clients

Create `baml_src/clients_biep_v3.baml` with:
- `BIEPV3Extract` (replaces `ExtractEn`) — Gemma 3 4B + retries + timeout + max_tokens
- `BIEPV3ExtractStrong` (replaces `ExtractEnStrong`) — Qwen 3-VL 8B + retries
- `BIEPV3Vision` — for the 4-path OCR ensemble (qwen3-vl-8b via llama-swap)

Update all 67+ active BAML functions to use the 3 canonical clients.

### 2. BAML codegen CI gate

- Fix `.github/workflows/baml-test.yaml:33-50` to use the actual repo root
- Add a `baml-cli generate` step + `baml-cli check` step + drift check
- Remove `.gitignore:143-147` for the generated `baml_client/` output
- Add 8 golden tests (one per jurisdiction) with EN/GA/CY/GD/GV fixtures

### 3. 3 missing sensors + 1 S3 sensor

- `orchestration/sensors/{jersey,guernsey,isle_of_man}_registry_sensor.py` — clone the NCCA sensor
- `orchestration/sensors/garage_pdf_arrival_sensor.py` (new, ~50 LOC) — polls S3 for new PDFs

### 4. Hoist 4 pipelines to a base class

`dlt/british_isles/_cross/jurisdiction_pipeline_base.py` (new, ~80 LOC) — `class JurisdictionPipelineBase` with `__init__`, `build_resource`, `build_pipeline`. The 4 jurisdiction files become ~25 LOC of overrides each.

### 5. Connection pool + DuckLake time-travel helper

- `dlt/common/ducklake_options.py:120-151` — add `DuckLakeConnectionPool(max_size=8)` + `time_travel_query(table, at_timestamp=...)`

### 6. `mode` + `tenant` + `iceberg` flags

`dlt/common/destinations_cianfhoghlaim.py:188-225` — add `mode`, `tenant`, `iceberg` arguments.

### 7. Iceberg write path

- `dlt/common/iceberg_options.py` (new, ~120 LOC)
- `destinations_cianfhoghlaim.py:188-225` — add `_build_iceberg_local_destination()`

### 8. Snapshots + Shares for MotherDuck

`dlt/common/motherduck_options.py:50-94` — `snapshot_database()`, `create_share()`, `attach_share()`, `compute_size`.

## Dependencies

```yaml
Blocked by: 2026-08-06-biep-v3-critical-path-fixes-v1
Affected repos: cianfhoghlaim
```

## Acceptance gates

- `baml-cli generate` succeeds + CI gate fails on drift
- `baml-cli check` passes for all 67+ BAML functions
- `dg list components` shows the 8 new sensors
- The 4 jurisdiction pipelines use the base class (no copy-paste)

## Cross-references
- `baml_src/clients_biep_v3.baml` (new canonical file)
- `dlt/british_isles/_cross/jurisdiction_pipeline_base.py` (new base class)
- `dlt/common/iceberg_options.py` (new Iceberg helpers)