# Tasks

## Phase 1 — File authoring (30 min)

> **Status (2026-07-08, pick-3-image-replacement):** tasks 1.1-1.5,
> 1.8, 1.9 are now complete. The remaining Phase 1 tasks
> (1.6-1.7, 1.10-1.15, 1.21) and Phases 3-9 are deferred — they
> belong to separate follow-up changes tracked in this change's
> `proposal.md` §"Open follow-up issues".

- [x] 1.1 Edit `bonneagar/stacks/mlflow/compose.yaml`: `image: ghcr.io/cianfhoghlaim/mlflow:v2.19.0` → `image: ghcr.io/mlflow/mlflow:v3.12.0` (landed via the 2026-07-06 upgrade-4-stacks-with-infisical change; pin was further bumped from v2.22.4 to v3.12.0 in that change)
- [x] 1.2 Edit `bonneagar/stacks/mlflow/Dockerfile.mlflow`: `FROM ghcr.io/mlflow/mlflow:v2.22.4` → `FROM ghcr.io/mlflow/mlflow:v3.12.0` (commit 93b7f8d6a on `pick-3-image-replacement`)
- [x] 1.3 Edit `bonneagar/stacks/dagster/compose.yaml` (2 places): `image: ghcr.io/cianfhoghlaim/dagster:latest` → `image: dagster-local:latest` (landed in the 2026-07-02 cutover)
- [x] 1.4 Edit `bonneagar/stacks/hermes/compose.yaml`: `image: ghcr.io/nousresearch/hermes-agent:0.17.0` → `image: nousresearch/hermes-agent:v2026.7.1` (landed in the 2026-07-02 cutover)
- [x] 1.5 Create `bonneagar/stacks/dagster/Dockerfile.dagster` (landed in the 2026-07-03 infrastructure-foundation change; multi-arch support added 2026-07-08 in commit 93b7f8d6a)
- [x] 1.6 Create `bonneagar/stacks/dagster/.env.dev` — already exists (pre-pick-3)
- [x] 1.7 Create `bonneagar/stacks/dagster/compose.dev.yaml` — already exists (pre-pick-3)
- [x] 1.8 Create `bonneagar/stacks/mlflow/.env.dev` — already exists (pre-pick-3)
- [x] 1.9 Create `bonneagar/stacks/mlflow/compose.dev.yaml` — already exists (pre-pick-3)
- [ ] 1.10 Create `bonneagar/stacks/cognee/.env.dev` — DEFERRED (separate change)
- [ ] 1.11 Create `bonneagar/stacks/cognee/compose.dev.yaml` — DEFERRED
- [ ] 1.12 Create `bonneagar/stacks/langfuse/.env.dev` — DEFERRED
- [ ] 1.13 Create `bonneagar/stacks/langfuse/compose.dev.yaml` — DEFERRED
- [ ] 1.14 Create `bonneagar/stacks/marimo/.env.dev` — DEFERRED
- [ ] 1.15 Create `bonneagar/stacks/marimo/compose.dev.yaml` — DEFERRED
- [x] 1.16 Write `openspec/changes/2026-07-02-replace-private-images-and-bring-wave2/proposal.md` — exists at the absorbed path
- [x] 1.17 Write `openspec/changes/2026-07-02-replace-private-images-and-bring-wave2/tasks.md` (this file) — exists at the absorbed path; ticked 2026-07-08
- [x] 1.18 Spec deltas — N/A; absorbed into v4-landing via 2026-07-07-finalize-v4-landing
- [x] 1.19 Spec deltas — N/A; absorbed into v4-landing
- [x] 1.20 Spec deltas — N/A; absorbed into v4-landing
- [ ] 1.21 Update `bonneagar/stacks/HEALTH_REPORT.md` (Session 6 entry after deploys) — DEFERRED to post-deploy (no docker daemon in this session)

## Phase 2 — Validate (2 min)

- [ ] 2.1 `cd /Users/cianmacandeisigh/dev/kings_college_galway && openspec validate 2026-07-02-replace-private-images-and-bring-wave2 --strict` — must say "is valid"
- [ ] 2.2 `cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar && bun run validate-stacks` — 9 gates, 0 hard failures

## Phase 3 — Build dagster image (5 min)

- [ ] 3.1 `cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar && docker build -f stacks/dagster/Dockerfile.dagster -t dagster-local:latest stacks/dagster/`
- [ ] 3.2 `docker images | grep dagster-local` — should show `dagster-local:latest`
- [ ] 3.3 If build fails: debug the Dockerfile (likely missing system deps for dagster-webserver, dagster-aws, boto3, psycopg2-binary). Common fixes: add `libpq-dev`, `libssl-dev` to the apt-get list.

## Phase 4 — Wave 2a deploy (12 min)

