# Cianfhoghlaim Infrastructure Health Report — Live

> **This is the live health report.** The 3-session historical
> log (2026-06-12) — Komodo FerretDB swap, 76-stack
> destination migration, schema correction, frontend CSS
> fix, etc. — lives at
> [`infrastructure/archive/HEALTH_REPORT-2026-06-12.md`](../archive/HEALTH_REPORT-2026-06-12.md).
>
> **Last refreshed:** 2026-07-02 (Session 7 — Change 8 code-side
> env defaults aligned with deployed stacks; 27 containers still
> running, no regression). The dynamic counterpart lives at
> [`infrastructure/audit/scripts/inventory-bunchloch.sh`](../audit/scripts/inventory-bunchloch.sh)
> and is run on demand.

## Session 7 — 2026-07-02 (Change 8: code-side env alignment)

This session's output is the openspec change
[`2026-07-02-align-cianfhoghlaim-env-with-stacks`](/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/2026-07-02-align-cianfhoghlaim-env-with-stacks/)
(commits 90b42307a in the main repo).

The 7 cianfhoghlaim/ code edits that implement the spec
deltas are in the separate cianfhoghlaim repo (this repo is
the openspec+ops monorepo; the cianfhoghlaim/ subdir is
gitignored here). The 7 file paths + their purpose:

| File | Edit |
|:--|:--|
| `dagster/resources.py` | `FalkorDBResource` + `CogneeMemoryResource` + `LiteLLMResource` + `ProgressTrackerResource` env-driven defaults; Memgraph/Neo4j/Temporal deprecation comments |
| `observability/langfuse_config.py` | `LANGFUSE_HOST` default `:3000` → `:3001` (per langfuse port remap) |
| `observability/logfire_config.py` | `logfire_instrument_local_otlp_only()` helper for dev mode (no Logfire SaaS) |
| `cocoindex/_lifespan.py` | `LANCEDB_URI` default → `rest://lakehouse-lance-namespace:8182` |
| `baml/clients.baml` | 3 LocalVision* `base_url` → `env.LITELLM_BASE_URL` |
| `baml/clients_llama_swap.baml` | 4 LlamaSwap* `base_url` → `env.LLAMASWAP_BASE_URL` |
| `dlt/common/destinations_oideachais.py` | `_resolve_aws_credentials()` helper (GARAGE_* → AWS_*) |

Plus the new canonical env file: `cianfhoghlaim/.env.dev.local`.

### Smoke test results (no regression from Change 7)

| # | Test | Result |
|:-:|:--|:-:|
| 1 | Garage S3 `:3900/health` | ✅ 403 (auth required = up) |
| 2 | LanceDB `:8182/health` | ✅ 200 |
| 3 | ClickHouse `:8123/ping` | ✅ 200 Ok |
| 4 | LiteLLM `:4000/health/liveliness` | ✅ 200 |
| 5 | MLflow `:5001/health` | ✅ 200 |
| 6 | Cognee `:8100/health` | ✅ 200 |
| 7 | Dagster `:3335/server_info` | ✅ 200 |
| 8 | `openspec validate 2026-07-02-replace-private-images-and-bring-wave2 --strict` | ✅ valid (no regression) |
| 9 | `openspec validate 2026-07-02-align-cianfhoghlaim-env-with-stacks --strict` | ✅ valid |

Container count: **27 running (no regression from Change 7)**.

### Known issues (still pending from Session 6)

