# Tasks: 2026-08-15-lakehouse-unified-data-plane-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/proposal.md` (the why + what changes)
- [ ] **T1.2**: Create `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/specs/infrastructure-stacks/spec.md` (the 1 ADDED Requirement with 3 Scenarios)

## Phase 2: Run openspec validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-15-lakehouse-unified-data-plane-v1 --strict` and verify it passes

## Phase 3: Lakehouse compose.yaml — add 5 services (1 file modified)

- [ ] **T3.1**: Add the 5 new services to `bonneagar/stacks/lakehouse/compose.yaml` (after `lancedb-viewer`):
  - `cognee` (image `cognee/cognee:1.2.2`, container `lakehouse-cognee`, port 8000) — uses shared `lakehouse-postgres:cognee_cianfhoghlaim` DB + LiteLLM at `http://litellm:4000/v1` + Lance Namespace at `rest://lakehouse-lance-namespace:8182`
  - `graphiti` (image `graphiti:local`, container `lakehouse-graphiti`, port 8000) — depends on `falkordb`, uses shared falkordb at `falkordb:6379`
  - `falkordb` (image `falkordb/falkordb:v4.18.11`, container `lakehouse-falkordb`, ports 6379 + 3000 BROWSER) — `--appendonly yes --appendfsync everysec` + `--loadmodule /etc/falkordb/vector.so` + `FALKORDB_ARGS=THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000`
  - `memgraph` (image `memgraph/memgraph-mage:3.6.0`, container `lakehouse-memgraph`, ports 7687 + 7444) — Bolt + Lab UI
  - `memgraph-lab` (image `memgraph/lab:3.6.0`, container `lakehouse-memgraph-lab`, port 3000) — connects to memgraph:7687
- [ ] **T3.2**: All 5 new services join `networks: [lakehouse]` only (no per-stack bridge networks)
- [ ] **T3.3**: All 5 new services add `depends_on: [locket: service_healthy]` + `volumes: [lakehouse-secrets:/run/secrets/locket:ro]` via the sidecar overlay

## Phase 4: Lakehouse secrets.env — add ~30 keys (1 file modified)

