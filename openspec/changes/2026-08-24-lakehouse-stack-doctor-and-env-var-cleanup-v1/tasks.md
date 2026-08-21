# Tasks: 2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1/proposal.md`
- [ ] **T1.2**: Create `openspec/changes/2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/changes/2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1/specs/infrastructure-stacks/spec.md` (3 ADDED Requirements + 1 MODIFIED Requirement)

## Phase 2: Validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1 --strict` and verify it passes

## Phase 3: Single source of truth for DB list (2 tasks)

- [ ] **T3.1**: Create `bonneagar/stacks/lakehouse/db_manifest.yaml` with the 14 databases grouped by purpose (ducklake, dagster, lakehouse_internal, downstream, graph_db, olake_source)
- [ ] **T3.2**: Update `bonneagar/stacks/lakehouse/init-db.sql` header comment to reference `db_manifest.yaml` as the source of truth

## Phase 4: Pydantic Settings class (1 task)

- [ ] **T4.1**: Create `bonneagar/stacks/lakehouse/config.py` with `LakehouseSettings(BaseSettings)` class:
  - `GarageSettings` (rpc_secret, admin_token, access_key_id, secret_access_key)
  - `LakekeeperSettings` (encryption_key, base_uri, ssl_mode, pg_host_r/w, metrics_port, pagination)
  - `CogneeSettings` (postgres_user, postgres_password, llm_api_key, embedding_api_key)
  - `GraphitiSettings` (openai_api_key, openai_base_url)
  - `FalkorDBSettings` (password, vector_module_url, cluster_mode, args)
  - `MemgraphSettings` (user, password, license_file_path)
  - `LanceNamespaceSettings` (endpoint, warehouse, auth_token, lance_root)
  - `ObservabilitySettings` (langfuse_*, mlflow_*, logfire_token)
  - `LakehouseSettings` (the parent aggregating all)

## Phase 5: Split `.infisical.env` into lakehouse sub-files (8 tasks)

- [ ] **T5.1**: Create `.infisical.env.lakehouse` (~62 lines) with garage + postgres + clickhouse + redis + lakekeeper + olake + lance + motherduck + planetscale + DuckLake vars
- [ ] **T5.2**: Create `.infisical.env.cognee` (~10 lines) with COGNEE_LLM_API_KEY, COGNEE_EMBEDDING_API_KEY, COGNEE_POSTGRES_PASSWORD, COGNEE_LLM_MODEL, COGNEE_EMBEDDING_MODEL, GALILEO_API_KEY
- [ ] **T5.3**: Create `.infisical.env.falkordb` (~3 lines) with FALKORDB_PASSWORD + VECTOR_MODULE_URL + CLUSTER_MODE
- [ ] **T5.4**: Create `.infisical.env.memgraph` (~4 lines) with MEMGRAPH_USER + MEMGRAPH_PASSWORD + MEMGRAPH_LICENSE_FILE_PATH + MEMGRAPH_LOG_LEVEL
- [ ] **T5.5**: Create `.infisical.env.lancedb` (~3 lines) with LANCEDB_API_KEY + LANCEDB_NAMESPACE_TOKEN + LANCEDB_REGION
- [ ] **T5.6**: Create `.infisical.env.observability` (~15 lines) with LOGFIRE_TOKEN + LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY + LANGFUSE_HOST + MLFLOW_TRACKING_URI + MLFLOW_ARTIFACT_ROOT
- [ ] **T5.7**: Update root `.infisical.env` header comment to reference the sub-files + remove the extracted sections
- [ ] **T5.8**: Verify `scripts/init-vault.ts` still parses the root `.infisical.env` correctly

## Phase 6: lakehouse profile in stack-doctor (2 tasks)

- [ ] **T6.1**: Create `scripts/lakehouse-stack-doctor.sh`:
  - Validates 17 services in compose.yaml
  - Validates 14 databases in init-db.sql match db_manifest.yaml
  - Validates 10 private-resources in blueprint.yaml
  - Validates 5 routes in pangolin.yaml
  - Validates 53+ Infisical URIs in secrets.env
  - Validates 100% of image tags pinned (with documented exceptions)
  - Validates no hardcoded absolute paths in sidecar.yaml
- [ ] **T6.2**: Add `lakehouse:stack-doctor` task to `mise.toml`:
  ```toml
  [tasks."lakehouse:stack-doctor"]
  description = "Lint the unified lakehouse stack (17 services + 14 DBs + 10 routes + 53+ URIs + image pinning + no absolute paths)"
  run = "bash scripts/lakehouse-stack-doctor.sh"
  ```

## Phase 7: garage-init bash → Python (2 tasks)

- [ ] **T7.1**: Create `bonneagar/stacks/lakehouse/garage_init.py` using boto3:
  - Replicates the 50-line bash logic (wait for garage health, configure layout, create key, create 8 buckets)
  - Better error handling + retry logic
  - Cleaner Python (no shell escaping issues)
- [ ] **T7.2**: Update `bonneagar/stacks/lakehouse/compose.yaml` — `garage-init` service:
  - Change image from `curlimages/curl:latest` to `python:3.11-slim` + install boto3
  - Change command to invoke the Python script
  - Or: build a custom image (the simplest path)

## Phase 8: Validate read-only shadow stacks (2 tasks)

- [ ] **T8.1**: Create `scripts/validate-deprecated-stacks.sh`:
  - For each of the 5 deprecated stacks (cognee/ + graphiti/ + falkordb/ + memgraph/ + lancedb/):
    - Verify `docker compose config --quiet` passes
    - Verify the deprecation banner is present (grep for "DEPRECATED 2026-08-15")
    - Verify the README documents the move to lakehouse
- [ ] **T8.2**: Run the validator and verify all 5 pass

## Phase 9: Quality gates (4 tasks)

- [ ] **T9.1**: Run `openspec validate 2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1 --strict`
- [ ] **T9.2**: Run `docker compose -f compose.yaml -f sidecar.yaml config --quiet` (lakehouse)
- [ ] **T9.3**: Run `mise run lint:skills`, `mise run lint:drift-docs`, `mise run lint:registry`
- [ ] **T9.4**: Run `bash scripts/lakehouse-stack-doctor.sh` (the new task) and verify it passes

## Phase 10: Commit + push (2 tasks)

- [ ] **T10.1**: Stage only the PR #3 files (NOT touching the 15+ pre-existing uncommitted changes from earlier sessions)
- [ ] **T10.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`

## Total: 22 tasks across 10 phases

Estimated effort: ~3-4 hours of file edits + ~30 minutes for openspec validate + CI gates.