- [ ] 4.1 `cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar && docker compose --env-file stacks/litellm/.env --env-file .env -f stacks/litellm/compose.yaml -f stacks/litellm/sidecar.yaml -f stacks/litellm/compose.dev.yaml up -d` (litellm alone — single stack in dev mode)
- [ ] 4.2 Wait 30s. `./scripts/stack.sh litellm ps` — confirm litellm + litellm-db + locket-dev up
- [ ] 4.3 `curl -fsS http://localhost:4000/health/liveliness` — HTTP 200
- [ ] 4.4 `./scripts/stack.sh mlflow up -d` (base + sidecar + dev overlay)
- [ ] 4.5 `curl -fsS http://localhost:5000/api/2.0/mlflow/ping` — HTTP 200
- [ ] 4.6 `./scripts/stack.sh cognee up -d` (base + sidecar + dev overlay)
- [ ] 4.7 `curl -fsS http://localhost:8100/api/health` — HTTP 200

## Phase 5 — Wave 2b deploy (18 min)

- [ ] 5.1 `./scripts/stack.sh langfuse up -d` (base + sidecar + dev overlay; brings up langfuse-web + langfuse-worker + langfuse-clickhouse + langfuse-minio + langfuse-postgres + langfuse-redis + locket-dev)
- [ ] 5.2 Wait 90s for langfuse ClickHouse + Postgres + Redis to all be healthy
- [ ] 5.3 `curl -fsS http://localhost:3001/api/public/health` — HTTP 200
- [ ] 5.4 `./scripts/stack.sh graphiti up -d` (base + sidecar + dev overlay)
- [ ] 5.5 `./scripts/stack.sh dagster up -d` (base + sidecar + dev overlay; uses dagster-local:latest)
- [ ] 5.6 Wait 30s. `./scripts/stack.sh dagster ps` — confirm `dagster` + `dagster-daemon` + locket-dev up
- [ ] 5.7 `curl -fsS http://localhost:3335/server_info` — HTTP 200 + JSON
- [ ] 5.8 `./scripts/stack.sh unstract up -d` (base + sidecar + dev overlay)

## Phase 6 — Wave 2c deploy (10 min)

