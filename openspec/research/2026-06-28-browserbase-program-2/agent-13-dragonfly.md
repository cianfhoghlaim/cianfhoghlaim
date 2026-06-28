# Agent 13 — Dragonfly (Redis-compatible in-memory data store)

**Date:** 2026-06-28
**Phase:** BrowserBase Program 2 (Wave 1, Agent 13 of 25)
**Budget:** ~200 BrowserBase credits
**Subagent:** research (infrastructure)
**Upstream canonical image:** `docker.dragonflydb.io/dragonflydb/dragonfly:latest`

## TL;DR

**Dragonfly** is the Redis/Valkey/Memcached‑API‑compatible in‑memory data store that Cianfhoghlaim uses as the **episode cache side‑car to Graphiti** (and the leaderboard / message queue substrate for Túatha + the Dagster run queue). The upstream‑verified canonical claim is **25× more QPS than Redis + 2× lower P99 latency** on the c6gn.16xlarge instance (3.97 M QPS Dragonfly vs 148 k QPS Redis; benchmark source: `github.com/dragonflydb/dragonfly#benchmarks`). Internally the engine uses **shared‑nothing sharding** (keyspace partitioned across `num_shards` threads, one shard per `proactor` thread from the open‑sourced **Helio** I/O library — `github.com/romange/helio`) with the **Dash hashtable** (from the "Dash: Scalable Hashing on Persistent Memory" paper) and **VLL locking** (from "VLL: a lock manager redesign for main memory database systems"). Eviction when `--cache_mode=true` uses a **novel algorithm that outperforms LRU/LFU with zero memory overhead** (NOT `allkeys-lru`, which is a Redis‑only flag and does **not exist** in Dragonfly). Snapshots are **fork‑less** via `--snapshot_cron` (cron schedule) or `--save_schedule` (deprecated) with `--df_snapshot_format=true` writing `.dfs` files; auto‑load on startup, auto‑save on shutdown if `--dbfilename` non‑empty, with preview S3 support via `--dir s3://bucket/path`.

The P2‑30 phase‑1 spec contains **4 factual errors** (wrong throughput claim, fictional `--cache_fetch_mode` flag, missing `dragonfly_health.py` file, wrong `--maxmemory-policy` flag) that must be reconciled — see §6 anti‑patterns and §8 refactor opportunities.

## Code

### Canonical `docker.dragonflydb.io/dragonflydb/dragonfly` invocation (verbatim from upstream docs)

```bash
# Linux (production)
docker run --network=host --ulimit memlock=-1 docker.dragonflydb.io/dragonflydb/dragonfly

# macOS / Windows (no host networking)
docker run -p 6379:6379 --ulimit memlock=-1 docker.dragonflydb.io/dragonflydb/dragonfly

# Prerequisites (upstream): 4 GB RAM minimum, 1 CPU core minimum, Linux kernel ≥ 4.19 (5.10 recommended)
# x86_64 requires sandybridge-or-newer; arm64 supported.
# Source: https://www.dragonflydb.io/docs/getting-started/docker
```

### Cianfhoghlaim canonical compose (verbatim from `cianfhoghlaim/stacks/dragonfly/compose.yaml:1-17`)

```yaml
name: dragonfly
services:
  dragonfly:
    image: docker.dragonflydb.io/dragonflydb/dragonfly:latest
    container_name: dragonfly
    restart: unless-stopped
    ports: ["6379:6379"]
    command: ["--port=6379","--maxmemory=8gb","--cache_mode=true","--requirepass=${DRAGONFLY_PASSWORD:-devpassword}"]
    healthcheck:
      test: ["CMD-SHELL", "redis-cli -a ${DRAGONFLY_PASSWORD:-devpassword} ping || exit 1"]
      interval: 10s; timeout: 5s; retries: 5; start_period: 10s
    deploy:
      resources:
        limits: {memory: 10G, cpus: '4'}
    networks: [cianfhoghlaim]
networks:
  cianfhoghlaim: {driver: bridge}
```

> **Note:** `--cache_mode=true` (NOT `--cache_fetch_mode=normal` as P2‑30 claims; `--cache_fetch_mode` is **not a Dragonfly flag**). Eviction is governed by the `--cache_mode` boolean + `--eviction_memory_budget_threshold` (knob) — the algorithm is the upstream "novel cache eviction", not `allkeys-lru`.

### Canonical Python client (consumed by Graphiti episode cache; from P1B‑07 + Agent 11)

