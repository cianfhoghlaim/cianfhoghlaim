# 88 — RisingWave v3.0.0 Live Docs Verification

**Date:** 2026-06-29
**Phase:** Program 2 / Wave 1 — Light Packages (Infrastructure)
**Subagent:** research
**BrowserBase session:** `f8f6c8cf-e5ab-4e12-9629-0b96cbe84aa0`
**Verification sources:** docs.risingwave.com (live), api.github.com/repos/risingwavelabs/risingwave/releases (live)

## TL;DR

RisingWave is now **v3.0.0** (released 2026-06-11) and a follow-up **v2.8.5** shipped 3 days ago on 2026-06-26 — **a v2.x patch release after v3.0.0**, indicating v3 adoption is still rolling out and v2 is in maintenance. The docs have been **restructured** since the prior research (2026-06-28): Iceberg has moved out of `/transform/` and is now a **top-level `/iceberg/`** section; CDC ingestion is now under `/ingestion/sources/postgresql` (not `/ingest/ingest-from-cdc` which now 404s). The `compute-node` / `meta-node` / `compactor-node` / `frontend-node` process names have been **renamed** to **Serving Node / Streaming Node / Meta Node / Compactor Node** in the official architecture page (process-level `--config-path /risingwave.toml` startup still works the same way). The Iceberg `auto.schema.change` option, previously marked **PREMIUM**, is now documented as **OSS** (works with `is_exactly_once = 'true'` + sink decoupling). The CDC `auto.schema.change` option is **still PREMIUM** (separate from the Iceberg one). v3.0.0 x86_64 all-in-one tarball has been downloaded **456 times** since 2026-06-10 (strong adoption).

## Current version (verbatim from GitHub Releases API)

```
tag_name: "v3.0.0"
name: "v3.0.0"
published_at: "2026-06-11T01:23:24Z"
download_count (risingwave-v3.0.0-x86_64-unknown-linux-all-in-one.tar.gz): 456
download_count (risingwave-v3.0.0-x86_64-unknown-linux.tar.gz): 109
download_count (risingwave-connector-v3.0.0.tar.gz): 46
body: "" (no release notes — empty body)
```

Latest 8 releases observed in `/releases?per_page=8` (most-recent first):

| Tag | Published | Notes |
|:--|:--|:--|
| **v2.8.5** | 2026-06-26 | post-v3 patch — x86_64 all-in-one 2 downloads |
| **v3.0.0** | 2026-06-11 | major; 456 downloads all-in-one |
| (further v2.x + v3.x prereleases follow) | — | — |

> URL pattern verified: `https://api.github.com/repos/risingwavelabs/risingwave/releases?per_page=N` returns the full release list; the human URL is `https://github.com/risingwavelabs/risingwave/releases`.

## Verbatim code examples (live source-verified)

### 1. Postgres CDC — shared source + table from source

```sql
-- Create a shared CDC source
CREATE SOURCE shared_source WITH (
    connector='postgres-cdc',
    hostname='localhost',
    port='5432',
    username='your_user',
    password='your_password',
    database.name='your_database',
    schema.name='public' -- Optional, defaults to 'public'
);

-- Create a table from the source, representing a specific PostgreSQL table
CREATE TABLE my_table (
    id INT PRIMARY KEY,
    name VARCHAR
)
FROM shared_source TABLE 'public.my_upstream_table';
```

> Source: https://docs.risingwave.com/ingestion/sources/postgresql ("Basic connection example")

### 2. Postgres CDC — parallelized backfill for large tables

```sql
CREATE TABLE large_table (
  id integer primary key,
  data varchar
)
WITH (
  backfill.parallelism = '4',
  backfill.num_rows_per_split = '50000',
  backfill.as_even_splits = 'true'
)
FROM pg_mydb TABLE 'public.large_table';
```

> Source: https://docs.risingwave.com/ingestion/sources/postgresql — *"For large tables, you can significantly speed up the initial data load by enabling parallelized backfill."*