- [ ] 6.1 `./scripts/stack.sh logfire up -d` (base + sidecar + dev overlay; otel/opentelemetry-collector-contrib image)
- [ ] 6.2 `./scripts/stack.sh dots-ocr up -d` — EXPECTED TO FAIL (`dots-ocr/dots-ocr:latest` doesn't exist on Docker Hub). Document the failure and accept it (deferred to follow-up change).
- [ ] 6.3 `./scripts/stack.sh olmocr up -d` (base + sidecar; uses `alleninstituteforai/olmocr:0.4.27`)
- [ ] 6.4 `curl -fsS http://localhost:8003/health` — HTTP 200
- [ ] 6.5 `./scripts/stack.sh paddleocr up -d` (base + sidecar; uses `paddlecloud/paddleocr:2.6-cpu-latest`)
- [ ] 6.6 `curl -fsS http://localhost:8000/health` — HTTP 200
- [ ] 6.7 `./scripts/stack.sh docling-serve up -d` (base + sidecar)
- [ ] 6.8 `curl -fsS http://localhost:5001/v1/health` — HTTP 200

## Phase 7 — Lakehouse integration smoke tests (15 min)

For each test, document pass/fail in the HEALTH_REPORT Session 6 entry.

- [ ] 7.1 **DLT → DuckLake**: `cd /Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim && uv run python -c "from dlt.common.destinations_oideachais import get_dlt_destination; print(get_dlt_destination())"` — no exceptions
- [ ] 7.2 **DLT pipeline dry-run**: `uv run python -c "from dlt.common.destinations_oideachais import create_pipeline; p = create_pipeline('test', 'test'); print(p.dataset_name)"` — prints "test"
- [ ] 7.3 **Garage S3**: `curl -fsS -o /dev/null -w "%{http_code}\n" http://localhost:3900/health` — 200 or 403
- [ ] 7.4 **LanceDB REST**: `curl -fsS -o /dev/null -w "%{http_code}\n" http://localhost:8182/health` — 200
- [ ] 7.5 **Postgres dev DBs**: `docker exec lakehouse-postgres psql -U lakekeeper -d postgres -c "SELECT datname FROM pg_database WHERE datistemplate = false"` — list shows at least: `mlflow`, `langfuse`, `litellm`, `cognee_oideachais`, `nimtable`, `olake_state`, `ducklake_oideachais`
- [ ] 7.6 **ClickHouse**: `curl -fsS http://localhost:8123/ping` — 200
- [ ] 7.7 **Lakehouse Redis**: `docker exec lakehouse-redis redis-cli ping` — PONG
- [ ] 7.8 **BAML generates**: `cd /Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim && uv run baml-cli generate` — no errors
- [ ] 7.9 **LiteLLM gateway**: `curl -fsS http://localhost:4000/health/liveliness` — 200
- [ ] 7.10 **(optional) BAML test call**: `curl -X POST http://localhost:4000/v1/chat/completions -H 'Authorization: Bearer sk-1234' -d '{"model":"minimax-m3","messages":[{"role":"user","content":"hi"}]}'` — 200 + JSON
- [ ] 7.11 **CocoIndex v1**: `cd /Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim && uv run cocoindex update -L cianfhoghlaim.cocoindex.codebase_indexing:codebase_app` — N files indexed, 0 errors
- [ ] 7.12 **Marimo `ducklake_explorer.py`**: open `http://localhost:2718/notebooks/dashboards/duckdb/ducklake_explorer.py` in a browser; verify "Local Development Configuration" panel shows live DUCKLAKE values (uses the new `marimo/.env.dev` which sets `DUCKLAKE_POSTGRES_HOST=lakehouse-postgres`)
- [ ] 7.13 **FalkorDB**: `docker exec falkordb redis-cli -p 6379 -a devpassword GRAPH.QUERY test "MATCH (n) RETURN n LIMIT 5"` — returns rows (or empty list) without connection error
- [ ] 7.14 **Dagster webserver**: `curl -fsS http://localhost:3335/server_info` — 200 + JSON
- [ ] 7.15 **Dagster code location**: `cd /Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim && DAGSTER_HOME=. uv run dagster dev -m cianfhoghlaim.dagster.definitions 2>&1 | head -20` — "Loading repository... Loaded 5 KCG Components" (or similar — note: this command runs in foreground; the test in CI would be different)

## Phase 8 — Refresh HEALTH_REPORT (5 min)

- [ ] 8.1 Capture the live `docker ps` output
- [ ] 8.2 Write the Session 6 entry at the top of `HEALTH_REPORT.md` (above Session 5 from the prior commit) with:
  - 12 stacks + 18 new containers (total 23 on bunchloch + 2 dev locket-dev sidecars = 25)
  - Per-stack health probe results
  - 15 smoke test results
  - Known issue: dots-ocr broken (deferred)
  - Openchamber deferred to separate change
- [ ] 8.3 Commit on bonneagar worktree: `git add -A && git commit -m "..."`
- [ ] 8.4 Commit on main repo: `git add openspec/changes/2026-07-02-replace-private-images-and-bring-wave2 && git commit -m "..."`

## Phase 9 — Stop + hand off to Change 8 (no auto-proceed)

- [ ] 9.1 Report status to user (containers up, smoke test results, any deviations from plan)
- [ ] 9.2 **STOP** before starting Change 8 — the user must explicitly say "proceed" to start the alignment work (Change 8 modifies cianfhoghlaim code: 18 files of env defaults, BAML env vars, marimo wiring)

## Phase 10 — Wave 2 NEW stacks (added 2026-07-08, pick-3-image-replacement)

The proposal's "Wave 2" referred to DEPLOYING 12 existing stacks
(litellm + mlflow + cognee + langfuse + graphiti + dagster + unstract
+ logfire + 4 OCR). All 12 already exist in `bonneagar/stacks/`.

The 2026-07-08 pick-3-image-replacement change added 7 NEW stacks
under `bonneagar/stacks/wave2/<name>/` (each with the 6-file
GOLD_STANDARD pattern + compose.dev.yaml + .env.dev + README.md):

- [x] 10.1 `bonneagar/stacks/wave2/letta/`   (letta/letta:v0.5.4)        — agent memory layer
- [x] 10.2 `bonneagar/stacks/wave2/kavita/`  (jvmouse/kavita:0.8.6)      — ebook + manga reader
- [x] 10.3 `bonneagar/stacks/wave2/mealie/`  (mealie-recipes/mealie:v1.10.0) — recipe manager
- [x] 10.4 `bonneagar/stacks/wave2/immich/`  (immich-app/immich-*:release-1.111.0) — photo management
- [x] 10.5 `bonneagar/stacks/wave2/siyuan/`  (b3log/siyuan:v3.1.0)       — block-based notes
- [x] 10.6 `bonneagar/stacks/wave2/outline/` (outlinewiki/outline:0.78.0) — team wiki
- [x] 10.7 `bonneagar/stacks/wave2/khoj/`    (khoj-ai/khoj:v1.30.0)      — personal AI
- [x] 10.8 `bonneagar/komodo/procedures/deploy-wave2-bunchloch.toml` — omnibus Komodo procedure (5 stages: prereqs → memory → personal → health → validate)
- [x] 10.9 `git commit` on `pick-3-image-replacement` branch — landed as commit bcc9a9e1b
- [x] 10.10 `git push` (see pick-3-image-replacement/final-report section)
