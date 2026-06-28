# P2-27 — dragonfly (Phase 2, Infrastructure)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** infrastructure

## TL;DR

Dragonfly is the **Redis-compatible in-memory store** used by Graphiti for the bi-temporal knowledge graph cache. It runs as a sidecar to Graphiti and exposes a Redis API for ephemeral state (recent episodes, embedding cache, lock contention).

The canonical Cianfhoghlaim pattern: Dragonfly is the **ephemeral layer** for Graphiti; the **persistent layer** is Neo4j (in graphiti stack).

## Code

| Path | Purpose |
|:--|:--|
| `stacks/dragonfly/compose.yaml` | Dragonfly service (port 6379) |
| `stacks/graphiti/compose.yaml` (depends on dragonfly) | Graphiti uses Dragonfly as cache |
| `cognify/rules/dragonfly_health.py` | Dagster asset check for Dragonfly memory usage |

**Canonical Dragonfly compose**:

```yaml
dragonfly:
  image: docker.dragonflydb.io/dragonfly/dragonfly:latest
  container_name: dragonfly-cache
  restart: unless-stopped
  ports:
    - "6379:6379"
  command:
    - "--proactor_threads=4"
    - "--maxmemory=8gb"
    - "--cache_fetch_mode=normal"
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 30s
    timeout: 5s
    retries: 3
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `DRAGONFLY_URL` | `redis://dragonfly:6379/0` | compose env |
| `DRAGONFLY_PASSWORD` | (none, internal-only) | compose env |

## CCC anchors

`stacks/dragonfly/` · `stacks/graphiti/compose.yaml` · `cognify/rules/dragonfly_health.py`

Search terms: `"dragonfly"`, `"proactor_threads"`, `"--maxmemory"`.

## Drift log

| Date | Event |
|:--|:--|
| 2026-02 | Initial Dragonfly deploy (replaced Redis) |
| 2026-03 | Wired to Graphiti as cache layer |

## Anti-patterns

1. Don't use Dragonfly for persistent storage — use Neo4j
2. Don't exceed 8 GB memory without enabling `--maxmemory-policy=allkeys-lru`
3. Don't use Dragonfly without `--proactor_threads` — defaults to single-threaded

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Backend | Dragonfly (not Redis) | 5x faster + lower memory |
| Memory | 8 GB | Enough for Graphiti episode cache |
| Threads | 4 (proactor) | Async I/O |
| Eviction | `allkeys-lru` | Bounded memory |
| Persistence | None (cache only) | Use Neo4j for persistence |

## Files to read next

`stacks/dragonfly/` · `stacks/graphiti/compose.yaml`
