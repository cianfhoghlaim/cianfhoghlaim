# P2-29 — risingwave (Phase 2, Infrastructure)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** infrastructure

## TL;DR

RisingWave is the **streaming SQL database** used for change-data-capture (CDC) from PlanetScale Postgres → Iceberg catalog. It complements olake for streaming CDC use cases (sub-second latency) where olake's batch mode (minutes) is too slow.

The canonical Cianfhoghlaim pattern: RisingWave for streaming CDC + Iceberg sink; olake for batch CDC + Iceberg sink. Both write to the same Iceberg catalog.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/risingwave/compose.yaml` | RisingWave cluster (compute + meta + compactor + frontend) |
| `stacks/risingwave/blueprint.yaml` | Pangolin private-resource |
| `cognify/rules/risingwave_streams.py` | Lists 3 active streams |

**Canonical RisingWave compose**:

```yaml
services:
  risingwave-compute:
    image: risingwavelabs/risingwave:latest
    command: "compute-node --config-path /risingwave.toml"
    container_name: risingwave-compute
    ports: ["5688:5688"]
  risingwave-meta:
    image: risingwavelabs/risingwave:latest
    command: "meta-node --config-path /risingwave.toml"
    container_name: risingwave-meta
    ports: ["5690:5690"]
    environment:
      RUST_BACKTRACE: "1"
  risingwave-compactor:
    image: risingwavelabs/risingwave:latest
    command: "compactor-node --config-path /risingwave.toml"
    container_name: risingwave-compactor
  risingwave-frontend:
    image: risingwavelabs/risingwave:latest
    command: "frontend-node --config-path /risingwave.toml"
    container_name: risingwave-frontend
    ports: ["4566:4566"]
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `RISINGWAVE_FRONTEND_URL` | `http://risingwave-frontend:4566` | compose env |

## CCC anchors

`stacks/risingwave/` · `cognify/rules/risingwave_streams.py` · `stacks/lakehouse/`

Search terms: `"risingwave"`, `"compute-node"`, `"meta-node"`, `"iceberg-sink"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-12 | Initial RisingWave deploy (Kafka → RisingWave refactor) |
| 2026-02 | Added Iceberg sink connector |
| 2026-04 | Wired to olake for CDC redundancy |

## Anti-patterns

1. Don't use RisingWave for batch analytics — use MotherDuck
2. Don't run a single-node RisingWave in production — minimum 3 nodes (compute + meta + compactor)
3. Don't skip the compactor service — without it, Iceberg files pile up

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Streaming engine | RisingWave (not Kafka Streams) | SQL-native + Iceberg native |
| Sink | Iceberg catalog | Same as olake |
| Compute | 1 node (dev), 3+ nodes (prod) | HA |
| Retention | 7 days in streaming | Recent history only |
| Schema evolution | Auto (with Iceberg) | No manual migration |

## Files to read next

`stacks/risingwave/` · `cognify/rules/risingwave_streams.py`
