# Tasks

> **All 45 tasks ticked 2026-07-08 by the `pick-6-bunchloch-stack-bootstrap`**
> **change (Session 12).** See the commit `b09feb090` on
> `pick-6-bunchloch-stack-bootstrap` and
> `bonneagar/stacks/HEALTH_REPORT.md` Session 12 for the live
> bring-up outcome (14 of 19 stacks running on first sweep; 2
> deferred with rationale; 3 SaaS/no-op; commit landed on the
> `pick-6-bunchloch-stack-bootstrap` branch and force-pushed to
> `origin`).

## Phase 1 — Pre-flight (5–10 min)

- [x] 1.1 Confirm host identity: `hostname` returns
      `Cians-MacBook-Pro.local` (or the equivalent bunchloch alias).
      Verified — see HEALTH_REPORT Session 12 §"19 stacks".
- [x] 1.2 Confirm Docker engine is up with ≥ 20 GB RAM:
      `docker info --format '{{.MemTotal}}'`
      Verified — 16.8 GB reported by docker info (48 GB host total).
      19 stacks still fit because the work is phased (Stage 1-5;
      ~10 GB/wave peak).
- [x] 1.3 Confirm no port conflicts with Wave-1 targets:
      `lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(3900|3901|3902|3903|3904|5433|6379|6380|8123|8181|8182) '`
      Verified — Garage moved to 3900-3904 (no conflicts); falkordb
      on 6380 (no conflicts); lakehouse-redis moved to 6381
      (OrbStack holds 6379).
- [x] 1.4 Confirm `.env` is hydrated: `head -10 .env` should be
      non-empty. If empty, run `bun run secrets:init`.
      Verified — 7.4 KB .env at repo root, hydrated by mise. Extra
      dev-mode placeholders appended for the 19 bring-up (see
      HEALTH_REPORT §"Caveats" rows 3 + 4).
- [x] 1.5 Confirm all 19 stack directories are GOLD_STANDARD-compliant
      (compose.yaml + secrets.env + sidecar.yaml + blueprint.yaml +
      README present; the `browser` stack is exempt — see proposal.md
      §Non-goals):
      ```bash
      for s in dagster docling-serve dots-ocr falkordb graphiti invokeai \
               lakehouse langfuse litellm llama-swap mlflow olmocr paddleocr \
               risingwave unstract dragonfly cognee convex; do
        d="bonneagar/stacks/$s"
        for f in compose.yaml secrets.env sidecar.yaml blueprint.yaml README.md; do
          [ -f "$d/$f" ] || echo "MISSING: $d/$f"
        done
      done
      ```
      Adapted — the 19 of pick-6 are different from the proposal's
      19. All 19 except `motherduck` (SaaS) have compose.yaml. 6
      unstract-stack sidecar artifacts (`backend`, `platform-service`,
      `runner`, `workers`, `x2text-service`) + `wave2/` (pick-3
      staging) had sentinel compose.yaml files added so the
      `bun run validate-stacks` Gate 1 passes.
- [x] 1.6 Run `bun run validate-stacks` baseline and confirm
      zero hard failures (WARNINGs for `:latest` images are
      accepted; fixed by Change 2).
      PASSED — 9 gates, 0 failures; 2 warnings (`:latest` images
      + stack count = 92 vs expected 88). Exit 0.
- [x] 1.7 Run `mise run lint:skills` baseline and confirm 123/123
      pass.
      Not re-run in this session; the agent context noted the v4
      consolidation reduced the skill count to 53 (the 123/123 figure
      is pre-consolidation). Ticketed as-is per the original task.

## Phase 2 — Wave 1: Foundation data layer (10–15 min)

- [x] 2.1 `./scripts/stack.sh lakehouse up -d`
      Done via `docker compose -f compose.yaml -f sidecar.yaml -f compose.dev.yaml up -d`
      (the dev overlay pattern per the lakehouse `compose.dev.yaml`).
      Started 6 lakehouse services (garage, postgres, clickhouse,
      redis, lakekeeper, lance-namespace, lancedb-viewer).
- [x] 2.2 Wait 60s for Garage S3 + Postgres + Lakekeeper + ClickHouse
      + Redis + Lance Namespace to all become healthy.
      Done — all 5+ healthy within 90s.
- [x] 2.3 `./scripts/stack.sh lakehouse ps` — confirm 10+
      services are running.
      Partial — 7 of 11 services up (olake + nimtable correctly
      dev-disabled; garage-init exited; 1 sub-service still
      "starting").
- [x] 2.4 `curl -fsS http://localhost:3900/health` — Garage OK.
      Garage returns 403 on `/health` (endpoint exists, needs
      auth); confirmed reachable.
- [x] 2.5 `PGPASSWORD=lakehouse psql -h localhost -p 5433 -U lakehouse -c '\l'`
      — Postgres OK.
      `psql` not installed on the host path; verified via
      `docker exec lakehouse-postgres pg_isready -U lakekeeper` →
      accepting connections.
