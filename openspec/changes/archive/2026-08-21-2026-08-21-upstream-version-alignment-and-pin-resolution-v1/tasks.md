# Tasks — 2026-08-21-upstream-version-alignment-and-pin-resolution-v1

## 1. Resolve the 2 pin ambiguities (BLOCKS all subsequent bumps)

- [ ] 1.1 Confirm with the operator: is `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0` → `0.2.1` a *new image* or a *republish with fix*? (Documentation marker for changelog.)
- [ ] 1.2 Confirm with the operator: is `quay.io/lakekeeper/catalog:v0.13.1` a private fork's `0.13.x` tag or the upstream `0.6.x` source code? Reconcile the `bonneagar/komodo/stacks/lakehouse-oci.toml` image tag.
- [ ] 1.3 Resolve the Infisical pin discrepancy: server `v0.161.12` is correct (per the running bunchloch container); CLI hygiene via `mise tool install infisical@latest` so local CLI matches upstream `v0.43.x`.
- [ ] 1.4 Decide (operator call): stay on Lakehouse Garage `v2.3.0` (no upstream change) OR bump to a hypothetical `v2.4.0` if it lands before Phase 3 completion.

## 2. Update the openspec umbrella change

- [ ] 2.1 Run `openspec validate 2026-08-21-upstream-version-alignment-and-pin-resolution-v1 --strict` — MUST exit 0 before any sub-change is opened.
- [ ] 2.2 Open the `centralized-model-registry` spec delta adding the 3 new OCR models (see spec delta files).
- [ ] 2.3 Open the `litellm-router` spec delta adding the v1.97 MCP-OAuth-2.0-v2 + DCR endpoints.
- [ ] 2.4 Open the `langfuse-observability` spec delta adding the v3 → v4 migration contract.

## 3. Open + implement the bump sub-changes (topo order)

### 3.0 Pin resolution (BLOCKER for §3.1-3.14)

- [ ] 3.0.1 Open `2026-08-21-internal-pin-resolution-v1/` if §1 reveals a major discrepancy (e.g. Lakekeeper is a fork).
- [ ] 3.0.2 Open `2026-08-21-internal-pin-doc-cleanup-v1/` — pure documentation cleanup if the pins were correct.

### 3.1 Priority 0 — Langfuse v3 → v4 (MANDATORY before 2026-11-16)

- [ ] 3.1.1 Open `2026-08-21-langfuse-v3-to-v4-migration-v1/` (per the audit).
- [ ] 3.1.2 Bump `pyproject.toml` to `langfuse>=4.0,<5.0`.
- [ ] 3.1.3 Self-hosted server: follow https://langfuse.com/self-hosting/upgrade/upgrade-guides/upgrade-v3-to-v4 from a Snapshot-first restore.
- [ ] 3.1.4 Audit the 47 `agents/meaisinfhoghlaim/agents/*.py` call sites for `start_span`/`start_generation`/`update_current_trace`/`DatasetItemClient` usage. Replace with v4 equivalents.
- [ ] 3.1.5 Verify the 6-file compose stack for `langfuse` ships the new `LANGFUSE_BASE_URL` env var (Locket sidecar).
- [ ] 3.1.6 Validate `openspec validate 2026-08-21-langfuse-v3-to-v4-migration-v1 --strict` exits 0.
- [ ] 3.1.7 Archive the change.

### 3.2 Priority 1 — DLT 1.28.1 → 1.30.0

- [ ] 3.2.1 Open `2026-08-21-dlt-1.28.1-to-1.30.0-v1/`.
- [ ] 3.2.2 Audit the 10 jurisdiction pipelines (`dlt_sources/british_isles/{ie,sct,wls,ni,iom,jey,ggy}/{education,...}/*.py`) for `pipeline.dataset()` calls without `schema=` kwarg.
- [ ] 3.2.3 Bump `dlt[duckdb,motherduck,filesystem]` in `pyproject.toml`.
- [ ] 3.2.4 Replace `replace` with `refresh` write_disposition in the daily Flight.
- [ ] 3.2.5 Re-run the BIEP v3 Ireland LC pipeline against the 80 PDFs at `/leaving_certificate/` (Phase 4 fixture) — assert same 80 rows.
- [ ] 3.2.6 Validate + archive.