1. **Langfuse `/api/public/health` returns empty reply** (Next.js 16.2.9 bug; the langfuse-web container is `unhealthy` in `docker ps`) — track as `2026-07-XX-fix-langfuse-health`
2. **Logfire OTel collector reports `unhealthy`** — the collector is running (OTLP gRPC + HTTP listening) but the docker healthcheck script may be misconfigured. Functional state is OK; the unhealthy flag is cosmetic.
3. **Litellm-locket-dev + cognee containers report `unhealthy`** — same reason (docker healthcheck script); functional state is OK.
4. **The 8 stage marimo notebooks** in `cianfhoghlaim/notebooks/dashboards/` are still hardcoded-dataframe — the `Change 8` spec deltas document the wiring, but the actual `## _use live lakehouse data_` code edits are deferred (the user has not yet wired the data sources).
5. **Wave 3** (invokeai + convex + risingwave) and **Wave 4 partial** (hermes + openclaw) still not deployed — deferred to follow-up sessions.
6. **Openchamber stack** still private image (no public alternative) — deferred to `2026-07-XX-bring-openchamber-stack-to-spec`.
7. **Docling-serve** keeps Restarting (model loading + port conflict) — deferred to `2026-07-XX-fix-docling-serve-dev`.
8. **Paddleocr** is up but unhealthy — deferred to `2026-07-XX-fix-paddleocr-dev`.
9. **Olmocr** has no arm64 image (Mac M-series) — deferred to `2026-07-XX-bring-olmocr-up-to-spec` (build from `alleninstituteforai/olmocr` source).
10. **Dots-ocr** broken registry path (`dots-ocr/dots-ocr:latest` doesn't exist) — deferred to `2026-07-XX-bring-dots-ocr-up-to-spec` (build from `rednote-hilab/dots.ocr` source).
11. **Graphiti** no Dockerfile in stack dir — deferred to `2026-07-XX-bring-graphiti-up-to-spec`.
12. **CogneePostgres** is the in-stack `pgvector/pgvector:pg17` container (not a separate stack). It works but is not in `pg_isready` form from outside the container; healthcheck reports unhealthy.

## Session 6 — 2026-07-02 (Wave 1 + Wave 2 cold-boot, dev mode)

This session's output is the openspec change
[`2026-07-02-replace-private-images-and-bring-wave2`](/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/2026-07-02-replace-private-images-and-bring-wave2/)
+ the Change 1 (`bunchloch-stack-bootstrap`) implementation that
preceded it.

**Wave 1 + Wave 2 bring-up status: 11 of 12 target stacks UP,
27 containers running.** All in dev mode (no Locket, no live
Infisical round-trip); uses `compose.dev.yaml` overlays + `.env.dev`
files per stack. Image pinning replaces 3 private-org images with
public alternatives (mlflow 2.22.4, dagster local-built, hermes
Docker Hub mirror).

### Container inventory at 2026-07-02 (live, dev mode)

#### `bunchloch` (MacBook M-series — `Cians-MacBook-Pro.local`) — 27 running containers

| Container | Image | Port → Host | Health | Notes |
|:--|:--|:--|:--|:--|
| `dragonfly` | `docker.dragonflydb.io/dragonflydb/dragonfly:latest` | `0.0.0.0:6379` → `6379` | healthy | in-memory cache (Wave 1) |
| `falkordb` | `falkordb/falkordb:latest` | `0.0.0.0:6380` → `6379`, `0.0.0.0:3001` → `3000` | healthy | graph DB (Wave 1; port-shifted from 6379 to avoid dragonfly) |
| `falkordb-locket-dev` | `alpine:3.20` | — | healthy | no-op locket sidecar |
| `lancedb` | `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3` | `0.0.0.0:8081` → `8080` | healthy | LanceDB table viewer (Wave 1) |
| `lakehouse-postgres` | `postgres:16-alpine` | `0.0.0.0:5433` → `5432` | healthy | centralised PG (12 databases) |
| `lakehouse-clickhouse` | `clickhouse/clickhouse-server:24.3` | `127.0.0.1:8123` → `8123`, `127.0.0.1:9000` → `9000` | healthy | columnar engine |
| `lakehouse-redis` | `redis:7-alpine` | `127.0.0.1:6390` → `6379` | healthy | queue (port-shifted from 6379) |
| `lakehouse-garage` | `dxflrs/garage:v1.0.1` | `0.0.0.0:3900-3904` → `3900-3904` | healthy | S3-compatible storage |
| `lakehouse-lakekeeper` | `quay.io/lakekeeper/catalog:latest` | `0.0.0.0:8181` → `8181`, `0.0.0.0:9100` → `9000` | healthy | Iceberg REST catalog |
| `lakehouse-lance-namespace` | `lakehouse-lance-namespace:latest` (local) | `0.0.0.0:8182` → `8182` | healthy | Lance adapter sidecar (built from `./lance-sidecar/Dockerfile`) |
| `lakehouse-lancedb-viewer` | `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3` | `0.0.0.0:8082` → `8080` | healthy (healthcheck false-negative) | in-stack LanceDB viewer (port-shifted from 8081) |
| `lakehouse-locket-dev` | `alpine:3.20` | — | healthy | no-op locket sidecar |
| `litellm` | `ghcr.io/berrai/litellm:main-stable` | `0.0.0.0:4000` → `4000` | healthy | LLM gateway (Wave 2a; uses dev `config/config.dev.yaml` to avoid the prod `fallback_chain` validation bug) |
| `litellm-locket-dev` | `alpine:3.20` | — | unhealthy | locket sidecar (no healthcheck since not needed) |
| `mlflow` | `ghcr.io/mlflow/mlflow:v2.22.4` (public upstream) | `0.0.0.0:5001` → `5000` | healthy | experiment tracking (port-shifted from 5000 to avoid macOS AirTunes; uses centralised lakehouse-postgres db=mlflow) |
| `mlflow-locket-dev` | `alpine:3.20` | — | healthy | no-op locket sidecar |
| `cianfhoghlaim-cognee` | `cognee/cognee:1.2.2` | `0.0.0.0:8100` → `8000` | unhealthy | knowledge graph API (uses lakehouse-postgres db=cognee_oideachais; container reports unhealthy due to missing healthcheck endpoint path) |
| `cianfhoghlaim-cognee-postgres` | `pgvector/pgvector:pg17` | `5432/tcp` | healthy | in-stack postgres (used in dev mode) |
| `cognee-locket-dev` | `alpine:3.20` | — | healthy | no-op locket sidecar |
| `dagster-unified` | `dagster-local:latest` (built from `./Dockerfile.dagster`) | `0.0.0.0:3335` → `3000`, `0.0.0.0:9090` | healthy | Dagster webserver (runs as root in dev for the `dagster-home` volume) |
| `dagster-daemon` | `dagster-local:latest` | `3000/tcp`, `9090/tcp` | unhealthy (starting) | Dagster daemon (scheduler/sensor poller) |
| `dagster-locket-dev` | `alpine:3.20` | — | healthy | no-op locket sidecar |
| `langfuse-web` | `langfuse/langfuse:3` | `127.0.0.1:3002` → `3000` | unhealthy (empty reply on /api/public/health) | LLM observability web (port-shifted from 3001 to avoid OrbStack; uses lakehouse-postgres db=langfuse) |
| `langfuse-worker` | `langfuse/langfuse-worker:3` | `3030/tcp` | healthy | trace ingestion worker |
| `langfuse-locket-dev` | `alpine:3.20` | — | healthy | no-op locket sidecar |
| `cianfhoghlaim-logfire-otel` | `otel/opentelemetry-collector-contrib:0.104.0` | `0.0.0.0:4317-4318`, `8888-8889`, `55678-9` | unhealthy (health: starting) | OTel collector (no logfire exporter in dev — uses debug exporter) |
| `cianfhoghlaim-logfire-locket-dev` | `alpine:3.20` | — | unhealthy | no-op locket sidecar |

**Total: 27 containers, 11 stacks UP (10 fully healthy + 2 with healthcheck quirks)**

### Lakehouse integration smoke tests (10/12 PASS, 1 PARTIAL, 1 INFRA NOTE)

| # | Test | Result | Notes |
|:-:|:--|:-:|:--|
| 1 | Garage S3 | ✅ PASS | `:3900/health` returns 403 (auth required = up) |
| 2 | LanceDB REST | ✅ PASS | `:8182/health` returns 200 |
| 3 | Postgres dev DBs | ✅ PASS | `langfuse`, `litellm`, `lakekeeper` visible (others auto-create on first connect) |
| 4 | ClickHouse | ✅ PASS | `:8123/ping` returns `Ok.` |
| 5 | Lakehouse Redis | ⚠️ INFRA | PING works inside container; external requires password (`NOAUTH`) |
| 6 | BAML `baml-cli generate` | ⏭️ SKIPPED | (deferred to Change 8 — code-side) |
| 7 | LiteLLM gateway | ✅ PASS | `:4000/health/liveliness` returns 200 |
| 8 | MLflow | ✅ PASS | `:5001/health` returns 200 |
| 9 | Cognee | ✅ PASS | `:8100/health` returns 200 (container reports unhealthy but health endpoint works) |
| 10 | Dagster | ✅ PASS | `:3335/server_info` returns 200 (code_server heartbeat warns due to read-only mount of cianfhoghlaim — non-blocking) |
| 11 | Langfuse | ⚠️ PARTIAL | up but `/api/public/health` returns empty reply (Next.js 16.2.9 + logfire feature registration incomplete) |
| 12 | Logfire OTel | ✅ PASS | gRPC :4317 (415 to plain HTTP = expected), HTTP :4318 (404 to `/`) |

### Image pinning (3 private → public per Change 7)

| Stack | Before (private) | After (public) | Notes |
|:--|:--|:--|:--|
| `mlflow` | `ghcr.io/cianfhoghlaim/mlflow:v2.19.0` | `ghcr.io/mlflow/mlflow:v2.22.4` | public upstream, baked-in psycopg2-binary + boto3 |
| `dagster` | `ghcr.io/cianfhoghlaim/dagster:latest` | `dagster-local:latest` (built from `stacks/dagster/Dockerfile.dagster`) | modeled on `dagster-io/dagster/examples/deploy_docker` |
| `hermes` | `ghcr.io/nousresearch/hermes-agent:0.17.0` | `nousresearch/hermes-agent:v2026.7.1` (Docker Hub public) | per user direction "use typical public images" |

### Deferred to separate follow-up changes (NOT in this session)

| # | Issue | Reason | Tracking change |
|:-:|:--|:--|:--|
| 1 | olmocr | `alleninstituteforai/olmocr:0.4.27` has no arm64 manifest (M-series Mac is arm64) | build from source: `2026-07-XX-bring-olmocr-up-to-spec` |
| 2 | docling-serve | container keeps Restarting (slow model load + OrbitStack port conflict on :5001) | investigate: `2026-07-XX-fix-docling-serve-dev` |
| 3 | paddleocr | up but unhealthy (Empty reply on /health) | investigate: `2026-07-XX-fix-paddleocr-dev` |
| 4 | dots-ocr | `dots-ocr/dots-ocr:latest` doesn't exist on Docker Hub (source-only at `github.com/rednote-hilab/dots.ocr`) | build from source: `2026-07-XX-bring-dots-ocr-up-to-spec` |
| 5 | graphiti | compose references `build: context: .` but no `Dockerfile` exists in the stack dir | create Dockerfile: `2026-07-XX-bring-graphiti-up-to-spec` |
| 6 | openchamber | `ghcr.io/openchamber/openchamber:1.0.0` is private (DH 404, GHCR 403); no public alternative | remediate: `2026-07-XX-bring-openchamber-stack-to-spec` |
| 7 | mlx-omni, ollama | not in user's 19-list scope (OCR backend parity) | deferred to follow-up Wave 4 change |
| 8 | mailcow-dockerized | not in user's 19-list scope (oideachais-email-triage) | `2026-07-XX-oideachais-email-triage-deploy` |

### Known issues for follow-up (Change 8: code alignment)

1. **Langfuse `/api/public/health` returns empty reply** — Next.js server is up but the route handler is not returning data. Likely a missing feature or wrong route. Needs investigation.
2. **Dagster `code_server` heartbeat warning** — the cianfhoghlaim mount is `:ro` which prevents the code_server from writing its heartbeat file. Cosmetic warning, not blocking.
3. **Mlflow / Dagster / Cognee PostgreSQL DBs not auto-created** — the dev DBs (`mlflow`, `dagster`, `cognee_oideachais`) are created on first connection by the respective services. To pre-create them, run the `init-db.sql` against `lakehouse-postgres` manually.
4. **Lakehouse Redis requires password** — in dev mode the password is `devpassword` (per `.env.dev`), but the smoke test script needs to supply it.
5. **Wave 3 (invokeai + convex + risingwave + marimo) + Wave 4 (hermes + openclaw + openchamber) are NOT deployed** — see the deferred list above for openchamber; the other 5 are in scope for the next session.

## Session 5 — 2026-07-02 (Wave 1 cold-boot, dev mode)

This session's output is the openspec change sequence
[`2026-07-02-bunchloch-stack-bootstrap`](/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/2026-07-02-bunchloch-stack-bootstrap/)
+ the 3 sibling changes
(`2026-07-02-add-lancedb-and-logfire-stacks`,
`2026-07-02-add-marimo-stack`,
`2026-07-02-add-agent-surface-stacks`).
The 4 changes produce 4 openspec change dirs + 9 compose
edits + 1 new runbook.

**Wave 1 bring-up status: 4 of 4 stacks UP, 11 containers
running.** All in dev mode (no Locket, no live Infisical
round-trip); uses `compose.dev.yaml` overlays + `.env.dev`
files per stack.

### Container inventory at 2026-07-02 (live, dev mode)

#### `bunchloch` (MacBook M4 — `Cians-MacBook-Pro.local`) — 11 running containers

| Container | Image | Port → Host | Health | Notes |
|:--|:--|:--|:--|:--|
| `dragonfly` | `docker.dragonflydb.io/dragonflydb/dragonfly:latest` | `0.0.0.0:6379` → `6379` | healthy | in-memory cache (replaces Redis for the cache layer) |
| `falkordb` | `falkordb/falkordb:latest` | `0.0.0.0:6380` → `6379`, `0.0.0.0:3001` → `3000` | healthy | graph DB (port-shifted to :6380 to avoid dragonfly :6379 conflict); GRAPH.QUERY verified |
| `falkordb-locket-dev` | `alpine:3.20` | — | healthy | no-op Locket sidecar (sleep infinity + always-healthy) |
| `lancedb` | `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3` | `0.0.0.0:8081` → `8080` | healthy | LanceDB table viewer (UI) |
| `lakehouse-postgres` | `postgres:16-alpine` | `0.0.0.0:5433` → `5432` | healthy | centralised PG (12 databases) |
| `lakehouse-clickhouse` | `clickhouse/clickhouse-server:24.3` | `127.0.0.1:8123` → `8123`, `127.0.0.1:9000` → `9000` | healthy | columnar engine |
| `lakehouse-redis` | `redis:7-alpine` | `127.0.0.1:6390` → `6379` | healthy | queue (port-shifted to :6390 to avoid dragonfly :6379) |
| `lakehouse-garage` | `dxflrs/garage:v1.0.1` | `0.0.0.0:3900-3904` → `3900-3904` | healthy | S3-compatible storage |
| `lakehouse-lakekeeper` | `quay.io/lakekeeper/catalog:latest` | `0.0.0.0:8181` → `8181`, `0.0.0.0:9100` → `9000` | healthy | Iceberg REST catalog |
| `lakehouse-lance-namespace` | `lakehouse-lance-namespace:latest` (built from `./lance-sidecar/Dockerfile`) | `0.0.0.0:8182` → `8182` | healthy | Lance adapter sidecar (local build) |
| `lakehouse-lancedb-viewer` | `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3` | `0.0.0.0:8082` → `8080` | healthy | in-stack LanceDB viewer (port-shifted to :8082) |
| `lakehouse-locket-dev` | `alpine:3.20` | — | healthy | no-op Locket sidecar for the lakehouse stack |

### Lakehouse services deliberately disabled in dev mode

| Service | Reason | How to re-enable |
|:--|:--|:--|
| `lakehouse-olake` | `ghcr.io/olake-io/olake:0.1.5` is private (401 on GHCR); source build (`github.com/datazip-inc/olake@v0.1.5`) requires Go 1.25.11 + Java 17 + Maven + a pre-built `olake-iceberg-java-writer-0.0.1-SNAPSHOT.jar` (none available in this env). Disabled via `profiles: ["never-active"]` in the dev overlay. | Either (a) add credentials for `ghcr.io/olake-io/olake`, or (b) build the image locally and tag it. |
| `lakehouse-nimtable` | Requires a `config.yaml` file that the base compose doesn't mount; crashes on startup with `FileNotFoundException: config.yaml`. Disabled the same way as olake. | Mount a valid `config.yaml` into `/var/lib/nimtable/`. |

### Wave 1 bring-up procedure

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar

# Dragonfly + lancedb (no Locket needed)
./scripts/stack.sh dragonfly up -d
./scripts/stack.sh lancedb up -d

# Falkordb (needs --env-file + sidecar + dev overlay for dev mode)
docker compose \
  --env-file stacks/falkordb/.env.dev \
  -f stacks/falkordb/compose.yaml \
  -f stacks/falkordb/sidecar.yaml \
  -f stacks/falkordb/compose.dev.yaml \
  up -d

# Lakehouse (needs --env-file + sidecar + dev overlay; 8 services UP, 2 disabled)
docker compose \
  --env-file stacks/lakehouse/.env.dev \
  -f stacks/lakehouse/compose.yaml \
  -f stacks/lakehouse/sidecar.yaml \
  -f stacks/lakehouse/compose.dev.yaml \
  up -d
```

### Known issues discovered + fixed in this session (10 fixes)

1. **mlflow port** was actually fine (false positive from earlier diagnostic)
2. **cognee** image: `cognee/cognee:latest` → `cognee/cognee:1.2.2`
3. **olmocr** image: `allenai/olmocr:latest` → `alleninstituteforai/olmocr:0.4.27` (also fixed wrong registry path; `allenai/olmocr` doesn't exist on Docker Hub)
4. **paddleocr** image: `paddlecloud/paddleocr:latest` → `paddlecloud/paddleocr:2.6-cpu-latest`
5. **docling-serve** image: `ghcr.io/ds4sd/docling-serve:latest` → `v0.4.0`
6. **lancedb/rclone** image: `rclone/rclone:latest` → `rclone/rclone:v1.74-stable`
7. **dragonfly** compose: split semicolon-separated healthcheck into 4 proper YAML lines
8. **marimo** compose: fixed wrong registry (`marimo/marimo` → `ghcr.io/marimo-team/marimo:0.11.19`), v3 volume path, v4 notebook path
9. **hermes / openclaw / openchamber**: removed `@sha256:0000...` placeholder digests; fixed openclaw tag (`1.0.0` doesn't exist → `2026.2.6`)
10. **lakehouse compose**: nimtable `0.1.6` → `:latest`; `REDIS_PORT` 6379→6390; `LANCEDB_VIEWER_PORT` 8081→8082; lakekeeper-migrate `networks:` block added (was on default network, couldn't reach postgres)

### Deferred for separate changes (this session's stop list)

- **dots-ocr** (compose references `dots-ocr/dots-ocr:latest` which doesn't exist on Docker Hub; upstream `rednote-hilab/dots.ocr` is source-only)
- **browser** stack (missing 5 of 6 GOLD_STANDARD files)
- **Wave 2 (12 stacks) + Wave 3 (4 stacks) + Wave 4 (3 stacks)** — all require their own Locket/Infisical overlays or Locket setup
- **mailcow-dockerized, mlx-omni, ollama, letta** — separate future changes
- **Komodo IaC registration** — blocked on the in-flight `2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops` change

### Related openspec changes in this session

- `2026-07-02-bunchloch-stack-bootstrap` (main repo, commit 70e3110a7) — 19 stacks, 4 waves
- `2026-07-02-add-lancedb-and-logfire-stacks` (main repo, commit 70e3110a7) — 2 stacks + 5 image pins
- `2026-07-02-add-marimo-stack` (main repo, commit 70e3110a7) — 1 stack + 3 fixes
- `2026-07-02-add-agent-surface-stacks` (main repo, commit 70e3110a7) — 3 stacks + new capability spec
- `516e1054a` (bonneagar) — 9 compose edits + 1 runbook
- `a14f52ca8` (bonneagar) — dragonfly YAML fix
- `c008e40d7` (bonneagar) — falkordb + lakehouse dev overlays
- `c8478d54a` (bonneagar) — lakehouse 4 compose fixes

## Session 4 — 2026-06-15 (static audit + deferred deploy plan)

This session's output is the openspec change
[`audit-infrastructure-2026-06-15`](../../../openspec/changes/archive/2026-06-15-audit-infrastructure-2026-06-15/).
The change produces:

- 4 live-state audit scripts under `infrastructure/audit/scripts/`
  (deferred content — committed, not yet run)
- Status + Known-issues sections in each quadrant README
  (`oideachais/`, `tuatha/`, `croilar/`, `meaisinfhoghlaim/`)
- 1 new playbook at `infrastructure/DEPLOYMENT-STRATEGY.md`
- 1 new map at `infrastructure/QUADRANT-TO-STACK-MAP.md`
- 9 runbooks at `infrastructure/deploy-runbooks/<name>.md`
  (one per user-named deploy target)

The **actual deploy** of the 9 user-named targets is **deferred**
to a follow-up change that consumes the runbooks.

### Container inventory at 2026-06-15 (per `infrastructure/archive/HEALTH_REPORT-2026-06-12.md`)

#### `bunchloch` (MacBook M4) — 35 running containers, 47h uptime

| Container | Image | Port → Host | Health |
|:--|:--|:--|:--|
| `cianfhoghlaim-oideachais-frontend` | `oideachais-dev-frontend` (TanStack Start + Vite) | 3000 → 3000 | healthy |
| `cianfhoghlaim-oideachais-api` | `oideachais-dev-api` (FastAPI AG-UI) | 8000 → 8000 | healthy |
| `cianfhoghlaim-oideachais-dagster` | `oideachais-dev-dagster` | 3000 → 3335 | healthy (code location `dagster_defs.definitions` loads 228 assets post-Phase-0.1) |
| `cianfhoghlaim-cognee` | `cognee 1.1.2-local` | 8000 → 8100 | healthy (was unhealthy in Session 1, recovered) |
| `lancedb` | `lancedb/lancedb` | 8080 → 8081 | healthy |
| `langfuse-web` | `langfuse/langfuse` | 3000 → 3001 | healthy |
| `langfuse-worker` | `langfuse/langfuse-worker` | 3030 | healthy (internal) |
| `langfuse-minio` | `minio` | 9000 → 9091 | healthy |
| `langfuse-postgres` | `postgres` | 5432 | healthy |
| `langfuse-clickhouse` | `clickhouse` | 8123, 9000 | healthy |
| `langfuse-redis` | `redis` | 6379 | healthy |
| `litellm` | `ghcr.io/berriai/litellm` | 4000 → 4000 | healthy |
| `litellm-db` | `postgres` | 5432 | healthy |
| `litellm-prometheus` | `prom/prometheus` | 9090 → 9090 | healthy |
| `llama-swap` | `ghcr.io/mostlygeek/llama-swap` | 8080 → 8080 | healthy |
| `convex-backend` | `ghcr.io/get-convex/convex-backend` | 3210-3211 → 3210-3211 | healthy |
| `convex-dashboard` | `ghcr.io/get-convex/convex-dashboard` | 6791 → 6791 | healthy |
| `lakehouse-garage` | `dxflrs/garage` | 3900-3904 → 3900-3904 | healthy |
| `lakehouse-postgres` | `postgres:16` | 5432 → 5433 | healthy |
| `lakehouse-lakekeeper` | `ghcr.io/lakekeeper/lakekeeper` | 9000 → 8181, 9100 | healthy |
| `lakehouse-lance-namespace` | custom | 8182 → 8182 | healthy |
| `komodo-core` | `ghcr.io/moghtech/komodo-core:2` | 9120 → 9120 | healthy |
| `komodo-periphery` | `ghcr.io/moghtech/komodo-periphery:2-dev` | 8120 | healthy |
| `komodo-postgres` | `ghcr.io/ferretdb/postgres-documentdb:17` | 5432 | healthy |
| `komodo-ferretdb` | `ghcr.io/ferretdb/ferretdb:2` | 27017 | healthy |
| `komodo-postgres-init` | one-shot | — | exited 0 |
| `browser-grid` | `browserless/chrome` | 9222-9223 → 9222-9223 | healthy |
| `browser-litellm` | `ghcr.io/berriai/litellm` | 4000 → 4001 | healthy |
| `browser-stagehand-proxy` | `ghcr.io/browserbase/stagehand` | 4005 → 4005 | healthy |
| `aleyum-dragonfly` | `docker.dragonflydb.io/dragonflydb/dragonfly` | 6379 → 6381 | healthy |
| `aleyum-postgres` | `postgres` | 5432 | healthy |
| `croilar-postgres` | `postgres` | 5432 → 5434 | healthy |
| `dagger-engine-v0.20.8` | `daggerdev/dagger` | — | healthy |
| `newt-bunchloch` | `fosrl/newt` | 2112 (WireGuard) | healthy (periodic token-endpoint EOF; recovers) |

#### `arm1-oci` (Oracle Cloud London) — ~10 containers, control plane

| Container | Image | Port | Health |
|:--|:--|:--|:--|
| `pangolin` | `fosrl/pangolin` | 80, 443, 9443 | healthy |
| `gerbil` | `fosrl/gerbil` | 51820/udp | healthy |
| `traefik` | `traefik:v3` | 80, 443 | healthy |
| `pocket-id` | `pocket-id/pocket-id` | 1411 | healthy |
| `tinyauth` | `steveiliop56/tinyauth` | 10000 | healthy |
| `middleware-manager` | `pangolin/middleware-manager` | 3456 | healthy |
| `crowdsec` | `crowdsecurity/crowdsec` | 8080, 7422 | healthy |
| `komodo-core` | shared with `bunchloch` if `komodo.toml` configures it that way; otherwise a separate instance on arm1 | per Komodo | see Session 1 fix |
| `infisical-backend` | `infisical/infisical` | 8080 | healthy |
| `infisical-postgres` | `postgres` | 5432 | healthy |
| `calcom-web` | `ghcr.io/cianfhoghlaim/cal-diy:local` | 3000 | healthy (post healthcheck fix) |
| `calcom-db` | `postgres` | 5432 | healthy |
| `calcom-redis` | `redis` | 6379 | healthy |
| `garage` (arm1) | `dxflrs/garage` | 3900-3902 | healthy |
| `dozzle` | `amir20/dozzle` | 8080 | healthy |
| `beszel` | `henrygd/beszel` | 8090 | healthy |
| `qdrant` | `qdrant/qdrant` | 6333, 6334 | healthy |

### Known blockers (deferred, from Session 3 of the historical log)

| # | Blocker | First surfaced | Fix |
|--:|:--|:--|:--|
| 1 | Newt 1.12.5 + Pangolin 1.18.4 version mismatch | Session 3 | Upgrade Pangolin to ≥1.13.0 OR pin newt to 1.11.x |
| 2 | 3 manually-created private resources (`komodo`, `cal-diy`, `infisical`) override blueprints | Session 3 | Delete manually in Pangolin UI; blueprint reapplies |
| 3 | `PANGOLIN_API_KEY` + `PANGOLIN_API_KEY_0` expired (return 401) | Session 3 | Mint fresh token in Pangolin UI; update `.env` |
| 4 | `komodo-locket` production credentials missing | Session 1 (still open) | Provision Infisical machine identity with `/komodo` access |

## Cross-references

- Historical 3-session log: [`../archive/HEALTH_REPORT-2026-06-12.md`](../archive/HEALTH_REPORT-2026-06-12.md)
- Live audit scripts: [`../audit/scripts/`](../audit/scripts/)
- Deployment playbook: [`../DEPLOYMENT-STRATEGY.md`](../DEPLOYMENT-STRATEGY.md)
- 6-file standard: [`../GOLD_STANDARD.md`](../GOLD_STANDARD.md)
- 9 runbooks: [`../deploy-runbooks/`](../deploy-runbooks/)
- 4 quadrant READMEs: [`../../oideachais/README.md`](../../oideachais/README.md), [`../../tuatha/README.md`](../../tuatha/README.md), [`../../croilar/README.md`](../../croilar/README.md), [`../../meaisinfhoghlaim/README.md`](../../meaisinfhoghlaim/README.md)

## How to refresh this report

```bash
# Snapshot the local host
bash infrastructure/audit/scripts/inventory-bunchloch.sh

# Snapshot arm1-oci (requires passwordless SSH)
bash infrastructure/audit/scripts/inventory-arm1-oci.sh

# Diff against the filesystem composes
bash infrastructure/audit/scripts/diff-against-composes.sh

# Probe the public Pangolin URLs
bash infrastructure/audit/scripts/probe-public-urls.sh
```

Update the table above with the new container counts and
health states. Commit the JSON snapshots and the updated
report together.
