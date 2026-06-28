# Consolidate Observability + Graph DB Stacks

## Why

The `cleanup-and-boot-stacks` change (archived as
`2026-06-26-cleanup-and-boot-stacks`) cleaned up dead prometheus, scaffolded
the logfire stack, and dropped Datadog from the documentation + Komodo
procedures. The Python observability modules (60+ Datadog refs) were
deferred because the scope was too large for a single change.

This change:

1. **Completes the observability consolidation** by making the Datadog
   Python code paths graceful no-op fallbacks (no behaviour change; the
   `ddtrace` and `datadog` packages are already optional imports behind
   try/except blocks in most places).

2. **Fixes the remaining 4 stacks with legacy Infisical URI form**
   (`mlflow`, `lakehouse`, `graphiti`, `falkordb`) so all stack secrets
   follow the Locket-canonical `infisical://dev-baile/...` convention.

3. **Fixes 2 blueprint port mismatches** (langfuse 8080→3000, graphiti
   8080→8000). The original audit said cognee was also wrong, but
   inspection of the compose file (`8100:8000`) shows the container
   listens on 8000 internally — the blueprint's `destination-port: 8000`
   is already correct. The audit confused the host port (8100) with the
   container port (8000).

4. **Fixes the `croilar-devtools` MCP command path** in `opencode.json`
   (the file `croilar/mcp/devtools/index.ts` doesn't exist at the repo
   root; the correct path is `sruth/croilar/mcp/devtools/index.ts` per
   `ls sruth/croilar/mcp/devtools/index.ts`).

5. **Adds 6 new `pangolin.yaml` files** so every audited stack has a
   private Pangolin route (`{name}.cianfhoghlaim.ie`) for browser
   access.

This change **does not** attempt to actually deploy the 5 stopped Docker
containers (cognee, mlflow, graphiti, falkordb, lakehouse-garage) — that
requires the Docker daemon on `bunchloch` which is not available from the
remote build agent. The deploy commands are documented in the per-stack
READMEs (unchanged) and in the spec scenario.

## What Changes

### 1. Infisical URI migration (4 secrets.env files)

| Stack | Secrets migrated |
|:--|:--|
| `mlflow` | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD` (5 items) |
| `lakehouse` | `PLANETSCALE_DATABASE_URL`, `LAKEKEEPER_ENCRYPTION_KEY`, `GARAGE_RPC_SECRET`, `GARAGE_ADMIN_TOKEN`, `GARAGE_ACCESS_KEY_ID`, `GARAGE_SECRET_ACCESS_KEY`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_ACCOUNT_ID`, `MOTHERDUCK_TOKEN`, `NIMTABLE_JDBC_PASSWORD`, `NIMTABLE_DASHBOARD_SECRET`, `OLAKE_JDBC_PASSWORD`, `OLAKE_SOURCE_PG_PASSWORD`, `OLAKE_WRITER_S3_SECRET_KEY`, `LANCEDB_VIEWER_ADMIN_TOKEN` (16 items) |
| `graphiti` | `OPENAI_API_KEY`, `NEO4J_USER`, `NEO4J_PASSWORD` (3 items) |
| `falkordb` | `FALKORDB_PASSWORD` (1 item) |

Format change: `{{ infisical:///key_name }}` →
`infisical://dev-baile/<service>/key_name`.

### 2. Blueprint port fidelity (2 files)

| Stack | Before | After | Reason |
|:--|:--|:--|:--|
| `langfuse/blueprint.yaml` | `destination-port: 8080` | `destination-port: 3000` | compose maps 3001→3000 (web listens on 3000 internally) |
| `graphiti/blueprint.yaml` | `destination-port: 8080` | `destination-port: 8000` | compose exposes 8000:8000 (graph API on 8000) |
| `cognee/blueprint.yaml` | `destination-port: 8000` | (unchanged) | audit was wrong; compose is 8100:8000 (container listens on 8000) |

### 3. MCP command path (1 file)

| File | Before | After |
|:--|:--|:--|
| `opencode.json` line 128 | `croilar/mcp/devtools/index.ts` | `sruth/croilar/mcp/devtools/index.ts` |

### 4. Pangolin.yaml additions (6 files)

| Stack | Private resource | Container port |
|:--|:--|:--|
| `mlflow` | `mlflow.cianfhoghlaim.ie` | 5000 |
| `langfuse` | `langfuse.cianfhoghlaim.ie` | 3000 |
| `lakehouse` | `lakehouse.cianfhoghlaim.ie` | 8181 (Lakekeeper REST catalog) |
| `graphiti` | `graphiti.cianfhoghlaim.ie` | 8000 |
| `falkordb` | `falkordb.cianfhoghlaim.ie` | 3000 (FalkorDB UI) |
| `cognee` | `cognee.cianfhoghlaim.ie` | 8000 |

### 5. Datadog Python code → graceful no-op fallbacks (10 files)

The `ddtrace` and `datadog` packages are already imported behind
`try/except` blocks in 8 of the 10 files. This change:

