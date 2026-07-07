# Tasks

## Phase 1 — Pre-flight (5–10 min)

- [ ] 1.1 Confirm host identity: `hostname` returns
      `Cians-MacBook-Pro.local` (or the equivalent bunchloch alias).
- [ ] 1.2 Confirm Docker engine is up with ≥ 20 GB RAM:
      `docker info --format '{{.MemTotal}}'`
- [ ] 1.3 Confirm no port conflicts with Wave-1 targets:
      `lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(3900|3901|3902|3903|3904|5433|6379|6380|8123|8181|8182) '`
- [ ] 1.4 Confirm `.env` is hydrated: `head -10 .env` should be
      non-empty. If empty, run `bun run secrets:init`.
- [ ] 1.5 Confirm all 19 stack directories are GOLD_STANDARD-compliant
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
- [ ] 1.6 Run `bun run validate-stacks` baseline and confirm
      zero hard failures (WARNINGs for `:latest` images are
      accepted; fixed by Change 2).
- [ ] 1.7 Run `mise run lint:skills` baseline and confirm 123/123
      pass.

## Phase 2 — Wave 1: Foundation data layer (10–15 min)

- [ ] 2.1 `./scripts/stack.sh lakehouse up -d`
- [ ] 2.2 Wait 60s for Garage S3 + Postgres + Lakekeeper + ClickHouse
      + Redis + Lance Namespace to all become healthy.
- [ ] 2.3 `./scripts/stack.sh lakehouse ps` — confirm 10+
      services are running.
- [ ] 2.4 `curl -fsS http://localhost:3900/health` — Garage OK.
- [ ] 2.5 `PGPASSWORD=lakehouse psql -h localhost -p 5433 -U lakehouse -c '\l'`
      — Postgres OK.
- [ ] 2.6 `./scripts/stack.sh falkordb up -d`
- [ ] 2.7 `redis-cli -h localhost -p 6380 ping` — FalkorDB returns PONG.
- [ ] 2.8 `./scripts/stack.sh dragonfly up -d`
- [ ] 2.9 `redis-cli -h localhost -p 6379 ping` — Dragonfly returns PONG.

**Wave 1 health gate:** Garage + Postgres + Lakekeeper + ClickHouse +
Redis + Lance Namespace + FalkorDB + Dragonfly all healthy. **If
this gate fails, do NOT proceed to Wave 2.**

## Phase 3 — Wave 2: Self-contained + OCR fleet (15–20 min)

- [ ] 3.1 `./scripts/stack.sh litellm up -d`
- [ ] 3.2 `curl -fsS http://localhost:4000/health/liveliness` — litellm OK.
- [ ] 3.3 `./scripts/stack.sh llama-swap up -d` (v166 starts in idle
      mode; do NOT load a model yet to keep RAM headroom).
- [ ] 3.4 `./scripts/stack.sh mlflow up -d`
- [ ] 3.5 `curl -fsS http://localhost:5000/api/2.0/mlflow/ping` — mlflow OK.
- [ ] 3.6 `./scripts/stack.sh cognee up -d` (Postgres baked in)
- [ ] 3.7 `curl -fsS http://localhost:8100/api/health` — cognee OK.
- [ ] 3.8 `./scripts/stack.sh unstract up -d` (Postgres baked in)
- [ ] 3.9 `curl -fsS http://localhost:8002/api/v1/health` — unstract OK.
- [ ] 3.10 `./scripts/stack.sh langfuse up -d` (Postgres + ClickHouse +
      MinIO + Redis baked in)
- [ ] 3.11 Wait 120s for langfuse web + worker to fully boot.
- [ ] 3.12 `curl -fsS http://localhost:3001/api/public/health` — langfuse OK.
- [ ] 3.13 `./scripts/stack.sh graphiti up -d` (needs Wave-1 FalkorDB)
- [ ] 3.14 `./scripts/stack.sh dagster up -d` (needs Wave-1 lakehouse +
      Wave-2 litellm)
- [ ] 3.15 `./scripts/stack.sh dagster logs -f 2>&1 | head -20`
      — confirm "Dagster webserver is ready" message. (No host
      port mapped per the current compose; reachable only via the
      internal `cianfhoghlaim` docker network.)
- [ ] 3.16 OCR fleet in parallel (4 containers, independent):
      `./scripts/stack.sh dots-ocr up -d && ./scripts/stack.sh olmocr up -d && ./scripts/stack.sh paddleocr up -d && ./scripts/stack.sh docling-serve up -d`
- [ ] 3.17 Verify each OCR stack with curl:
      - `curl -fsS http://localhost:8001/health` (dots-ocr)
      - `curl -fsS http://localhost:8003/health` (olmocr)
      - `curl -fsS http://localhost:8000/health` (paddleocr)
      - `curl -fsS http://localhost:5001/health` (docling-serve)

**Wave 2 health gate:** litellm + llama-swap + mlflow + cognee +
unstract + langfuse + graphiti + dagster + 4 OCR all healthy.

## Phase 4 — Wave 3: UI + streaming (10 min)

- [ ] 4.1 `./scripts/stack.sh invokeai up -d`
- [ ] 4.2 Verify via browser at `http://localhost:9090` (or via
      `./scripts/stack.sh invokeai ps` to confirm the container is up).
- [ ] 4.3 `./scripts/stack.sh convex up -d` (backend on 3210-3211,
      dashboard on 6791 — no host port mapped per current compose).
- [ ] 4.4 `./scripts/stack.sh convex exec backend curl -fsS http://localhost:3210/version`
      — convex backend OK.
- [ ] 4.5 `./scripts/stack.sh risingwave up -d`
- [ ] 4.6 `PGPASSWORD=root psql -h localhost -p 4566 -U root -d dev -c '\dt'`
      — Risingwave accepting PostgreSQL wire protocol.

**Wave 3 health gate:** invokeai + convex + risingwave all healthy.

## Phase 5 — Health report + handoff (5 min)

- [ ] 5.1 `docker ps --format "{{.Names}}\t{{.Image}}\t{{.Status}}"`
      and capture the output.
- [ ] 5.2 Update `bonneagar/stacks/HEALTH_REPORT.md` with the live
      2026-07-02 container inventory (replace or augment the
      2026-06-15 static snapshot).
- [ ] 5.3 Run `bun run validate-stacks` and confirm zero hard
      failures (WARNINGs from `:latest` images remain; expected
      and addressed by Change 2).
- [ ] 5.4 Run `mise run lint:skills` and confirm 123/123 pass.
- [ ] 5.5 Verify no ports were silently rebound. Re-run the lsof
      sweep from Task 1.3 plus the Wave 2 + 3 ports:
      ```bash
      lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(4000|5000|5001|8001|8002|8003|8100|3001|8080|9090|9091|3210|6791|4566|5690|5691|9200|9201) '
      ```
- [ ] 5.6 Hand off to Change 2 (`add-lancedb-and-logfire-stacks`).
      The 2 follow-on stacks + 5 image pins complete the
      observability + vector-viewer profile.

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