- [ ] **T4.1**: Add the Cognee section (~16 keys): `COGNEE_LLM_MODEL`, `COGNEE_EMBEDDING_MODEL`, `COGNEE_POSTGRES_PASSWORD` (resolved from `POSTGRES_PASSWORD` at compose time), `LANCEDB_API_KEY`, `LANCEDB_NAMESPACE_TOKEN`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `GALILEO_API_KEY`, `REQUIRE_AUTHENTICATION`, `ENABLE_BACKEND_ACCESS_CONTROL`, `PLANETSCALE_DATABASE_URL`, `COGNEE_DATABASES`, `LOG_LEVEL`, `ENVIRONMENT`
- [ ] **T4.2**: Add the Graphiti section (~5 keys): `FALKORDB_PASSWORD`, `FALKORDB_GRAPHITI_DB`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LANGFUSE_*`
- [ ] **T4.3**: Add the FalkorDB section (3 keys): `FALKORDB_PASSWORD`, `VECTOR_MODULE_URL`, `CLUSTER_MODE`
- [ ] **T4.4**: Add the Memgraph section (~4 keys): `MEMGRAPH_USER`, `MEMGRAPH_PASSWORD`, `MEMGRAPH_LICENSE_FILE_PATH`, `MEMGRAPH_LOG_LEVEL`

## Phase 5: init-db.sql — add cognee_cianfhoghlaim database (1 file modified)

- [ ] **T5.1**: Add `CREATE DATABASE cognee_cianfhoghlaim;` after the `langfuse / mlflow / litellm` block
- [ ] **T5.2**: Add `GRANT ALL PRIVILEGES ON DATABASE cognee_cianfhoghlaim TO lakekeeper;` in the grant block
- [ ] **T5.3**: Verify total = 13 databases (6 ducklake + dagster_local + olake_state + nimtable + langfuse + mlflow + litellm + cognee_cianfhoghlaim)

## Phase 6: Pangolin blueprint.yaml — add 4 private resources (1 file modified)

- [ ] **T6.1**: Add `cognee` private-resource (port 8000, `cognee.cianfhoghlaim.ie`)
- [ ] **T6.2**: Add `graphiti` private-resource (port 8000, `graphiti.cianfhoghlaim.ie`)
- [ ] **T6.3**: Add `falkordb-browser` private-resource (port 3000, `falkordb.cianfhoghlaim.ie`)
- [ ] **T6.4**: Add `memgraph-lab` private-resource (port 3000, `memgraph.cianfhoghlaim.ie`)

## Phase 7: Pangolin.yaml — single multi-route declaration (1 file modified)

- [ ] **T7.1**: Update `bonneagar/stacks/lakehouse/pangolin.yaml` to add the 4 new routes (in addition to the existing lakehouse → lakekeeper:8181 route)

## Phase 8: Deprecation banners (5 files modified — banner only)

- [ ] **T8.1**: Add the deprecation banner to `bonneagar/stacks/cognee/compose.yaml` (at the top, after the comment header)
- [ ] **T8.2**: Add the deprecation banner to `bonneagar/stacks/graphiti/compose.yaml`
- [ ] **T8.3**: Add the deprecation banner to `bonneagar/stacks/falkordb/compose.yaml`
- [ ] **T8.4**: Add the deprecation banner to `bonneagar/stacks/memgraph/compose.yaml`
- [ ] **T8.5**: Add the deprecation banner to `bonneagar/stacks/lancedb/compose.yaml`

## Phase 9: Lakehouse preflight extension (1 file modified)

- [ ] **T9.1**: Add the 4 new endpoints to `REQUIRED_ENDPOINTS` in `scripts/lakehouse_preflight.py` (cognee :8000, graphiti :8000, falkordb :6379 TCP, memgraph :7687 TCP)
- [ ] **T9.2**: Add `cognee_cianfhoghlaim` to `EXPECTED_DATABASES` (now 13 entries)
- [ ] **T9.3**: Remove the 4 endpoints from `OPTIONAL_COGNIFY` (they're now required)
- [ ] **T9.4**: Update the docstring + the section comments to reflect "5+4=9 endpoints + 13 databases"

## Phase 10: Komodo resource-sync trim (1 file modified)

- [ ] **T10.1**: Remove the 5 graph DB stack TOML references from `bonneagar/komodo/resource-syncs/bunchloch.toml` resource_path
- [ ] **T10.2**: Update the header comment to reflect the new resource_path (only `bunchloch-analytics.toml` etc + `lakehouse-bunchloch`)

## Phase 11: Bring-up shell entry-point (1 file NEW)

- [ ] **T11.1**: Create `scripts/lakehouse_unified_up.sh` — the canonical bring-up shell script (executable +0700)
- [ ] **T11.2**: Create `scripts/lakehouse_unified_down.sh` — the canonical teardown shell script (executable +0700)

## Phase 12: mise.toml task aliases (1 file modified)

- [ ] **T12.1**: Add `[tasks."lakehouse:up"]` → `bash scripts/lakehouse_unified_up.sh`
- [ ] **T12.2**: Add `[tasks."lakehouse:down"]` → `bash scripts/lakehouse_unified_down.sh`
- [ ] **T12.3**: Add `[tasks."lakehouse:preflight:unified"]` → `python3 scripts/lakehouse_preflight.py --strict-cognify`

## Phase 13: Updated README (1 file modified)

- [ ] **T13.1**: Update `bonneagar/stacks/lakehouse/README.md` to document the 16-service unified stack + the 5 deprecation banners + the 1 canonical bring-up command
- [ ] **T13.2**: Add a "Unified Graph DB Backends" section documenting the 5 new services (cognee + graphiti + falkordb + memgraph + memgraph-lab)

## Phase 14: Quality gates (4 tasks)

- [ ] **T14.1**: Run `openspec validate 2026-08-15-lakehouse-unified-data-plane-v1 --strict` and verify it passes
- [ ] **T14.2**: Run `mise run cic:stack-doctor` and verify the 5 deprecated stacks still validate (banner doesn't break the GOLD_STANDARD check)
- [ ] **T14.3**: Run `mise run lint:skills` and verify 157 skills still pass
- [ ] **T14.4**: Run `mise run lint:drift-docs` and verify no new AGENTS.md number drift

## Phase 15: Commit + push + archive (3 tasks)

- [ ] **T15.1**: Commit the changes (stage ONLY the lakehouse-related files + the deprecation banners + the openspec change; do NOT touch the 20 unrelated working-tree changes from earlier sessions)
- [ ] **T15.2**: Push to `origin/token-plan-lc-pipeline-2026-08`
- [ ] **T15.3**: Open a follow-up issue to delete the 5 deprecated stacks in `2026-XX-XX-delete-deprecated-graph-db-stacks`

## Total: 32 tasks across 15 phases

Estimated effort: ~2 hours for the file edits + ~30 minutes for openspec validate + CI gates.