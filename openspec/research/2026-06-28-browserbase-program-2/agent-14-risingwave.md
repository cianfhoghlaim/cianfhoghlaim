# Agent 14 — RisingWave (Streaming SQL Database)

**Date:** 2026-06-28
**Phase:** Program 2 / Wave 1 — Light Packages (Infrastructure)
**Subagent:** research
**Credit budget:** ~200 (used ~6 via Firecrawl fallbacks; 1 BrowserBase session started)

## TL;DR

RisingWave is the **cloud-native streaming SQL database** that Cianfhoghlaim
uses for sub-second CDC from PlanetScale Postgres → Iceberg. Per the docs it
**"replaces the traditional stack (Debezium + Kafka + Flink + serving DB)
with a single PostgreSQL-compatible system"** (llms.txt:3). It is wire-compatible
with PostgreSQL on port 4566 (default db `dev`, user `root`, no password) — every
existing pgx/psycopg2/JDBC client "just works." Materialized views are
**incrementally maintained automatically** (no `REFRESH MATERIALIZED VIEW` —
that DDL doesn't exist), and state lives in object storage (~100× cheaper
than RAM).

**Critical facts vs current KCG stack:**
- The KCG `infrastructure/stacks/risingwave/compose.yaml:17` runs a **single
  `risingwave` container in all-in-one mode** (Serving + Streaming + Meta +
  Compactor in one process). The official compose splits these into 4 services
  (`compute-node`, `meta-node`, `compactor-node`, `frontend-node`). **All-in-one
  is "not recommended for production"** (deploy/risingwave-docker-compose:5).
- **RisingWave 3.0.0** was released **3 weeks ago (2026-06-11)**. The current
  compose pins `:latest` so it is on v3.
