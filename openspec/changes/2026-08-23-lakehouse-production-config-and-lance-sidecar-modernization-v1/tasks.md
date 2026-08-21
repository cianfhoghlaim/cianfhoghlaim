# Tasks: 2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1/proposal.md`
- [ ] **T1.2**: Create `openspec/changes/2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/changes/2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1/specs/infrastructure-stacks/spec.md` (4 ADDED Requirements + 1 MODIFIED Requirement)

## Phase 2: Validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1 --strict` and verify it passes

## Phase 3: Lance Namespace sidecar rewrite (3 tasks)

- [ ] **T3.1**: Update `bonneagar/stacks/lakehouse/lance-sidecar/requirements.txt`:
  - Replace `urllib3` with `lance-namespace>=0.11.1` + `lance-namespace-urllib3-client>=0.11.1` + `lance-namespace-impls[iceberg]>=0.4.1` + `pylance>=7.0.0` + `pyarrow>=15.0.0`
  - Keep `fastapi` + `pydantic` + `uvicorn`
- [ ] **T3.2**: Rewrite `bonneagar/stacks/lakehouse/lance-sidecar/main.py` (567 → ~150 LOC):
  - Import `from lance_namespace_impls.iceberg import IcebergNamespace`
  - Initialize `IcebergNamespace(endpoint=..., auth_token=..., root=..., ...)` at app startup
  - Map FastAPI endpoint handlers to `ns.list_namespaces()`, `ns.create_namespace()`, etc.
  - Keep the same REST API surface (for backward compat with cogeen + graphiti + lancedb-viewer + 47 CocoIndex Apps)
  - Keep `table_type=lance` property hack via `request.properties` updates
- [ ] **T3.3**: Verify `python -c "import lance_namespace_impls.iceberg"` succeeds (sanity check the deps)

## Phase 4: Lance sidecar image publishing (2 tasks)

- [ ] **T4.1**: Create `.github/workflows/build-lance-namespace-sidecar.yml`:
  - Trigger on PR merge to main with paths under `bonneagar/stacks/lakehouse/lance-sidecar/`
  - Build with `docker buildx` + push to `ghcr.io/cianfhoghlaim/lance-namespace-sidecar:v0.3.0`
  - Use `secrets.GITHUB_TOKEN` for registry auth