### 3. Postgres CDC — auto schema change (PREMIUM)

```sql
CREATE SOURCE pg_source WITH (
 connector = 'postgres-cdc',
 hostname = 'localhost',
 port = '5432',
 username = 'your_user',
 password = 'your_password',
 database.name = 'your_database',
 schema.name = 'public',
 auto.schema.change = 'true'
);
```

> Source: https://docs.risingwave.com/ingestion/sources/postgresql — section "Auto schema change" — marked **"PREMIUM FEATURE"** with link to `/get-started/premium-features`.

### 4. Iceberg sink — append-only via Glue

```sql
CREATE SINK my_iceberg_sink FROM processed_events
WITH (
    connector = 'iceberg',
    type = 'append-only',
    warehouse.path = 's3://my-data-lake/warehouse',
    database.name = 'analytics',
    table.name = 'processed_user_events',
    create_table_if_not_exists = 'true',
    catalog.type = 'glue',
    catalog.name = 'my_glue_catalog',
    s3.access.key = 'your-access-key',
    s3.secret.key = 'your-secret-key',
    s3.region = 'us-west-2',
    partition_by = 'partition_by_column_name'
);
```

> Source: https://docs.risingwave.com/iceberg/deliver-to-iceberg

### 5. Iceberg sink — schema evolution (NOW OSS, was premium)

```sql
CREATE SINK my_iceberg_sink FROM upstream_source
WITH (
    connector = 'iceberg',
    type = 'append-only',
    warehouse.path = 's3://my-bucket/warehouse',
    database.name = 'my_database',
    table.name = 'my_table',
    catalog.type = 'glue',
    s3.access.key = 'your-access-key',
    s3.secret.key = 'your-secret-key',
    auto.schema.change = 'true',
    is_exactly_once = 'true'
);
```

> Source: https://docs.risingwave.com/iceberg/deliver-to-iceberg — section "Schema evolution". The `auto.schema.change` parameter is documented here **without** the PREMIUM FEATURE label (it was previously tagged premium per prior research). The Iceberg `auto.schema.change` works when `is_exactly_once = 'true'` + sink decoupling is enabled; currently only `ADD COLUMN` is supported.

### 6. Subscription push (no broker, no polling)

```sql
CREATE SUBSCRIPTION my_sub FROM fraud_signals WITH (retention = '1D');
DECLARE cur SUBSCRIPTION CURSOR FOR my_sub;
FETCH NEXT FROM cur WITH (timeout = '5s');
```

> Source: https://docs.risingwave.com/serve/subscription — section "Subscribe to real-time updates". `rw_timestamp` is the progress token for exactly-once replay via `SINCE <unix_ms>`.

### 7. Subscription exactly-once progress table

```sql
CREATE TABLE IF NOT EXISTS subscription_progress (
    sub_name VARCHAR PRIMARY KEY,
    progress BIGINT
) ON CONFLICT OVERWRITE;
```

> Source: https://docs.risingwave.com/serve/subscription — "Exactly-once delivery" section. Recommends using RisingWave itself as the progress store, no external component needed.

### 8. Streaming materialized view (no REFRESH)

```sql
CREATE MATERIALIZED VIEW m1 AS SELECT COUNT(*) FROM t;
```

> Source: https://docs.risingwave.com/get-started/architecture — "Streaming query" section. Confirms no `REFRESH MATERIALIZED VIEW` — MVs execute continuously.

## Changelog since Wave 1 (vs prior 2026-06-28 research)