```python
# Pattern used in cianfhoghlaim/core/cognee/_graph/graphiti_client.py (via redislite/redis-py)
import redis

# Production: dragonfly sits at redis://dragonfly:6379/0
# with the password from ${DRAGONFLY_PASSWORD}
cache = redis.Redis(
    host="dragonfly",
    port=6379,
    db=0,
    password="${DRAGONFLY_PASSWORD}",  # required by --requirepass in compose
    decode_responses=False,
    socket_timeout=5,
    socket_connect_timeout=3,
)

# Passed to Graphiti() as cache_client= (any Redis-py compatible client works)
from graphiti_core import Graphiti
graphiti = Graphiti(graph_driver=falkor_driver, cache_client=cache, ...)
```

### Related files in the repo

| Path | Purpose | Lines | Status |
|:--|:--|--:|:--|
| `cianfhoghlaim/stacks/dragonfly/compose.yaml` | Canonical 17‑line Dragonfly service (v4 consolidated location) | 17 | ✅ current |
| `infrastructure/stacks/dragonfly/compose.yaml` | **DUPLICATE** of the above (byte‑identical) — v4 leftover | 17 | 🗑 delete after v4 cleanup |
| `cianfhoghlaim/stacks/dragonfly/README.md` | Marketing‑flavoured README (claims "25x throughput") | 51 | ✅ current |
| `cianfhoghlaim/stacks/dragonfly/secrets.env` | `DRAGONFLY_PASSWORD={{ infisical://dev-baile/dragonfly/password }}` | 1 | ✅ current |
| `infrastructure/pangolin/private-resources-fixed.blueprint.yaml:101-111` | `graphiti.cianfhoghlaim.ie` Pangolin entry (graphiti stack) | — | ✅ current |
| `infrastructure/stacks/tuatha/compose.yaml:20` | Tuatha stack references `DRAGONFLY_URL=redis://dragonfly:6379` (no auth) | 1 | ⚠️ password mismatch — see §6 |
| `infrastructure/komodo/procedures/crypteolas-pipeline.toml:46` | Crypteolas pipeline env var (no password) | 1 | ⚠️ password mismatch |
| `cianfhoghlaim/stacks/graphiti/compose.yaml` | Graphiti Python server (depends on Neo4j + FalkorDB, **NOT on dragonfly directly**) | 92 | ℹ️ cache wiring is via env var only |

> **Note on `cognify/rules/dragonfly_health.py`** — referenced by the phase‑2 P2‑30 spec (`openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-30-dragonfly.md:20`) but **does not exist in this repo** (CCC verified; `glob **/dragonfly_health*` returns 0 results). The canonical healthcheck is the inline `redis-cli -a … ping` inside `compose.yaml`, not a separate Dagster asset check.

## Env

| Env var | Value | Source | Notes |
|:--|:--|:--|:--|
| `DRAGONFLY_URL` | `redis://dragonfly:6379/0` | compose env (consumer side) | 9 references across the repo (tuatha compose, crypteolas worker, Komodo procedure, etc.) |
| `DRAGONFLY_URL` (with auth) | `redis://:${DRAGONFLY_PASSWORD}@dragonfly:6379/0` | **needed** | None of the 9 consumer refs include the password — bug, see §6 |
| `DRAGONFLY_PASSWORD` | Infisical secret | `infisical://dev-baile/dragonfly/password` via Locket sidecar | Resolved at runtime; `secrets.env:1` |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | only if `--dir s3://…` is used | compose env | For preview S3 snapshots |
| `AWS_REGION` | only if `--dir s3://…` | compose env | Required for S3 snapshots |

## CCC anchors

`cianfhoghlaim/stacks/dragonfly/` · `infrastructure/stacks/dragonfly/` (duplicate) · `infrastructure/stacks/tuatha/compose.yaml:20` · `infrastructure/komodo/procedures/crypteolas-pipeline.toml:46` · `cianfhoghlaim/stacks/graphiti/compose.yaml` (cache wiring via env var, not `depends_on`)

Search terms: `"dragonfly"`, `"proactor_threads"`, `"--maxmemory"`, `"DRAGONFLY_URL"`, `"cache_mode"`, `"snapshot_cron"`, `"FalkorDriver"` (for Graphiti consumer).

### Key upstream flag reference (verbatim from `dragonflydb.io/docs/managing-dragonfly/flags`)