- **Iceberg v3 exactly-once commit** support shipped **4 days ago (2026-06-24,
  PR #25708)** — this is brand-new and we should adopt it.
- **Native PostgreSQL CDC** (`postgres-cdc` connector) requires **no Debezium**
  when using shared sources — Postgres 10-17, RDS, Aurora, Neon, Supabase
  all supported (ingestion/sources/postgresql/pg-cdc).
- **Premium features** (`auto.schema.change` for Iceberg sinks, exactly-once
  Iceberg v3 commit) require **RisingWave Cloud or Enterprise** — this is a
  KCG blocker for the auto-schema-change Iceberg sink in our init.d/01_init.sql.

## Code

| Path | Purpose | Source verified |
|:--|:--|:--|
| `infrastructure/stacks/risingwave/compose.yaml` | KCG single-node all-in-one stack | yes |
| `infrastructure/stacks/risingwave/init.d/01_init.sql` | 6 event streams + 2 commented CDC + 1 commented Iceberg sink | yes |
| `infrastructure/stacks/risingwave/blueprint.yaml` | Pangolin private resources `risingwave.cianfhoghlaim.ie` (port 4566) + `risingwavedb.cianfhoghlaim.ie` (port 5691) | yes |
| `infrastructure/stacks/risingwave/README.md` | Quick-start, env vars, ports | yes |
| `infrastructure/stacks/risingwave/sidecar.yaml` | Locket sidecar | yes |
| `infrastructure/stacks/risingwave/secrets.env` | Infisical-ref template | yes |
| `cianfhoghlaim/stacks/risingwave/compose.yaml` | v4 duplicate (post 2026-06-28 consolidation) | yes — identical to infra/ copy |
| `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:57-74` | Canonical "RisingWave + olake is the CDC stack" requirement | yes |
| `docs/RESEARCH_REPORT.md:56-58` | "CDC stack = RisingWave (streaming, sub-second) + olake (batch, 15-min)" | yes |

**Canonical multi-node RisingWave compose (from upstream
`docker-compose-distributed.yml`)** — **NOT what KCG currently runs**:

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
    environment: {RUST_BACKTRACE: "1"}
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

**Canonical KCG single-node all-in-one (current `infrastructure/stacks/risingwave/compose.yaml:17-53`):**

```yaml
risingwave:
  image: risingwavelabs/risingwave:latest
  container_name: risingwave
  ports:
    - "4566:4566"   # PostgreSQL wire protocol
    - "5690:5690"   # Meta service
    - "5691:5691"   # Dashboard
  environment:
    RW_STATE_STORE_URL: "hummock+minio://minio:9201/hummock"
    RW_OBJECT_STORE_URL: "minio://minio:9201/hummock"
    RW_DATA_DIR: /risingwave/data
    RW_META_ADDR: "0.0.0.0:5690"
    RW_COMPACTOR_ADDR: "0.0.0.0:6660"
    RW_DATABASE_URL: ${RISINGWAVE_DATABASE_URL}
    RW_MEMORY_MODE: "true"   # v2.6+ saves disk + latency at our scale
```

**Canonical CDC source (`ingestion/sources/postgresql/pg-cdc`):**

```sql
CREATE SOURCE shared_source WITH (
    connector='postgres-cdc',
    hostname='localhost', port='5432',
    username='your_user', password='your_password',
    database.name='your_database',
    schema.name='public'
);
CREATE TABLE my_table (
    id INT PRIMARY KEY, name VARCHAR
) FROM shared_source TABLE 'public.my_upstream_table';
```

**Canonical Iceberg sink (`iceberg/deliver-to-iceberg`):**

```sql
CREATE SINK my_iceberg_sink FROM processed_events
WITH (
    connector = 'iceberg',
    type = 'append-only',                        -- or 'upsert'
    warehouse.path = 's3://my-data-lake/warehouse',
    database.name = 'analytics',
    table.name = 'processed_user_events',
    create_table_if_not_exists = 'true',
    catalog.type = 'glue',                       -- 'rest' | 'hive' | 'jdbc' | 'glue'
    s3.access.key = 'your-access-key',
    s3.secret.key = 'your-secret-key',
    s3.region = 'us-west-2',
    partition_by = 'partition_by_column_name',
    is_exactly_once = 'true',                    -- default; requires sink_decouple
    commit_checkpoint_interval = 60,             -- default 60s
    auto.schema.change = 'true'                  -- premium feature; requires Iceberg v3 EO
);
```

**Canonical subscription push (no polling, no message broker — `get-started/recipes/subscription-push`):**

```sql
CREATE SUBSCRIPTION my_sub FROM fraud_signals WITH (retention = '1D');
DECLARE cur SUBSCRIPTION CURSOR FOR my_sub;
FETCH NEXT FROM cur WITH (timeout = '5s');       -- blocks up to 5s, returns changed rows
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `RISINGWAVE_FRONTEND_URL` | `http://risingwave:4566` | inferred from compose (`compose.yaml:22`) |
| `RISINGWAVE_DATABASE_URL` | (Infisical) `postgres-connector://...` | `compose.yaml:33` → `secrets.env` |
| `RISINGWAVE_MINIO_USER` | `risingwave` | `compose.yaml:64` |
| `RISINGWAVE_MINIO_PASSWORD` | (Infisical) | `compose.yaml:65` |
| `RW_PORT` | `4566` | `infrastructure/stacks/risingwave/README.md:36` |
| `RW_META_PORT` | `5690` | `README.md:37` |
| `RW_DASHBOARD_PORT` | `5691` | `compose.yaml:24` |
| `KAFKA_BROKERS` | (no Kafka in our stack — RisingWave subsumes it) | `README.md:38` (legacy) |

**Connect string:** `postgresql://root@risingwave:4566/dev` (no password by default; user `root`)

## CCC anchors

- `infrastructure/stacks/risingwave/compose.yaml` (single-node all-in-one)
- `infrastructure/stacks/risingwave/init.d/01_init.sql` (6 event streams + commented CDC + commented Iceberg sink)
- `infrastructure/stacks/risingwave/blueprint.yaml` (Pangolin private resources)
- `infrastructure/stacks/risingwave/README.md`
- `infrastructure/stacks/olake/compose.yaml` (sibling batch CDC stack)
- `infrastructure/stacks/lakehouse/compose.yaml` (Garage S3 — sink target)
- `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:57-74` (canonical CDC stack requirement)
- `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-07-falkordb-graphiti-dragonfly-risingwave.md` (sibling research — RisingWave → FalkorDB path)

Search terms: `"risingwave"`, `"compute-node"`, `"meta-node"`, `"iceberg-sink"`, `"hummock+minio"`, `"postgres-cdc"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-12 | Initial RisingWave deploy (Kafka → RisingWave refactor) — per P2-31 |
| 2026-02 | Added Iceberg sink connector (per P2-31) |
| 2026-04 | Wired to olake for CDC redundancy (per P2-31) |
| 2025-12-01 | Upstream: DataFusion engine for Iceberg batch queries (PR #23860) — affects OLAP path |
| 2026-06-11 | Upstream: RisingWave **v3.0.0 released** (3 weeks ago; pinned `:latest`) |
| 2026-06-24 | Upstream: **Iceberg v3 exactly-once commit** (PR #25708, 4 days old) — premium, requires Enterprise |
| 2026-06-26 | Upstream: rate limit on snapshot backfill chunks (PR #26022) — affects large CDC backfills |
| 2026-06-28 | v4 consolidation: duplicate stack at `cianfhoghlaim/stacks/risingwave/` |

## Anti-patterns

1. **Don't run all-in-one in production.** Current KCG compose uses
   single `risingwave` container. Upstream docs explicitly state this
   **"is not recommended for production"** (`deploy/risingwave-docker-compose:5`)
   because failover and resource management are absent. Use multi-node compose
   (`docker-compose-distributed.yml`) or Kubernetes Helm/Operator.

2. **Don't use `REFRESH MATERIALIZED VIEW`** — it doesn't exist in RisingWave.
   MVs are **incrementally maintained automatically** (`llms.txt:14`). If you
   see this DDL in agent code, it's a Postgres habit that needs translating.

3. **Don't use `UPDATE`/`DELETE` on a `CREATE SOURCE`.** Sources are read-only.
   Use `CREATE TABLE` with a connector for mutable data (llms.txt:15).

4. **Don't skip watermarks on time-windowed MVs.** Without
   `WATERMARK FOR event_time AS event_time - INTERVAL '5 seconds'`, windows
   never close (`llms.txt:17`). Our `audio_events` table in
   `init.d/01_init.sql:108-111` correctly uses `APPEND ONLY` + watermark.

5. **Don't use `NOW()` in an MV without a temporal filter.** This triggers
   **full recomputation on every barrier** (1s by default). Always pair with
   `WHERE col > NOW() - INTERVAL '...'` (llms.txt:19).

6. **Don't skip the compactor node.** Even in single-node all-in-one mode the
   compactor thread is running. In multi-node, dropping the compactor causes
   Iceberg file pile-up because LSM-tree L0 never compacts. Recommended ratio
   **Compute:Compactor = 2:1** (4:1 in write-heavy workloads) per
   `get-started/architecture` §Compute-Compactor.

7. **Don't use `:latest` in production.** Upstream releases every few weeks
   (121 releases to date). Pin to a specific minor version (`v3.0.0`) and bump
   deliberately.

8. **Don't reach for premium Iceberg features on OSS.** `auto.schema.change`
   for Iceberg sinks (the v3 exactly-once commit variant) and the new
   `auto.schema.change = 'true'` CDC source option are explicitly tagged
   "PREMIUM FEATURE" in the upstream docs — they require Cloud or Enterprise.

9. **Don't assume streaming CDC will backfill in real-time.** The
   `snapshot.batch_size` (default 1000) and `backfill.parallelism` (default 0,
   i.e., disabled) govern how fast the initial snapshot completes. For large
   tables, set `backfill.parallelism = '4'` and `backfill.num_rows_per_split = '50000'`
   (`ingestion/sources/postgresql/pg-cdc`).

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Streaming engine | RisingWave (not Kafka Streams / Flink) | SQL-native, Postgres-compatible, no Debezium required |
| CDC source | `postgres-cdc` shared source + `CREATE TABLE FROM SOURCE` | Native, supports PG 10-17 + Neon/Supabase/RDS |
| Sink target | Iceberg catalog (REST/Glue/JDBC) | Same catalog as olake — avoids double-write |
| Default mode | `merge-on-read` (Iceberg EO + sink decoupling) | Default; gives exactly-once with no perf hit |
| Subscription for agents | `CREATE SUBSCRIPTION ... WITH (retention='1D')` | No polling, no message broker — agents subscribe directly |
| Deployment | Single-node all-in-one (dev) → multi-node distributed (prod) | Per upstream docs; HA via Kubernetes Helm |
| Object store | MinIO (dev) → Garage S3 (prod) | Already in `lakehouse` stack |
| Meta store | Postgres (compose default) | Persistent meta survives container restarts |
| MV strategy | Cascading MVs (hourly → daily) | Our `init.d/01_init.sql:34-51` demonstrates |
| Compactor ratio | 2:1 (Compute:Compactor) in steady state; 1:8 write-heavy | Per `get-started/architecture` |
| Memory | `RW_MEMORY_MODE = "true"` for our scale | KCG deviation from upstream — saves disk |
| Connection string | `postgresql://root@risingwave:4566/dev` (no password) | Port 4566 ≠ 5432 — common confusion |

## §8 Refactor opportunities

1. **Split into 4-service multi-node compose.** Current `compose.yaml:17`
   runs all-in-one. Add `risingwave-compute`, `risingwave-meta`,
   `risingwave-compactor`, `risingwave-frontend` as separate services per
   upstream `docker-compose-distributed.yml`. Add 3:1 CPU:Memory ratio on
   compute per `get-started/architecture` §CPU-Memory.

2. **Pin to `v3.0.0` instead of `:latest`.** Released 3 weeks ago (June 11,
   2026). Avoids surprise upgrades; allows deliberate bumps.

3. **Adopt Iceberg v3 exactly-once commit.** PR #25708 merged 4 days ago.
   Requires RisingWave Enterprise/Cloud for the premium `auto.schema.change`
   on Iceberg sinks. Open an RFC for license decision before adopting.

4. **Wire Iceberg sink to Garage S3.** `init.d/01_init.sql:145-155` has the
   commented Iceberg sink pointing at `http://lakehouse-garage:3900` — uncomment
   it and add the 2:1 compactor ratio compute nodes to keep up with compaction.

5. **Add a Subscription cursor for agent event push.** `get-started/recipes/subscription-push`
   shows how `CREATE SUBSCRIPTION` + `DECLARE cur SUBSCRIPTION CURSOR` +
   `FETCH NEXT FROM cur WITH (timeout = '5s')` lets agents receive
   pushed events without polling. Replace the current polling pattern in
   the agent stack.

6. **Add CDC source for the 5 internal Postgres databases.**
   `init.d/01_init.sql:124-138` has the commented template for
   `litellm_model_registry_cdc` and `langfuse_traces_cdc`. Extend to:
   `oideachais_db_cdc`, `meaisinfhoghlaim_db_cdc`, `langfuse_postgres_cdc`,
   `litellm_db_cdc`, `better_auth_db_cdc`. Set `auto.schema.change = 'true'`
   only on Enterprise (premium).

7. **Add Iceberg engine for batch OLAP.** Per `get-started/architecture`,
   `engine = 'iceberg'` on `CREATE TABLE` routes batch queries through
   DataFusion. Currently our batch path is MotherDuck — Iceberg engine in
   RisingWave would give us "single SQL interface, both streaming MVs and
   Iceberg lakehouse queries" without a roundtrip to MotherDuck.

8. **Replace the duplicate stack.** `infrastructure/stacks/risingwave/`
   and `cianfhoghlaim/stacks/risingwave/` are byte-identical. The v4
   consolidation change should symlink or delete the older copy.

9. **Add a `subscription-push` example to init.d** mirroring the
   `get-started/recipes/subscription-push` pattern — gives agents a
   Postgres-protocol push primitive without standing up a separate broker.

10. **Add `watermark` on all `event_time` columns** in init.d. Currently only
    `audio_events` (init.d/01_init.sql:108-111) has a watermark; the other
    5 event streams will fail to emit on time-windowed MVs.

## Files to read next

- `infrastructure/stacks/risingwave/init.d/01_init.sql` (155 lines — full event stream + CDC + sink template)
- `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md` (the canonical CDC stack requirement)
- `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-07-falkordb-graphiti-dragonfly-risingwave.md` (sibling — RisingWave → FalkorDB path via Iceberg)
- `infrastructure/stacks/lakehouse/compose.yaml` (Garage S3 sink target)
- Upstream: https://github.com/risingwavelabs/risingwave (Rust 91.8%, Java 3.5%, Python 2.6%, 9.1k stars, 121 releases, Apache-2.0)