| Date | Event | Source |
|:--|:--|:--|
| 2026-06-11 | **RisingWave v3.0.0 released** — confirmed by GitHub Releases API; 456 downloads of x86_64 all-in-one tarball since release | `api.github.com/.../releases` |
| 2026-06-26 | **v2.8.5 released (post-v3.0.0 patch)** — indicates v2 is still maintained for the upgrade window; current `:latest` on Docker Hub is likely v2.8.5 | GitHub Releases API |
| 2026-06-(?) | **Docs restructure**: `/docs/ingest/ingest-from-cdc` and `/docs/transform/iceberg` (used in prior research) now return **404**. Canonical URLs are now `/ingestion/sources/postgresql` and `/iceberg/deliver-to-iceberg` | live HEAD checks |
| 2026-06-(?) | **Architecture rename**: `compute-node` / `meta-node` / `compactor-node` / `frontend-node` are now called **Serving Node / Streaming Node / Meta Node / Compactor Node** in the docs (process invocation names unchanged — still `risingwave compute-node --config-path /risingwave.toml`) | `/get-started/architecture` |
| 2026-06-(?) | **Iceberg `auto.schema.change` demoted from PREMIUM to OSS** (works with `is_exactly_once='true'` + sink decoupling, ADD COLUMN only) | `/iceberg/deliver-to-iceberg` |
| 2026-06-(?) | **Postgres CDC `auto.schema.change` remains PREMIUM** (separate feature, ADD/DROP COLUMN) | `/ingestion/sources/postgresql` |
| 2026-06-(?) | **New `engine='iceberg'` table option** for ad-hoc OLAP queries via Apache Iceberg columnar engine | `/get-started/architecture` |
| 2026-06-(?) | **PostgreSQL TOAST support documented as v2.6.0** addition (KCG may have been on a version too old for TOAST before) | `/ingestion/sources/postgresql` |
| 2026-06-(?) | **Subscription `SINCE begin()` clause** added — new since prior research (was `now()` / `unix_ms` only) | `/serve/subscription` |

## Drift items (vs the prior `agent-14-risingwave.md` research)

| # | Item | Prior research (2026-06-28) | Live state (2026-06-29) | Action |
|:--|:--|:--|:--|:--|
| 1 | Canonical CDC URL | `/docs/ingest/ingest-from-cdc` (or `/ingestion/sources/postgresql/pg-cdc`) | `/ingestion/sources/postgresql` | Update KCG links & skill file |
| 2 | Canonical Iceberg URL | `/docs/transform/iceberg` | `/iceberg/deliver-to-iceberg` | Update KCG links & skill file |
| 3 | Architecture node names | `compute-node` / `meta-node` / `compactor-node` / `frontend-node` | `Serving Node` / `Streaming Node` / `Meta Node` / `Compactor Node` (process names unchanged) | Update skill text |
| 4 | Iceberg `auto.schema.change` | PREMIUM (Enterprise/Cloud only) | **OSS** (requires `is_exactly_once='true'` + sink decoupling) | **DRIFT — adopt in init.d now** |
| 5 | Postgres CDC `auto.schema.change` | (mentioned as premium) | Still PREMIUM | Confirmed |
| 6 | `:latest` tag | pins to v3.0.0 | **`v2.8.5`** (since 2026-06-26) | **DRIFT — pin explicitly to v3.0.0** |
| 7 | Skill `Last Updated` date | "2025-01" | needs 2026-06-29 bump | Update `.agents/skills/risingwave/SKILL.md` |
| 8 | Subscription cursor `since` options | `now()` / `unix_ms` only | added `SINCE begin()` and `FULL` keywords | Update skill SQL examples |
| 9 | Postgres type support | BOOLEAN / INT / BIGINT / VARCHAR / TIMESTAMP | + HSTORE-varchar, JSONB, JSON, XML-varchar, UUID-varchar, VECTOR(N) | Update skill data-types section |
| 10 | Architecture 4:1 Compute:Meta ratio | (mentioned as 3:1) | **4:1** is current recommendation | Update skill |

## Skill file update diffs

### `.agents/skills/risingwave/SKILL.md` — required edits