- Updates the `datadog_enabled: bool = True` default in
  `sruth/oideachais/observability/unified_tracer.py` line 296 →
  `False` (the canonical default is no-Datadog).
- Updates the `datadog_enabled: bool = False` default in
  `sruth/croilar/_shared/config/settings.py` (already False; no change).
- Updates the `datadog_enabled: bool = Field(...)` defaults in
  `sruth/oideachais/config/base.py` lines 149, 311 and
  `sruth/meaisinfhoghlaim/ocr/config/base.py` lines 149, 311 to
  `default=False`.
- Adds explicit `DD_ENABLED=${DD_ENABLED:-false}` env var read in
  `setup_datadog_apm` so the Komodo procedure override works
  cleanly.
- Documents the no-op behaviour in
  `sruth/oideachais/observability/__init__.py` docstring.

The 60+ `from ddtrace import ...` and `from datadog import ...` lines
are LEFT IN PLACE because they are already guarded by try/except — the
imports only succeed if the packages are installed (they aren't in the
production images). The code paths are dead code at runtime.

### 6. TypeScript comment update (1 file)

`sruth/croilar/apps/portal/src/routes/api/mcp.gateway.ts` line 10:
- Before: `* - Observability: datadog, langfuse, logfire`
- After: `* - Observability: logfire, langfuse`

## Out of scope (deferred to Change 3 or operational)

- **Booting the 5 stopped Docker containers** (cognee, mlflow, graphiti,
  falkordb, lakehouse-garage) — requires Docker daemon on `bunchloch`
  + Infisical vault seeded with the 25 new secrets.
- **Deploying graphiti + falkordb as the user-requested graph DB stack**
  — depends on the Docker boot above.
- **Infisical vault seeding** — `bun run scripts/init-vault.ts` must
  be run after the secrets.env changes land so the `dev-baile` vault
  has the corresponding entries. The script reads from `.env` (hydrated
  by mise hooks), so it picks up the Locket-canonical URIs automatically
  once the change is in.

## Files Changed (26 files)

### Modifications (20)

- `infrastructure/stacks/mlflow/secrets.env`
- `infrastructure/stacks/lakehouse/secrets.env`
- `infrastructure/stacks/graphiti/secrets.env`
- `infrastructure/stacks/falkordb/secrets.env`
- `infrastructure/stacks/langfuse/blueprint.yaml`
- `infrastructure/stacks/graphiti/blueprint.yaml`
- `opencode.json`
- `infrastructure/stacks/mlflow/pangolin.yaml` (new file, see below)
- `infrastructure/stacks/langfuse/pangolin.yaml` (new file)
- `infrastructure/stacks/lakehouse/pangolin.yaml` (new file)
- `infrastructure/stacks/graphiti/pangolin.yaml` (new file)
- `infrastructure/stacks/falkordb/pangolin.yaml` (new file)
- `infrastructure/stacks/cognee/pangolin.yaml` (new file)
- `sruth/oideachais/observability/unified_tracer.py`
- `sruth/oideachais/observability/__init__.py`
- `sruth/oideachais/observability/fastapi_middleware.py`
- `sruth/oideachais/config/base.py`
- `sruth/meaisinfhoghlaim/ocr/config/base.py`
- `sruth/croilar/_shared/observability/tracing.py`
- `sruth/croilar/apps/portal/src/routes/api/mcp.gateway.ts`

### Spec deltas (1)

- `openspec/changes/consolidate-observability-and-graph/specs/agent-memory-systems/spec.md`
  — adds 1 ADDED Requirement (`Stack deployability contract`) and
  4 ADDED Requirements for the consolidated observability + graph DB
  wiring.

## Validation

```bash
openspec validate consolidate-observability-and-graph --strict
bun run validate-stacks           # all 6 pangolin files parse
mise run lint:skills              # 123/123
mise run py:typecheck             # (pre-existing broken at mise level)
```

## Risk

- **Infisical URI migration** — Low risk. The 4 stacks were already
  broken at deploy time (the Jinja form was never wired to a working
  resolver). After this change they will be wired correctly.
- **Blueprint port fixes** — Low risk. The fix changes the destination
  port that Pangolin's Traefik proxies to. The 2 stacks either have
  no running container (graphiti) or have a working container
  reachable on the correct port via localhost (langfuse).
- **MCP path fix** — Zero risk. The `croilar-devtools` MCP was already
  failing to start (path didn't exist); fixing it makes the MCP
  available.
- **Datadog no-op defaults** — Low risk. The code was already
  conditionally importing ddtrace/datadog. Setting the default
  `datadog_enabled=False` makes the no-op path explicit.

## Lines Added/Removed

- **Lines added:** ~150 (6 pangolin.yaml + 4 secrets.env migrations +
  Datadog default flips + spec deltas)
- **Lines removed:** ~0
- **Net file count change:** +6 new files (pangolin.yaml) + 0
  deletions