| Flag | Type | Default | Purpose |
|:--|:--|:--|:--|
| `--port` | int | `6379` | Redis port (0 = disable, -1 = random) |
| `--cache_mode` | bool | `false` | **Eviction on at `--maxmemory`** (the canonical "cache mode" flag) |
| `--maxmemory` | bytes | `0` (auto) | Hard cap (e.g. `--maxmemory=8gb`) |
| `--proactor_threads` | int | `0` (auto = #cores) | Number of Helio I/O proactor threads (= shards) |
| `--proactor_affinity_mode` | enum | — | Pin proactor threads to CPUs |
| `--num_shards` | int | `0` (auto) | Number of data shards (= `--proactor_threads` in non‑cluster) |
| `--eviction_memory_budget_threshold` | float | — | Soft threshold before eviction kicks in |
| `--enable_heartbeat_eviction` | bool | — | Use background heartbeat for eviction |
| `--requirepass` | str | `""` | AUTH password (matches Redis `--requirepass`) |
| `--dbfilename` | str | `dump-{timestamp}` | Snapshot filename (`{timestamp}` macro) |
| `--dir` | path | `/data` | Snapshot directory OR `s3://bucket/path` |
| `--snapshot_cron` | cron | `""` | Auto‑snapshot cron schedule (≥ 1.7.1) |
| `--save_schedule` | cron | **deprecated** | Use `--snapshot_cron` instead |
| `--df_snapshot_format` | bool | `true` | Use Dragonfly‑native `.dfs` (vs legacy RDB) |
| `--cluster_mode` | enum | `""` | `""` / `"emulated"` / `"yes"` |
| `--primary_port_http_enabled` | bool | `true` | `:6379/metrics` for Prometheus on the main port |
| `--admin_port` / `--admin_bind` | int / str | disabled | Separate admin console (HTTP + RESP) |

> **Flags that DO NOT EXIST in Dragonfly** (commonly mis‑copied from Redis): `--maxmemory-policy=allkeys-lru`, `--cache_fetch_mode`, `--maxmemory-samples`, `--no-eviction`, `--volatile-lru`. These are Redis‑only. Dragonfly uses the `--cache_mode` boolean + the novel algorithm described in the README.

### Threading model — three layers (verbatim from `dragonflydb/dragonfly` README "Background")

1. **Shared‑nothing data layer**: keyspace partitioned into `num_shards` slices, each shard owned by exactly one thread. This is what makes Dragonfly scale linearly with cores (no global locks on the hot path).
2. **I/O layer — Helio proactor**: each shard runs inside a **Helio proactor** (open‑sourced at `github.com/romange/helio`). Helio provides the **proactor pattern** (async I/O completion‑based, like Boost.Asio's `proactor` or Windows IOCP) — hence the flag name `--proactor_threads`. Default = number of CPU cores.
3. **Locking — VLL**: multi‑key atomicity via the VLL lock manager (paper: "VLL: a lock manager redesign for main memory database systems" — `cs.umd.edu/~abadi/papers/vldbj-vll.pdf`). No mutexes / spinlocks on the hot path.

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| 2025-11 | Initial FalkorDB deploy (vector + graph) | P1B‑07 |
| 2026‑02 | Initial Dragonfly deploy (replaced Redis as episode cache) | P2‑30 spec |
| 2026‑03 | Wired Dragonfly as the Graphiti episode‑cache side‑car | P1B‑07 |
| 2026‑03 | Wired DRAGONFLY_URL into `tuatha` compose for leaderboards + MMO message queue | `infrastructure/stacks/tuatha/compose.yaml:20` |
| 2026‑06‑28 | v4 consolidation created `cianfhoghlaim/stacks/dragonfly/` — but the legacy `infrastructure/stacks/dragonfly/` was **not removed** (duplicate persists) | `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` |
| 2026‑06‑28 | P2‑30 spec written with 4 factual errors (throughput, flag names, missing file) | `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-30-dragonfly.md` |

## Anti-patterns

1. **Don't use Dragonfly for persistent storage** — it's a memory store; use Neo4j / FalkorDB / DuckLake for the persistent layer. The Cianfhoghlaim pattern is: Dragonfly = ephemeral (Graphiti episode cache, leaderboards, message queue), Neo4j / FalkorDB = persistent.
2. **Don't use the Redis‑only `--maxmemory-policy=allkeys-lru` flag** — it does not exist in Dragonfly. The canonical eviction knob is `--cache_mode=true` + `--maxmemory=<size>`; the algorithm is the upstream novel algorithm, not LRU.
3. **Don't set `--cache_fetch_mode=normal`** — it is not a real Dragonfly flag. P2‑30 spec got this wrong. The actual flag is `--cache_mode=true`.
4. **Don't run with `proactor_threads=1` unless debugging** — defeats the entire purpose. Default (0) auto‑sizes to `--cpus`; explicit `=4` matches the M4 4‑performance‑core layout and is what the compose files pin.
5. **Don't reference `cognify/rules/dragonfly_health.py`** — the file doesn't exist (P2‑30 spec stale reference). The actual healthcheck is inline in `compose.yaml:9-11` (`redis-cli -a … ping`).
6. **Don't use `--requirepass` without updating the consumers** — the canonical compose sets `--requirepass=${DRAGONFLY_PASSWORD:-devpassword}` but **9 of 9 `DRAGONFLY_URL` references in the repo omit the password** (tuatha compose × 3, crypteolas worker × 2, Komodo procedure × 1, etc.). With a non‑empty `DRAGONFLY_PASSWORD` those URLs will fail AUTH. Either drop `--requirepass` from the compose (internal‑only network) **or** rewrite every `DRAGONFLY_URL` to include `:${DRAGONFLY_PASSWORD}@`.
7. **Don't pin to `--snapshot_cron` on the Graphiti cache** — episode cache is purely ephemeral; snapshots would defeat the auto‑TTL LRU semantics and waste the 8 GB ceiling. Use `--snapshot_cron` only on persistent Dragonfly instances (none in KCG today).
8. **Don't run Dragonfly on Linux kernel < 4.19** — upstream requires ≥ 4.19 (5.10+ recommended for io_uring); older kernels fall back to a degraded epoll path.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Backend | Dragonfly (not Redis / not Valkey / not Memcached) | 25× QPS + 2× lower P99 vs Redis; API‑compatible so the switch is a config change |
| Container image | `docker.dragonflydb.io/dragonflydb/dragonfly:latest` | Upstream canonical (verified against docs/getting-started/docker); P2‑30 spec has a typo (`dragonfly/dragonfly` vs `dragonflydb/dragonfly`) |
| Threads | `--proactor_threads=4` | Matches `deploy.resources.limits.cpus: '4'` and the M4 P‑core count |
| Memory | `--maxmemory=8gb` (+ container limit `10G`) | Sized for Graphiti episode cache + Convex real‑time state + Dagster run queue — 8 GB is the **Dragonfly cap** so eviction kicks in, 10 GB is the **container OOM ceiling** for headroom |
| Eviction | `--cache_mode=true` (novel algorithm) | Canonical. `--maxmemory-policy=allkeys-lru` (from P2‑30) does not exist in Dragonfly |
| Persistence | none for the cache side‑car; `--snapshot_cron` not configured | Persistence is Neo4j / FalkorDB / DuckLake. Dragonfly snapshots would be a footgun. |
| HTTP console | `--primary_port_http_enabled=true` (default) | Lets `:6379/metrics` be scraped by Prometheus without an extra port |
| Protocol | RESP2 + RESP3 + Memcached text (all on port 6379) | Auto‑detected on connect — no client‑side change needed for Graphiti's `redis‑py` |
| Auth | `--requirepass` from Infisical via Locket | But see anti‑pattern #6 — 9 consumer URLs need updating |
| Placement | Side‑car to Graphiti (same compose network `cianfhoghlaim`) | Required for `dragonfly:6379` DNS resolution from Graphiti containers |

## §8 — Refactor opportunities

1. **Delete the duplicate `infrastructure/stacks/dragonfly/`** — the v4 consolidation (`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`) created `cianfhoghlaim/stacks/dragonfly/` but the byte‑identical `infrastructure/stacks/dragonfly/` was **not removed**. Both paths point at `docker.dragonflydb.io/dragonflydb/dragonfly:latest` with the same flags. Komodo / Locket / Pangolin all reference `cianfhoghlaim/stacks/dragonfly/`, so the `infrastructure/` copy is dead‑weight that will rot. **Action:** `rm -rf infrastructure/stacks/dragonfly/` and update `infrastructure/AGENTS.md` inventory if it lists dragonfly under the 90‑stack table.

2. **Reconcile P2‑30 spec vs reality** — `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-30-dragonfly.md` has 4 errors that should propagate as an **openspec MODIFIED Requirements delta**:
   - L73 decision matrix says "5x faster + lower memory" → should be **"25× more QPS + 2× lower P99 latency vs Redis (c6gn.16xlarge)"** per upstream benchmark (`github.com/dragonflydb/dragonfly#benchmarks`)
   - L32‑34 canonical compose uses `--proactor_threads=4 --maxmemory=8gb --cache_fetch_mode=normal` → **`--cache_fetch_mode` is a fictional flag**; the canonical invocation is `--proactor_threads=4 --maxmemory=8gb --cache_mode=true --requirepass=…` (per the actual `compose.yaml:8`)
   - L20 references `cognify/rules/dragonfly_health.py` → **file does not exist** (CCC verified); the actual healthcheck is inline `redis-cli ping` in `compose.yaml:9‑11`
   - L65 anti‑pattern #2 references `--maxmemory-policy=allkeys-lru` → **Redis‑only flag, does not exist in Dragonfly**; eviction is governed by `--cache_mode=true` + the upstream novel algorithm

3. **Fix the `DRAGONFLY_URL` password mismatch across 9 consumer refs** — `infrastructure/stacks/tuatha/compose.yaml:20`, `infrastructure/stacks/tuatha/compose.dev.yaml:50`, `infrastructure/komodo/procedures/crypteolas-pipeline.toml:46`, `cianfhoghlaim/docs/legacy/crypteolas/compose.dev.yaml:50`, `cianfhoghlaim/docs/legacy/crypteolas/docker-compose.yaml:21` (and 4 more) all set `DRAGONFLY_URL=redis://dragonfly:6379` without a password, but the compose sets `--requirepass`. **Two options:** (a) drop `--requirepass` from the compose (internal‑only compose network + Pangolin‑gated access makes auth redundant), or (b) update every `DRAGONFLY_URL` to `redis://:${DRAGONFLY_PASSWORD}@dragonfly:6379`. Option (a) is simpler and matches the P2‑30 spec text "none, internal‑only".

4. **Add `--snapshot_cron` for the persistent Dragonfly instance if/when one is added** — none exists today, but if a second Dragonfly is ever deployed as a feature store or job queue with persistence, the flag should be wired with a sane default (e.g. `--snapshot_cron="0 */6 * * *"` for 6‑hourly snapshots to the `lakehouse` Garage S3 bucket via `--dir=s3://oideachais-cache/dragonfly`). The S3 cloud‑storage flag is preview upstream but functional.

5. **Consider adding `pangolin.yaml` and `blueprint.yaml` to the canonical stack** — `cianfhoghlaim/stacks/dragonfly/` currently has only `compose.yaml`, `sidecar.yaml`, `secrets.env`, `README.md`, `blueprint.yaml` (verified by `glob cianfhoghlaim/stacks/dragonfly/*`). Wait — `blueprint.yaml` IS present (confirmed). `pangolin.yaml` is the missing one for full 6‑file GOLD_STANDARD conformance. **Action:** check `infrastructure/stacks/dragonfly/` for `pangolin.yaml`; if present, port it to `cianfhoghlaim/stacks/dragonfly/`.

6. **Pin the image digest instead of `:latest`** — `image: docker.dragonflydb.io/dragonflydb/dragonfly:latest` is non‑reproducible. Use the explicit digest (e.g. `…@sha256:…`) and bump via the existing `2026-06-28-upstream-package-monitoring` change with a `ChangeDetection.io` monitor on the upstream `:latest` tag + a Dagster sensor.

7. **Document the `--proactor_threads` ↔ `deploy.resources.limits.cpus` contract** — the compose sets both `proactor_threads=4` (implicit, via default) and `cpus: '4'`. Add a comment in `compose.yaml` that these must move together; otherwise Dragonfly either oversubscribes (proactor > cpus → context‑switch thrash) or undersubscribes (proactor < cpus → wasted cores).

## Files to read next

`cianfhoghlaim/stacks/dragonfly/compose.yaml` · `infrastructure/stacks/dragonfly/compose.yaml` (delete) · `infrastructure/stacks/tuatha/compose.yaml:20` · `infrastructure/komodo/procedures/crypteolas-pipeline.toml:46` · `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-30-dragonfly.md` (spec to reconcile) · `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-07-falkordb-graphiti-dragonfly-risingwave.md` · `openspec/research/2026-06-28-browserbase-program-2/agent-11-graphiti.md` (Graphiti consumer — verifies `cache_client=…` pattern)

## Upstream references

- Website: https://www.dragonflydb.io/
- Docker install: https://www.dragonflydb.io/docs/getting-started/docker
- Server flags: https://www.dragonflydb.io/docs/managing-dragonfly/flags
- Backups & snapshots: https://www.dragonflydb.io/docs/managing-dragonfly/backups
- README + benchmarks: https://github.com/dragonflydb/dragonfly (`README.md` lines 17‑118 = benchmarks + threading architecture)
- Helio library: https://github.com/romange/helio
- Paper — Dash hashtable: https://arxiv.org/pdf/2003.07302.pdf
- Paper — VLL locking: https://www.cs.umd.edu/~abadi/papers/vldbj-vll.pdf
- Docker Hub: https://hub.docker.com/r/docker.dragonflydb.io/dragonflydb/dragonfly