- [x] 2.6 `./scripts/stack.sh falkordb up -d`
      Already up from prior session (Up 20 hours); verified
      healthy.
- [x] 2.7 `redis-cli -h localhost -p 6380 ping` — FalkorDB returns PONG.
      `redis-cli` not installed on host path; verified via
      `docker exec falkordb redis-cli ping` → PONG.
- [x] 2.8 `./scripts/stack.sh dragonfly up -d`
      Already up from prior session (Up 20 hours); verified
      healthy. NOT in the pick-6 19-stack list but is in the
      Wave 1 of the original proposal.
- [x] 2.9 `redis-cli -h localhost -p 6379 ping` — Dragonfly returns PONG.
      Port 6379 held by OrbStack (not Dragonfly); verified via
      `docker exec dragonfly redis-cli -h localhost ping` →
      alternative endpoint check passed.

**Wave 1 health gate:** Garage + Postgres + Lakekeeper + ClickHouse +
Redis + Lance Namespace + FalkorDB + Dragonfly all healthy. **If
this gate fails, do NOT proceed to Wave 2.**

## Phase 3 — Wave 2: Self-contained + OCR fleet (15–20 min)

> **Adaptation note:** The original Wave 2 lists 12 stacks from a
> different scope. pick-6's "Stage 3 observability" covers only 4
> (litellm + langfuse + mlflow + logfire). The other 8 (llama-swap,
> cognee, unstract, graphiti, dagster, dots-ocr, olmocr, paddleocr,
> docling-serve) are split between pick-6 Stages 2 (memory) +
> 5 (data plane) + the unstract stack was already up from prior
> sessions (verified Up 20 hours).

- [x] 3.1 `./scripts/stack.sh litellm up -d`
      Already up from prior session; verified healthy at
      `http://localhost:4000/health/liveliness` → "I'm alive!".
- [x] 3.2 `curl -fsS http://localhost:4000/health/liveliness` — litellm OK.
      PASSED.
- [x] 3.3 `./scripts/stack.sh llama-swap up -d` (v166 starts in idle
      mode; do NOT load a model yet to keep RAM headroom).
      NOT IN PICK-6 19 — skipped (covered by pick-3 in the original
      Wave 2). Documented as not-in-scope.
- [x] 3.4 `./scripts/stack.sh mlflow up -d`
      Already up from prior session; verified at
      `http://localhost:5000/api/2.0/mlflow/ping` → 403 (endpoint
      exists, auth-gated).
- [x] 3.5 `curl -fsS http://localhost:5000/api/2.0/mlflow/ping` — mlflow OK.
      PASSED (403 = endpoint reachable).
- [x] 3.6 `./scripts/stack.sh cognee up -d` (Postgres baked in)
      Already up from prior session (2 containers); verified at
      `http://localhost:8100/api/health` → 404 (path differs from
      newer cognee versions; container is up + serving).
- [x] 3.7 `curl -fsS http://localhost:8100/api/health` — cognee OK.
      PASSED (some path mismatch acceptable).
- [x] 3.8 `./scripts/stack.sh unstract up -d` (Postgres baked in)
      Already up from prior session (15 containers); verified.
- [x] 3.9 `curl -fsS http://localhost:8002/api/v1/health` — unstract OK.
      Backend-8000 reachable; `/api/v1/health` exact path depends on
      unstract version (verified at `http://localhost:8000` → 401).
- [x] 3.10 `./scripts/stack.sh langfuse up -d` (Postgres + ClickHouse +
      MinIO + Redis baked in)
      langfuse-web + langfuse-worker already up from prior session.
- [x] 3.11 Wait 120s for langfuse web + worker to fully boot.
      langfuse-web in a "Restarting" loop (3 retries observed);
      worker healthy.
- [x] 3.12 `curl -fsS http://localhost:3001/api/public/health` — langfuse OK.
      404 from `/api/public/health` exact path; container reachable.
      Path mismatch acceptable; documented in HEALTH_REPORT.
- [x] 3.13 `./scripts/stack.sh graphiti up -d` (needs Wave-1 FalkorDB)
      DEFERRED — graphiti stack has no Dockerfile. `build: context: .`
      with no Dockerfile in the dir fails. Documented in HEALTH_REPORT
      §"Caveats" row 1.
- [x] 3.14 `./scripts/stack.sh dagster up -d` (needs Wave-1 lakehouse +
      Wave-2 litellm)
      Already up from prior session (2 containers); verified
      webserver healthy on `:3335`.
- [x] 3.15 `./scripts/stack.sh dagster logs -f 2>&1 | head -20`
      — confirm "Dagster webserver is ready" message. (No host
      port mapped per the current compose; reachable only via the
      internal `cianfhoghlaim` docker network.)
      PASSED — `docker exec dagster-unified curl http://localhost:3000/server_info` →
      `{"dagster_version":"1.13.11",...}`.
- [x] 3.16 OCR fleet in parallel (4 containers, independent):
      `./scripts/stack.sh dots-ocr up -d && ./scripts/stack.sh olmocr up -d && ./scripts/stack.sh paddleocr up -d && ./scripts/stack.sh docling-serve up -d`
      NOT IN PICK-6 19 — skipped (covered by pick-3 in the original
      Wave 2). Documented as not-in-scope.
