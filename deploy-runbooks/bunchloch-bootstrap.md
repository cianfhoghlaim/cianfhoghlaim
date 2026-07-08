# Bunchloch Cold-Boot Procedure

> **Read this first.** Use this runbook when the `bunchloch`
> host (MacBook M4 / M4 Max / Pro — typically
> `Cians-MacBook-Pro.local` on this operator's machine) is a
> cold-boot (zero Compose containers running) and you need the
> 19 canonical workload-host stacks brought up in dev mode
> (no Locket, no live Infisical round trip).
>
> After the in-flight
> `2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops`
> change lands, prefer `bun run iac:bootstrap` instead and
> mark this runbook DEPRECATED.

## Why this exists

`bunchloch` (the MacBook M4 workload host) was cold as of
2026-07-02 (verified via `docker ps -a` returning zero rows).
The Komodo TOML bundles reference paths that no longer exist
post-v4-canonical (the `infrastructure/stacks/<x>/` references
are stale; canonical path is `bonneagar/stacks/<x>/`).
`./scripts/stack.sh` reads the canonical compose.yaml files
directly, bypassing that drift.

This runbook is created by the
`2026-07-02-bunchloch-stack-bootstrap` openspec change.

## Audience

A cold-boot agent or operator on the bunchloch host who needs
the 19 GOLD_STANDARD-compliant stacks running with no Infisical /
Locket round trip (dev mode).

The 19 stacks are exactly the user-selected list:

```
dagster docling-serve dots-ocr falkordb graphiti invokeai
lakehouse langfuse litellm llama-swap mlflow olmocr paddleocr
risingwave unstract dragonfly cognee convex
```

The `browser` stack is **NOT** in this runbook — it is missing
5/6 GOLD_STANDARD files (no `secrets.env`, no `sidecar.yaml`,
no `blueprint.yaml`, no `README.md`) and is addressed by a
separate openspec change.

## Pre-flight

```bash
# 1. Confirm you are on the bunchloch host
hostname
# Expect: Cians-MacBook-Pro.local (or your equivalent bunchloch alias)

# 2. Docker engine is up + has ≥ 20 GB RAM
docker info --format '{{.MemTotal}}'

# 3. No port conflicts on Wave 1 + Wave 2 + Wave 3 targets
lsof -nP -iTCP -sTCP:LISTEN \
  | grep -E ':(3900|3901|3902|3903|3904|5433|6379|6380|8123|9000|8181|8182|4000|5000|5001|8001|8002|8003|8100|3001|8080|9090|9091|3210|6791|4566|5690|5691|9200|9201|3335) '

# 4. Stack defaults hydrated (Locket disabled)
ls -la .env
head -10 .env    # should be non-empty; if empty run `bun run secrets:init`

# 5. GOLD_STANDARD compliance baseline for the 19 stacks
for s in dagster docling-serve dots-ocr falkordb graphiti invokeai \
         lakehouse langfuse litellm llama-swap mlflow olmocr paddleocr \
         risingwave unstract dragonfly cognee convex; do
  d="bonneagar/stacks/$s"
  for f in compose.yaml secrets.env sidecar.yaml blueprint.yaml README.md; do
    [ -f "$d/$f" ] || echo "MISSING: $d/$f"
  done
done
# Expect: no MISSING lines

# 6. Audit baselines
bun run validate-stacks       # expect zero hard failures (`:latest` WARNINGs are accepted)
mise run lint:skills          # expect 53/53 pass
```

## Wave 1 — Foundation data layer (10–15 min)

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar

./scripts/stack.sh lakehouse up -d
sleep 60
./scripts/stack.sh lakehouse ps
curl -fsS http://localhost:3900/health || echo "garage not ready"

./scripts/stack.sh falkordb up -d
./scripts/stack.sh dragonfly up -d
```

**Health gate before Wave 2 (all must pass):**

- Garage responding at `:3900`
- Postgres accepting at `:5433`
- Lakekeeper responding at `:8181`
- Lance Namespace responding at `:8182`
- ClickHouse responding at `:8123`
- `redis-cli -h localhost -p 6380 ping` (FalkorDB) returns PONG
- `redis-cli -h localhost -p 6379 ping` (Dragonfly) returns PONG

If any of the above fail, do NOT proceed to Wave 2. Diagnose
and re-run the failing stack.

## Wave 2 — Self-contained + OCR fleet (15–20 min)

```bash
# Self-contained services (Wave 2a)
./scripts/stack.sh litellm up -d
./scripts/stack.sh llama-swap up -d     # do NOT load a model yet (RAM headroom)
./scripts/stack.sh mlflow up -d
./scripts/stack.sh cognee up -d
./scripts/stack.sh unstract up -d
./scripts/stack.sh langfuse up -d
./scripts/stack.sh graphiti up -d       # needs falkordb from Wave 1
./scripts/stack.sh dagster up -d        # needs lakehouse + litellm
sleep 120   # langfuse + dagster cold-boot

# OCR fleet (Wave 2b — 4 containers, all independent)
./scripts/stack.sh dots-ocr up -d
./scripts/stack.sh olmocr up -d
./scripts/stack.sh paddleocr up -d
./scripts/stack.sh docling-serve up -d
```

**Health gate before Wave 3 (all must pass):**

- `curl :4000/health/liveliness` — litellm
- `curl :5000/api/2.0/mlflow/ping` — mlflow
- `curl :8100/api/health` — cognee
- `curl :8002/api/v1/health` — unstract
- `curl :3001/api/public/health` — langfuse
- dagster webserver "Dagster webserver is ready" in logs
- `curl :8001/health` (dots-ocr)
- `curl :8003/health` (olmocr)
- `curl :8000/health` (paddleocr)
- `curl :5001/health` (docling-serve)

## Wave 3 — UI + streaming (10 min)

```bash
./scripts/stack.sh invokeai up -d    # browser → http://localhost:9090
./scripts/stack.sh convex up -d      # internal only; exec into it to query
./scripts/stack.sh risingwave up -d   # psql -h localhost -p 4566
```

**Health gate:**

- invokeai container up at `:9090` (verify via browser or `docker ps`)
- convex backend at container `:3210` (verify via
  `./scripts/stack.sh convex exec backend curl :3210/version`)
- Risingwave accepting psql at `:4566`

## Defer list

The following stacks are NOT in this runbook; they are
addressed by sibling openspec changes:

- **`lancedb`** + **`logfire`** + image pinning → change
  `2026-07-02-add-lancedb-and-logfire-stacks` (Wave 1 + Wave 2b)
- **`marimo`** → change `2026-07-02-add-marimo-stack` (Wave 3)
- **`hermes`**, **`openclaw`**, **`openchamber`** → change
  `2026-07-02-add-agent-surface-stacks` (Wave 4)
- **`browser`** → change
  `2026-07-XX-bring-browser-stack-to-gold-standard` (NOT in
  this sequence)
- **`mailcow-dockerized`**, **`mlx-omni`**, **`letta`**,
  **`memgraph`** → separate future changes

## Rollback

Per-stack: `./scripts/stack.sh <name> down`.

Whole-bundle (use with care):

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar
for s in invokeai convex risingwave dagster graphiti langfuse unstract \
         cognee mlflow llama-swap litellm docling-serve paddleocr olmocr \
         dots-ocr dragonfly falkordb lakehouse; do
  ./scripts/stack.sh $s down
done
```

Add `-v` to wipe volumes (only if you want to start over):

```bash
./scripts/stack.sh <name> down -v
```

## Memory budget

All 19 stacks concurrently: ~36–42 GB RAM. The M4 baseline is
51.5 GB. Loading a llama-swap model adds another 4–6 GB.
**Phased bring-up reduces per-wave peak pressure to ~10 GB**.

## Failure modes & escalation

- **`lock /var/run/docker.sock`** — start Docker Desktop.
- **`bind: address already in use`** — `lsof -i :<port>` and
  stop the conflicting process (often macOS ControlCe on
  5000 / 7000; Spotify on 57621 / 58380).
- **`graphiti:local` not found** —
  `cd bonneagar/stacks/graphiti && docker compose build graphiti`
  first.
- **`ghcr.io/cianfhoghlaim/<x>:latest` 401/404** —
  `docker login ghcr.io` first; the image may need a
  personal-access-token pull.
- **Compose version mismatch** — `docker compose version`
  should be ≥ 2.20 (we have v5.1.2 ✓).
- **`mlflow` 5000 not reachable** — confirm
  `${MLFLOW_PORT:-5000}:5000` env var expansion is working;
  the port mapping is in `bonneagar/stacks/mlflow/compose.yaml`
  line 36 (already correct per 2026-07-02 re-inspection).
- **`:latest` WARNINGs in `bun run validate-stacks`** — accepted
  in this change; fixed by
  `2026-07-02-add-lancedb-and-logfire-stacks` (5 image pins:
  cognee, dots-ocr, olmocr, paddleocr, docling-serve).

## See also

- `openspec/changes/2026-07-02-bunchloch-stack-bootstrap/` —
  this runbook's source-of-truth openspec change.
- `openspec/changes/2026-07-02-add-lancedb-and-logfire-stacks/`
  — adds `lancedb` + `logfire` + pins 5 unpinned images.
- `openspec/changes/2026-07-02-add-marimo-stack/` — adds
  the marimo notebook server.
- `openspec/changes/2026-07-02-add-agent-surface-stacks/` —
  adds `hermes` + `openclaw` + `openchamber`.
- `openspec/changes/2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops/`
  — heals the Komodo TOML drift; once merged, the canonical
  IaC path takes over and this runbook is deprecated.
- `bonneagar/AGENTS.md` §"Priority compose stacks (4 of 86)".
- `bonneagar/stacks/HEALTH_REPORT.md` (2026-06-15 stale
  snapshot; refresh after Wave 3 lands).
- `.agents/skills/infrastructure-stacks/SKILL.md` — the
  router skill for the 87-stack catalogue.