- [ ] **T4.2**: Update `bonneagar/stacks/lakehouse/compose.yaml`:
  - Change `lance-namespace.image` from `lakehouse-lance-namespace:latest` (built) to `ghcr.io/cianfhoghlaim/lance-namespace-sidecar:v0.3.0` (pinned)
  - Add `pull_policy: if_not_present` for local dev fallback to build
  - Keep `build:` context as alternative for local dev (the workflow is gated by the operator's choice)

## Phase 5: Lakekeeper production env vars (2 tasks)

- [ ] **T5.1**: Update `bonneagar/stacks/lakehouse/compose.yaml` — add to lakekeeper environment:
  - `LAKEKEEPER__PG_HOST_R: ${LAKEKEEPER__PG_HOST_R:-postgres}` (read replica — defaults to single postgres)
  - `LAKEKEEPER__PG_HOST_W: ${LAKEKEEPER__PG_HOST_W:-postgres}`
  - `LAKEKEEPER__METRICS__PORT: ${LAKEKEEPER_METRICS_PORT:-9100}`
  - `LAKEKEEPER__PAGINATION_SIZE_DEFAULT: ${LAKEKEEPER_PAGINATION_SIZE_DEFAULT:-1024}`
  - `LAKEKEEPER__PAGINATION_SIZE_MAX: ${LAKEKEEPER_PAGINATION_SIZE_MAX:-2048}`
  - `LAKEKEEPER__USE_X_FORWARDED_HEADERS: "true"`
  - `LAKEKEEPER__CACHE__STC__ENABLED: "true"`
  - `LAKEKEEPER__CACHE__WAREHOUSE__ENABLED: "true"`
  - `LAKEKEEPER__CACHE__WAREHOUSE__CAPACITY: "1000"`
- [ ] **T5.2**: Update `bonneagar/stacks/lakehouse/secrets.env` — add Infisical URI refs for the new env vars:
  - `LAKEKEEPER__PG_HOST_R=infisical://dev-baile/lakehouse/pg_host_r` (optional)
  - `LAKEKEEPER__PG_HOST_W=infisical://dev-baile/lakehouse/pg_host_w` (optional)
  - Document that production OpenID/OpenFGA env vars are off by default (operator opt-in)

## Phase 6: Cognee Dataset Database Handlers (1 task)

- [ ] **T6.1**: Update `bonneagar/stacks/lakehouse/compose.yaml` — Cognee service environment:
  - REMOVE `USE_UNIFIED_PROVIDER: pghybrid`
  - KEEP `DB_PROVIDER: postgres` + `VECTOR_DB_PROVIDER: pgvector` + `GRAPH_DATABASE_PROVIDER: postgres`
  - ADD `LANCEDB_PROVIDER: lancedb` (uses Lance Namespace adapter)

## Phase 7: FalkorDB canonical env vars (1 task)

- [ ] **T7.1**: Update `bonneagar/stacks/lakehouse/compose.yaml` — falkordb service:
  - Change `command:` from inline args to `["falkordb"]`
  - Add env vars:
    - `REDIS_ARGS: "--requirepass ${FALKORDB_PASSWORD:?...} --appendonly yes --appendfsync everysec --maxmemory 2gb --maxmemory-policy allkeys-lru"`
    - `FALKORDB_ARGS: "THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000 TIMEOUT_DEFAULT 30000 QUERY_MEM_CAPACITY 104857600"`
    - Keep `BROWSER: "1"`

## Phase 8: Cognee PostgreSQL user isolation (2 tasks)

- [ ] **T8.1**: Update `bonneagar/stacks/lakehouse/init-db.sql` — after `CREATE DATABASE cognee_cianfhoghlaim`:
  - `CREATE USER cognee WITH PASSWORD '${COGNEE_POSTGRES_PASSWORD}';` (substituted by compose at runtime)
  - `GRANT ALL PRIVILEGES ON DATABASE cognee_cianfhoghlaim TO cognee;`
- [ ] **T8.2**: Update `bonneagar/stacks/lakehouse/compose.yaml` — Cognee service environment:
  - `COGNEE_POSTGRES_USER: ${COGNEE_POSTGRES_USER:-cognee}` (was `${POSTGRES_USER:-lakekeeper}`)
  - `COGNEE_POSTGRES_PASSWORD: ${COGNEE_POSTGRES_PASSWORD:?COGNEE_POSTGRES_PASSWORD must be set via Locket/Infisical}` (was `${POSTGRES_PASSWORD:?...}`)
  - Add `COGNEE_POSTGRES_USER=infisical://dev-baile/lakehouse/cognee_postgres_user` to `secrets.env`

## Phase 9: OpenTelemetry collector stub (1 task)

- [ ] **T9.1**: Update `bonneagar/stacks/lakehouse/compose.yaml` — add OTel collector stub (optional profile `otel`):
  - Service: `otel-collector` — `image: otel/opentelemetry-collector-contrib:0.110.0`
  - Config-only (no collector.yaml yet — that's PR #4)
  - Wired by each service via `OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317`
  - PR #4 will add the collector config + Langfuse/Logfire exporters

## Phase 10: Quality gates (4 tasks)

- [ ] **T10.1**: Run `openspec validate 2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1 --strict` and verify it passes
- [ ] **T10.2**: Run `docker compose -f compose.yaml -f sidecar.yaml config --quiet` (in `bonneagar/stacks/lakehouse/`) and verify it passes
- [ ] **T10.3**: Run `mise run cic:stack-doctor` and verify no new criticals
- [ ] **T10.4**: Run `mise run lint:skills`, `mise run lint:drift-docs`, `mise run lint:registry` and verify all green

## Phase 11: Commit + push (2 tasks)

- [ ] **T11.1**: Stage only the PR #2 files:
  - `openspec/changes/2026-08-23-.../{proposal.md, tasks.md, specs/infrastructure-stacks/spec.md}`
  - `bonneagar/stacks/lakehouse/{compose.yaml, init-db.sql, secrets.env, lance-sidecar/requirements.txt, lance-sidecar/main.py}`
  - `.github/workflows/build-lance-namespace-sidecar.yml`
  - DO NOT stage: 15+ pre-existing uncommitted changes from earlier sessions
- [ ] **T11.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`

## Total: 18 tasks across 11 phases

Estimated effort: ~3-4 hours of file edits + ~30 minutes for openspec validate + CI gates.