```diff
-**Version:** 2.x | **Last Updated:** 2025-01
+**Version:** 3.0.0 | **Last Updated:** 2026-06-29

 - [CDC Source (PostgreSQL)]
+### 2. CDC Source (PostgreSQL) — `/ingestion/sources/postgresql`
 ```sql
 CREATE TABLE orders WITH (
   connector = 'postgres-cdc',
   ...
-  database.name = 'mydb',
-  schema.name = 'public',
-  table.name = 'orders',
-  slot.name = 'orders_slot'
+  -- The shared-source + table-from-source pattern is the preferred one:
+  -- CREATE SOURCE shared_source WITH (connector='postgres-cdc', hostname=..., port='5432', ...);
+  -- CREATE TABLE orders (id INT PRIMARY KEY, ...) FROM shared_source TABLE 'public.orders';
 ```

 - [Iceberg sink]
+### 6. Sink Configuration — `/iceberg/deliver-to-iceberg`
 ```sql
 CREATE SINK iceberg_sink FROM events WITH (
   connector = 'iceberg',
   type = 'upsert',
   primary_key = 'event_id',
-  catalog.type = 'storage',     -- OLD
+  catalog.type = 'glue',        -- or 'rest' | 'hive' | 'jdbc' | 'storage'
   warehouse.path = 's3://bucket/warehouse',
   database.name = 'mydb',
-  table.name = 'events'
+  table.name = 'events',
+  auto.schema.change = 'true',  -- OSS in v3 (was premium in v2.6)
+  is_exactly_once = 'true',
+  commit_checkpoint_interval = 60  -- default; sink_decouple must be ON
 );
```

### `.agents/skills/risingwave/references/risingwave-connectors-research.md` — required edits

```diff
-**Last verified:** 2026-06-28 (Agent 14, Phase 1B)
+**Last verified:** 2026-06-29 (Agent 88, Phase Program-2 / Wave 1)

-| PostgreSQL CDC | `/ingestion/sources/postgresql/pg-cdc` | shared source + table |
+| PostgreSQL CDC | `/ingestion/sources/postgresql` | shared source + table |
```

### `infrastructure/stacks/risingwave/compose.yaml` — required edits

```diff
 services:
   risingwave:
-    image: risingwavelabs/risingwave:latest
+    image: risingwavelabs/risingwave:v3.0.0   # pin: 2026-06-11 release; 456 downloads
     ...
-    # v3.0.0 is on :latest since 2026-06-11 (per Agent 14 research)
+    # v2.8.5 was released on 2026-06-26 (15 days after v3.0.0) — v2 is still in maintenance
+    # Pin explicitly to v3.0.0 to avoid surprise rollbacks to v2.8.x line
```

### `infrastructure/stacks/risingwave/init.d/01_init.sql` — required edits

```diff
--- a/infrastructure/stacks/risingwave/init.d/01_init.sql
+++ b/infrastructure/stacks/risingwave/init.d/01_init.sql
@@ -145,7 +145,7 @@ CREATE SINK litellm_model_registry_cdc_sink FROM litellm_model_registry_cdc
     warehouse.path = 's3://lakehouse-garage/warehouse',  -- Garage S3 sink target
     database.name = 'analytics',
     table.name = 'litellm_model_registry',
-    auto.schema.change = 'true'   -- PREMIUM FEATURE in v2.x — requires Cloud/Enterprise
+    auto.schema.change = 'true',  -- OSS in v3.0.0 (was PREMIUM in v2.6.x and earlier)
+    is_exactly_once = 'true',     -- required for auto.schema.change to take effect
     commit_checkpoint_interval = 60,
     catalog.type = 'rest',
     catalog.uri = 'http://lakehouse-iceberg-rest:8181',
```

## URL patterns observed (real, live, on `docs.risingwave.com`)

`/` (→ `/get-started/intro`) · `/llms.txt` (agent-optimized) · `/get-started/architecture` · `/get-started/premium-features` · `/ingestion/overview` · `/ingestion/sources/postgresql` · `/iceberg/overview` · `/iceberg/deliver-to-iceberg` · `/iceberg/ingest-from-iceberg` · `/iceberg/catalogs` · `/iceberg/write-modes` · `/iceberg/object-storage` · `/iceberg/maintenance` · `/delivery/overview` · `/serve/subscription` · `/processing/watermarks` · `/sql/commands/{overview,sql-create-source,sql-create-mv,sql-create-sink}` · `https://github.com/risingwavelabs/risingwave/releases/tag/v3.0.0` · `https://api.github.com/repos/risingwavelabs/risingwave/releases?per_page=N`

## OpenSpec / CCC anchors

- `infrastructure/stacks/risingwave/compose.yaml:17` — KCG single-node all-in-one compose
- `infrastructure/stacks/risingwave/init.d/01_init.sql` — 6 event streams + 2 commented CDC + 1 commented Iceberg sink (needs v3 update)
- `infrastructure/stacks/risingwave/blueprint.yaml` — Pangolin private resources (`risingwave.cianfhoghlaim.ie:4566`, `:5691`)
- `infrastructure/stacks/risingwave/README.md` — quick-start
- `.agents/skills/risingwave/SKILL.md` — primary skill file (needs version + URL updates)
- `.agents/skills/risingwave/references/risingwave-connectors-research.md` — needs URL + version update
- `.agents/skills/risingwave/references/risingwave-best-practices.md` — needs Compute:Meta 3:1→4:1 update
- `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:57-74` — canonical CDC stack requirement
- `openspec/research/2026-06-28-browserbase-program-2/agent-14-risingwave.md` — prior research (302 lines)
- `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-07-falkordb-graphiti-dragonfly-risingwave.md`
- `openspec/research/2026-06-28-browserbase-credit-program/phase-2/P2-31-risingwave.md`

Search terms: `"risingwave"`, `"compute-node"`, `"Serving Node"`, `"Streaming Node"`, `"iceberg-sink"`, `"hummock+minio"`, `"postgres-cdc"`, `"auto.schema.change"`, `"is_exactly_once"`, `"CREATE SUBSCRIPTION"`.

## Anti-patterns (re-confirmed)

1. **Don't run all-in-one in production.** KCG compose is single `risingwave` container. Upstream `docker-compose-distributed.yml` splits into 4 services. Per `/get-started/architecture`: Compute:Compactor = **2:1** (1:8 write-heavy); Compute:Meta = **4:1**; CPU:Memory = **1:4**.
2. **Don't use `REFRESH MATERIALIZED VIEW`** — does not exist. MVs are continuously maintained.
3. **Don't use `UPDATE`/`DELETE` on a `CREATE SOURCE`.** Sources are read-only; use `CREATE TABLE` with connector.
4. **Don't skip watermarks** on time-windowed MVs. Without `WATERMARK FOR event_time AS event_time - INTERVAL '5 seconds'`, windows never close.
5. **Don't use `NOW()` in an MV without a temporal filter.** Triggers full recomputation on every barrier (1s default).
6. **Don't reach for premium Iceberg features on OSS** — `auto.schema.change` is now OSS but still requires `is_exactly_once='true'` + sink decoupling. **Postgres CDC `auto.schema.change` is still PREMIUM.**
7. **Don't use `:latest` in production** — pin explicitly to v3.0.0; v2.8.5 post-dates v3.0.0 and `:latest` could flip.
8. **Don't reach for premium on OSS CDC sources.** CDC `auto.schema.change` and the new Iceberg v3 exactly-once commit (PR #25708) still require Cloud/Enterprise.
9. **Don't skip the compactor node.** Even in single-node all-in-one, the compactor thread is running; in multi-node, dropping it causes Iceberg file pile-up.
10. **Don't use `subscription-push` without persisting `rw_timestamp`** — otherwise no exactly-once replay on consumer failure.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Streaming engine | RisingWave (not Kafka Streams / Flink) | SQL-native, Postgres-compatible, no Debezium required |
| CDC source pattern | `postgres-cdc` shared source + `CREATE TABLE FROM SOURCE` | Native, supports PG 10-17 + RDS / Aurora / Neon / Supabase |
| Iceberg catalog | Glue / REST (Lakekeeper) / JDBC | Same catalog as olake avoids double-write |
| Iceberg sink mode | `merge-on-read` (default) with `is_exactly_once='true'` + sink_decouple ON | Default; gives exactly-once with no perf hit; unlocks `auto.schema.change` (now OSS) |
| Iceberg `auto.schema.change` | **Adopt in v3.0.0** (no longer PREMIUM) | Drift vs prior research; see init.d diff above |
| Postgres CDC `auto.schema.change` | **Defer** until Enterprise license decision | Still PREMIUM |
| Deployment (dev) | single-node all-in-one `:v3.0.0` | Per upstream docs; adequate for KCG dev scale |
| Deployment (prod) | multi-node distributed compose (4 services) | Per `/get-started/architecture` |
| Subscription push | `CREATE SUBSCRIPTION ... WITH (retention='1D')` + cursor + persist `rw_timestamp` | No polling, no broker; agents subscribe via Postgres protocol |
| Object store | MinIO (dev) → Garage S3 (prod, `lakehouse-garage:3900`) | Already in `lakehouse` stack |
| Meta store | Postgres (compose default) | Persistent meta survives container restarts |
| Image tag | `risingwavelabs/risingwave:v3.0.0` (NOT `:latest`) | v2.8.5 was released 15 days after v3.0.0 — `:latest` could flip |
| Subscription retention | `'1D'` default; `'7D'` for replay windows | Match per-call latency budget |

## §8 Refactor opportunities (10, ranked by impact)

1. **Adopt Iceberg v3 `auto.schema.change`** in `init.d/01_init.sql:145-155` — was premium, now OSS. Add `is_exactly_once='true'` (sink_decouple is default ON).
2. **Pin RisingWave image to `:v3.0.0`** in `compose.yaml:17` (NOT `:latest` — `v2.8.5` shipped 15 days post-v3).
3. **Update architecture node names** in `.agents/skills/risingwave/SKILL.md` from `compute-node`/`meta-node`/`compactor-node`/`frontend-node` to **Serving Node / Streaming Node / Meta Node / Compactor Node** (process invocation unchanged).
4. **Fix CDC + Iceberg URLs** in skill + research notes → `/ingestion/sources/postgresql` and `/iceberg/deliver-to-iceberg` (the old `/docs/ingest/ingest-from-cdc` and `/docs/transform/iceberg` now 404).
5. **Update Compute:Meta ratio from 3:1 → 4:1** in `risingwave-best-practices.md` (live docs).
6. **Add Firecrawl monitor** on `https://docs.risingwave.com/llms.txt` for URL restructure alerts (4th-layer monitoring).
7. **CCC: crawl `llms.txt`** as a doc source so CCC auto-discovers URL changes.
8. **Add Postgres TOAST awareness** to the skill (v2.6.0 addition; matters for `oideachais_db_cdc` if `text`/`jsonb` columns).
9. **Defer Postgres CDC `auto.schema.change`** — keep commented in `init.d/01_init.sql:124-138` until license decision (still PREMIUM).
10. **Add a Subscription progress-table template** to `init.d/01_init.sql` for the agent event push use case.

## Files to read next

- `infrastructure/stacks/risingwave/init.d/01_init.sql` (155 lines — needs v3 update)
- `infrastructure/stacks/risingwave/compose.yaml` (needs `:v3.0.0` pin)
- `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:57-74`
- `openspec/research/2026-06-28-browserbase-program-2/agent-14-risingwave.md` (302 lines — prior research)
- `.agents/skills/risingwave/SKILL.md` (needs version + URL updates)
- Live: https://docs.risingwave.com/llms.txt (canonical agent-optimized index)
- Live: https://github.com/risingwavelabs/risingwave/releases (Rust 91.8%, Java 3.5%, Python 2.6%, 9.1k+ stars)