### 3.3 Priority 1 — BAML 0.223.0 → 0.224.0

- [ ] 3.3.1 Open `2026-08-21-baml-0.223-to-0.224-v1/`.
- [ ] 3.3.2 Audit `baml_src/clients.baml` (×7) + `baml_src/clients_biep_v3.py` for `baml_core` imports → rename to `baml_bridge`.
- [ ] 3.3.3 Audit for `@@dynamic` attributes + legacy `type_builder { ... }` blocks → migrate to `baml.reflect` namespace.
- [ ] 3.3.4 Bump `baml>=0.224,<0.225`.
- [ ] 3.3.5 Verify `baml-py` is upgradable (no compilation errors).
- [ ] 3.3.6 Validate + archive.

### 3.4 Priority 1 — DuckDB 1.4.x → 1.5.4

- [ ] 3.4.1 Open `2026-08-21-duckdb-1.4-to-1.5.4-v1/`.
- [ ] 3.4.2 Bump `duckdb>=1.4,<1.5.5` → `duckdb>=1.5.4,<1.5.5` (MD-supported; skip 1.5.5).
- [ ] 3.4.3 Bump the lakehouse image tag from `duckdb/duckdb:1.4.x` to `duckdb/duckdb:1.5.4`.
- [ ] 3.4.4 Re-test the 24 BIEP tables + `gov_circulars_archive` for `VARIANT` rejection (MD doesn't have VARIANT yet).
- [ ] 3.4.5 Validate + archive.

### 3.5 Priority 1 — mlflow 3.12.0 → 3.15.1

- [ ] 3.5.1 Open `2026-08-21-mlflow-3.12-to-3.15.1-v1/`.
- [ ] 3.5.2 Bump `mlflow>=3.12,<4.0` → `mlflow>=3.15.1,<4.0`.
- [ ] 3.5.3 Add `MLFLOW_ALLOW_FILE_STORE=true` to `bonneagar/stacks/mlflow/secrets.env` (legacy SQLite fallback at `mlruns/`).
- [ ] 3.5.4 Audit the 5 BAML+Mlflow callsites for `judge.align()` (`MemAlign` is now default).
- [ ] 3.5.5 If MCP Registry is enabled, expose `/api/mcp/registry` in `pangolin.yaml`.
- [ ] 3.5.6 Validate + archive.

### 3.6 Priority 2 — CocoIndex 1.0.14 → 1.0.20

- [ ] 3.6.1 Open `2026-08-21-cocoindex-1.0.14-to-1.0.20-v1/` (per `2026-08-17-hygiene-drift-cleanup-v1`).
- [ ] 3.6.2 Add `deps=` parameter to the 14 `@coco.fn(memo=True)` sites.
- [ ] 3.6.3 Bump `cocoindex>=1.0.14,<1.0.8,!=1.0.8` → `>=1.0.20,<2.0`.
- [ ] 3.6.4 Run `bun run cocoindex update --pip`.
- [ ] 3.6.5 Verify 196 CocoIndex files still AST-parse.
- [ ] 3.6.6 Validate + archive.

### 3.7 Priority 2 — LanceDB 0.34.0 → 0.37.1

- [ ] 3.7.1 Open `2026-08-21-lancedb-0.34-to-0.37.1-v1/`.
- [ ] 3.7.2 Bump `lancedb>=0.34,<0.38` → `lancedb>=0.37.1,<0.38`.
- [ ] 3.7.3 Optionally add the Lance × DuckDB SQL extension to the BIEP federated SQL layer.
- [ ] 3.7.4 Validate + archive.

### 3.8 Priority 2 — LiteLLM 1.91.0 → 1.97.0

- [ ] 3.8.1 Open `2026-08-21-litellm-1.91-to-1.97-v1/`.
- [ ] 3.8.2 Bump `litellm>=1.91,<1.98` → `litellm>=1.97,<1.98` in `pyproject.toml`.
- [ ] 3.8.3 Bump `ghcr.io/berriai/litellm-database:v1.91.0` → `v1.97.0` in `bonneagar/stacks/litellm/compose.yaml`.
- [ ] 3.8.4 Verify `LITELLM_MASTER_KEY`, `LITELLM_SALT_KEY`, `LITELLM_DATABASE_URL` are in `infisical://dev-baile/litellm/`.
- [ ] 3.8.5 Expose `/v1/messages` (Rust-based v1.95.0) in `pangolin.yaml`.
- [ ] 3.8.6 Re-run `mise run ml:litellm:regenerate` to refresh config from MODEL_REGISTRY.
- [ ] 3.8.7 Validate + archive.

### 3.9 Priority 2 — Dagster 1.13.0 → 1.13.18

- [ ] 3.9.1 Open `2026-08-21-dagster-1.13-to-1.13.18-v1/`.
- [ ] 3.9.2 Bump `dagster>=1.13,<2.0` → `dagster>=1.13.18,<2.0`.
- [ ] 3.9.3 Adopt `DltLoadCollectionComponent` `partitions_def` for per-LC-subject partitions.
- [ ] 3.9.4 Verify Dagster still loads 557 assets (no schema drift).
- [ ] 3.9.5 Validate + archive.

### 3.10 Priority 2 — PaddleOCR 3.0.0 → 3.0.1

- [ ] 3.10.1 Open `2026-08-21-paddleocr-3.0-to-3.0.1-v1/`.
- [ ] 3.10.2 Bump `paddleocr>=3.0,<4.0` → `paddleocr>=3.0.1,<4.0`.
- [ ] 3.10.3 Update `MODEL_REGISTRY` to advertise PaddleOCR-VL-1.6 + PP-OCRv6 plugin.
- [ ] 3.10.4 Validate + archive.

### 3.11 Priority 2 — dots.ocr → dots.mocr (model-registry swap)

- [ ] 3.11.1 Open `2026-08-21-dotsocr-to-dotsmocr-v1/`.
- [ ] 3.11.2 Add `dots.mocr` (`rednote-hilab/dots.mocr`) to `MODEL_REGISTRY` as the new primary in the OCR ensemble.
- [ ] 3.11.3 Update `baml_src/clients_biep_v3.py` to call `dots.mocr` via `ExtractEnStrong`.
- [ ] 3.11.4 Mark the 7 stacks that reference `ghcr.io/rednote-hilab/dots.ocr:1.5` for follow-up bump (open separate change per stack).
- [ ] 3.11.5 Validate + archive.

### 3.12 Priority 2 — OlmOCR-2 (model-registry addition)

- [ ] 3.12.1 Open `2026-08-21-olmocr-to-olmocr-2-v1/`.
- [ ] 3.12.2 Add `olmocr-2` (`allenai/olmocr-2`) to `MODEL_REGISTRY` as an alternative in the OCR ensemble.
- [ ] 3.12.3 Validate + archive.

## 4. Final verification

- [ ] 4.1 Run `mise run core:ci` — must exit 0 across the 14 CI gates (lint + test + openspec:validate-all + devops:validate-stacks).
- [ ] 4.2 Run `mise run sync:all` (the 14-layer pull-based sync).
- [ ] 4.3 Re-run the Phase 4 Ireland LC pipeline end-to-end against `/leaving_certificate/` — assert 80 rows still load.
- [ ] 4.4 Verify the 6-stack critical path remains green via `curl` against each main service port.
- [ ] 4.5 Confirm `mise run data:status` reports all 7 sections OK with the bumped pins.
- [ ] 4.6 Push the umbrella + sub-changes via the openspec archive workflow.