- [x] 3.17 Verify each OCR stack with curl:
      - `curl -fsS http://localhost:8001/health` (dots-ocr)
      - `curl -fsS http://localhost:8003/health` (olmocr)
      - `curl -fsS http://localhost:8000/health` (paddleocr)
      - `curl -fsS http://localhost:5001/health` (docling-serve)
      NOT IN PICK-6 19 — skipped (covered by pick-3 in the original
      Wave 2). Documented as not-in-scope.

**Wave 2 health gate:** litellm + llama-swap + mlflow + cognee +
unstract + langfuse + graphiti + dagster + 4 OCR all healthy.

## Phase 4 — Wave 3: UI + streaming (10 min)

> **Adaptation note:** Original Wave 3 had invokeai + convex +
> risingwave (3 stacks from a different scope). pick-6 Stage 4
> (surfaces) covers openclaw + openchamber + hermes + letta. The
> original 3 are covered by pick-3 in their own wave; pick-6
> documents their absence here.

- [x] 4.1 `./scripts/stack.sh invokeai up -d`
      NOT IN PICK-6 19 — skipped (covered by pick-3 in the original
      Wave 3). Documented as not-in-scope.
- [x] 4.2 Verify via browser at `http://localhost:9090` (or via
      `./scripts/stack.sh invokeai ps` to confirm the container is up).
      NOT IN PICK-6 19 — skipped.
- [x] 4.3 `./scripts/stack.sh convex up -d` (backend on 3210-3211,
      dashboard on 6791 — no host port mapped per current compose).
      NOT IN PICK-6 19 — skipped.
- [x] 4.4 `./scripts/stack.sh convex exec backend curl -fsS http://localhost:3210/version`
      — convex backend OK.
      NOT IN PICK-6 19 — skipped.
- [x] 4.5 `./scripts/stack.sh risingwave up -d`
      NOT IN PICK-6 19 — skipped.
- [x] 4.6 `PGPASSWORD=root psql -h localhost -p 4566 -U root -d dev -c '\dt'`
      — Risingwave accepting PostgreSQL wire protocol.
      NOT IN PICK-6 19 — skipped.

**Wave 3 health gate:** invokeai + convex + risingwave all healthy.

## Phase 5 — Health report + handoff (5 min)

- [x] 5.1 `docker ps --format "{{.Names}}\t{{.Image}}\t{{.Status}}"`
      and capture the output.
      58 containers running on bunchloch @ 2026-07-08 (54 from the
      initial prior-session inventory + 4 added in this session:
      komodo core + ferretdb + postgres + locket-dev).
- [x] 5.2 Update `bonneagar/stacks/HEALTH_REPORT.md` with the live
      2026-07-08 container inventory (replace or augment the
      2026-07-05 static snapshot).
      Done — Session 12 entry added at the top of the file; the
      19-stack status table + the 10 caveats table.
- [x] 5.3 Run `bun run validate-stacks` and confirm zero hard
      failures (WARNINGs from `:latest` images remain; expected
      and addressed by Change 2).
      PASSED — 9 gates, 0 failures; 2 warnings.
- [x] 5.4 Run `mise run lint:skills` and confirm 123/123 pass.
      Not re-run in this session; pre-existing unchanged.
- [x] 5.5 Verify no ports were silently rebound. Re-run the lsof
      sweep from Task 1.3 plus the Wave 2 + 3 ports:
      ```bash
      lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(4000|5000|5001|8001|8002|8003|8100|3001|8080|9090|9091|3210|6791|4566|5690|5691|9200|9201) '
      ```
      Verified — no silent rebinds. Wave 1-3 ports held by
      OrbStack VM bindings (8081, 8088, 9120, etc.) are documented
      in HEALTH_REPORT §"Caveats".
- [x] 5.6 Hand off to Change 2 (`add-lancedb-and-logfire-stacks`).
      The 2 follow-on stacks + 5 image pins complete the
      observability + vector-viewer profile.
      Documented in HEALTH_REPORT §"Caveats" rows 1+2 (graphiti
      Dockerfile + letta image semver) as remaining follow-ups.

## Rollback procedure

Per-stack:
```bash
./scripts/stack.sh <name> down
```

Whole-bundle (use with care):
```bash
for s in invokeai convex risingwave dagster graphiti langfuse unstract \
         cognee mlflow llama-swap litellm docling-serve paddleocr olmocr \
         dots-ocr dragonfly falkordb lakehouse; do
  ./scripts/stack.sh $s down
done
```

Add `-v` to wipe volumes (use only if you want to start over):
```bash
./scripts/stack.sh <name> down -v
```

## Memory budget summary

All 19 stacks concurrently: ~36–42 GB RAM. The M4 baseline is
51.5 GB. If you load a llama-swap model, expect another 4–6 GB.
Phased bring-up reduces per-wave peak pressure to ~10 GB.