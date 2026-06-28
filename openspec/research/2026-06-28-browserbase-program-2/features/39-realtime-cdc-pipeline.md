# F-01 · Realtime CDC Pipeline — RisingWave (streaming) + olake (batch) → Iceberg

**Agent:** 39 of 43 (BrowserBase Program 2, Wave 3 — `realtime-cdc-pipeline`)
**Date:** 2026-06-29 · **Status:** design spec, ready for `openspec validate` review
**Source files consulted:** `agent-14-risingwave.md` (302 L), `agent-08-ducklake.md` (320 L), `agent-17-komodo.md` (315 L), `synthesis/27-feature-backlog.md` (240 L), `cianfhoghlaim/stacks/risingwave/{compose.yaml,init.d/01_init.sql}`, `cianfhoghlaim/stacks/olake/{compose.yaml,DEPRECATED.md,README.md}`
**Cross-refs:** `synthesis/27-feature-backlog.md:33-38` (F-01 P0), `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:57-74` (canonical CDC stack req), `agent-14:29-31` (Iceberg v3 EO premium gate), `agent-14:184-228` (9 anti-patterns), `refactors/37-dagster-asset-check-rollout.md` (canonical `@multi_asset_check` pattern, 1.13.11)
**Credits used:** ~0 (all context from Wave-1 outputs; no live browser)

---

## 1. TL;DR

**RisingWave v3.0.0** (sub-second streaming via `postgres-cdc`) writes **append-only** to `oideachais_cdc.streaming.*` partitioned by `event_date`; **olake** (300K rows/sec, 15-min incremental + nightly full snapshot) writes **merge-on-read** to `oideachais_cdc.batch.*` partitioned by `snapshot_date`; both target the same **Lakekeeper REST catalog** on the same **Garage S3** bucket. **Disjoint namespaces + disjoint partition columns** mean the two writers never touch the same Iceberg table or partition; a DuckDB read view dedupes via `DISTINCT ON (pk) ORDER BY _ver DESC`. A Dagster 1.13.11 `@multi_asset_check` (`blocking=True`) fires when streaming lag > 60 s OR batch lag > 26 h, wired to a Komodo `[[alerter]]`. **Premium gate:** Iceberg v3 exactly-once (PR #25708) requires RisingWave Enterprise/Cloud — we ship at-least-once + idempotent retries until the license decision.

---

## 2. Architecture — the two paths

```
 ┌──────────────────────┐                      ┌──────────────────────────────┐
 │ PlanetScale Postgres │                      │ Mongo / MySQL / Postgres     │
 │ (production OLTP)    │                      │ (legacy + crown deps)       │
 └──────────┬───────────┘                      └──────────────┬───────────────┘
            │ WAL (logical replication, slot)                 │ oplog / binlog
            ▼                                                  ▼
 ┌──────────────────────┐                      ┌──────────────────────────────┐
 │ RisingWave v3.0.0    │  sub-second CDC      │ olake v0.1.x (olakego/olake) │
 │ (streaming, all 4    │  ───────────────►    │ (batch, every 15 min         │
 │  nodes)              │                      │  incremental + nightly       │
 │                      │                      │  full snapshot)              │
 │  - postgres-cdc      │                      │                              │
 │  - 6 event streams   │                      │  - source-mongodb:latest     │
 │  - cascading MVs     │                      │  - source-postgres:latest    │
 │  - subscription      │                      │  - writer-iceberg:latest     │
 │    push for agents   │                      │                              │
 └──────────┬───────────┘                      └──────────────┬───────────────┘
            │ CREATE SINK (iceberg)                          │ olake write
            │ type=append-only                               │ (merge-on-read)
            │ partition_by=event_date                        │ partition_by=snapshot_date
            ▼                                                  ▼
 ┌─────────────────────────────────────────────────────────────────────────┐
 │  Lakekeeper REST catalog (:8181) — single source of truth for Iceberg  │
 │  s3://lakehouse-bucket/iceberg/                                         │
 │     streaming/oideachais_cdc.curriculum_outcomes/   (RisingWave writes) │
 │     batch/    oideachais_cdc.curriculum_outcomes/   (olake     writes) │
 └─────────────────────────────────────────────────────────────────────────┘
            │                │                          │
            ▼                ▼                          ▼
       DuckDB/Iceberg    LanceDB                Cognee + Graphiti
       (MotherDuck)      (read replica)        (consume both for
                                                knowledge graph edges)
```

**Coexistence rule (the one thing that has to be right):** RisingWave and olake never write the **same row** to the **same Iceberg table** in the **same partition**. The split is:

| Layer | Writer | Partition column | Mode | Namespace |
|:--|:--|:--|:--|:--|
| Streaming tail (last 24 h) | RisingWave | `event_date` (UTC date of `event_time`) | `append-only` | `oideachais_cdc.streaming.*` |
| Historical + slow tables | olake | `snapshot_date` (UTC date of `olake_snapshot_ts`) | `upsert` (merge-on-read) | `oideachais_cdc.batch.*` |
| Reference / dimension | olake (nightly full) | `snapshot_date` | `upsert` | `oideachais_cdc.batch.*` |

Downstream readers compose with a **time-window UNION** view:

```sql
-- oideachais_cdc.curriculum_outcomes_recent view (read-only)
SELECT * FROM oideachais_cdc.streaming.curriculum_outcomes
WHERE event_time > NOW() - INTERVAL '24 hours'
UNION ALL
SELECT *, snapshot_time AS event_time
FROM oideachais_cdc.batch.curriculum_outcomes
WHERE snapshot_date >= CURRENT_DATE - INTERVAL '7 days';
```

Iceberg's hidden partitioning handles `event_date` / `snapshot_date` so the view doesn't scan the full history.

---

## 3. RisingWave CDC source — Postgres publication + `CREATE SOURCE`

### 3.1 Postgres side (one-time per database)

```sql
-- On PlanetScale Postgres (the upstream OLTP for oideachais)
ALTER SYSTEM SET wal_level = 'logical';  -- requires restart

CREATE PUBLICATION oideachais_pub FOR TABLE
    public.curriculum_outcomes,
    public.curriculum_strands,
    public.school_enrolment,
    public.assessment_results,
    public.student_progress;

CREATE ROLE rw_replicator WITH REPLICATION LOGIN PASSWORD '...';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rw_replicator;
```

### 3.2 RisingWave side (replaces the commented template at `init.d/01_init.sql:124-138`)

```sql
-- Per Agent 14 §ANTI-PATTERN #9: set backfill.parallelism for large tables
CREATE SOURCE oideachais_pg WITH (
    connector = 'postgres-cdc',
    hostname = 'planetscale-prod.internal', port = '5432',
    username = 'rw_replicator',
    password = 'secret:risingwave/rw_replicator_password',  -- Locket
    database.name = 'oideachais', schema.name = 'public',
    slot.name = 'risingwave_oideachais_slot',
    snapshot.batch_size = '2000',
    backfill.parallelism = '4',
    backfill.num_rows_per_split = '50000'
);

CREATE TABLE streaming_curriculum_outcomes (
    outcome_id     VARCHAR PRIMARY KEY,
    strand_code    VARCHAR, subject VARCHAR, cycle VARCHAR,
    description_en TEXT, description_ga TEXT,
    updated_at     TIMESTAMPTZ,
    _rw_lsn        BIGEST                -- monotonic LSN for reconciliation
) FROM oideachais_pg TABLE 'public.curriculum_outcomes';

CREATE TABLE streaming_curriculum_strands (
    strand_code   VARCHAR PRIMARY KEY,
    strand_name   VARCHAR, aole VARCHAR,
    updated_at    TIMESTAMPTZ, _rw_lsn BIGEST
) FROM oideachais_pg TABLE 'public.curriculum_strands';

-- Watermark for time-windowed MVs (per Agent 14 §ANTI-PATTERN #4)
CREATE TABLE streaming_audio_events (
    event_id    VARCHAR PRIMARY KEY, payload JSONB,
    event_time  TIMESTAMPTZ,
    WATERMARK FOR event_time AS event_time - INTERVAL '5 seconds'
) APPEND ONLY;
```

**Why shared source + per-table `CREATE TABLE`** (Agent 14 §CODE line 100-111): one logical replication slot serves N tables. Avoids exhausting `max_replication_slots` (default 10 on PlanetScale).

---

## 4. RisingWave Iceberg sink — `CREATE SINK`

```sql
-- Per Agent 14 §ANTI-PATTERN #8: avoid `auto.schema.change = 'true'`
-- (PREMIUM FEATURE; requires Enterprise/Cloud). We rely on
-- Iceberg v2 hidden partitioning + manual ALTER for schema adds.
CREATE SINK IF NOT EXISTS streaming_curriculum_outcomes_iceberg
FROM streaming_curriculum_outcomes
WITH (
    connector = 'iceberg',
    type = 'append-only',                           -- streaming path is append
    catalog.type = 'rest',
    catalog.uri = 'http://lakehouse-iceberg-rest:8181',
    warehouse.path = 's3://lakehouse-bucket/iceberg/streaming/',
    database.name = 'oideachais_cdc',
    table.name = 'curriculum_outcomes',
    create_table_if_not_exists = 'true',
    s3.endpoint = 'http://lakehouse-garage:3900',
    s3.region = 'garage',
    s3.access.key = 'secret:lakehouse/s3_access_key',
    s3.secret.key = 'secret:lakehouse/s3_secret_key',
    s3.path.style.access = 'true',
    partition_by = 'event_date',                    -- derived column from MV below
    is_exactly_once = 'true',                       -- requires sink_decouple
    commit_checkpoint_interval = 60,
    sink_decouple = 'true'
    -- auto.schema.change = 'true'                   -- DO NOT USE (premium)
) FORMAT UPSERT ENCODE PARQUET (force_append_only = true);

-- The `partition_by` in RisingWave must be a column name (not expression);
-- this MV adds the derived `event_date` partition column.
CREATE MATERIALIZED VIEW streaming_curriculum_outcomes_iceberg_mv AS
SELECT outcome_id, strand_code, subject, cycle,
       description_en, description_ga, updated_at, _rw_lsn,
       DATE_TRUNC('day', updated_at) AS event_date
FROM streaming_curriculum_outcomes;

-- Cascade MVs (the marimo dashboard pattern, from init.d/01_init.sql:34-51)
CREATE MATERIALIZED VIEW IF NOT EXISTS streaming_outcomes_hourly AS
SELECT date_trunc('hour', event_time) AS hour, strand_code, cycle,
       COUNT(*) AS update_count,
       COUNT(DISTINCT outcome_id) AS distinct_outcomes
FROM streaming_curriculum_outcomes_iceberg_mv
GROUP BY date_trunc('hour', event_time), strand_code, cycle;

CREATE MATERIALIZED VIEW IF NOT EXISTS streaming_outcomes_daily AS
SELECT date_trunc('day', hour) AS day, strand_code,
       SUM(update_count) AS total_updates
FROM streaming_outcomes_hourly
GROUP BY date_trunc('day', hour), strand_code;
```

**Premium gate** (Agent 14 §DRIFT 2026-06-24): `is_exactly_once = 'true'` + `auto.schema.change = 'true'` is the **Iceberg v3 commit** (PR #25708, 4 days old). **License decision (Enterprise/Cloud) required** before adopting v3. Until then: at-least-once + idempotent retries + reconciliation view dedup.

---

## 5. olake batch CDC — the nightly full + 15-min incremental

The standalone `infrastructure/stacks/olake/` is **DEPRECATED** (per `DEPRECATED.md:1-39`). olake is a service inside `infrastructure/stacks/lakehouse/compose.yaml`. The pattern is **one JSON config per source**; olake is a CLI-driven tool, no daemon.

### 5.1 Source config — `infrastructure/stacks/lakehouse/olake/configs/curriculum_outcomes.json`

```json
{
  "source": {
    "type": "POSTGRES",
    "connection": {
      "host": "planetscale-prod.internal", "port": 5432,
      "database": "oideachais",
      "username": "olake_replicator",
      "password": "secret:lakehouse/olake_replicator_password",
      "sslmode": "require"
    },
    "replication_slot": "olake_oideachais_slot",
    "publication_name": "olake_pub",
    "snapshot_mode": "initial",
    "incremental_mode": "logical_replication"
  },
  "destination": {
    "type": "ICEBERG",
    "catalog_type": "rest",
    "catalog_uri": "http://lakehouse-iceberg-rest:8181",
    "warehouse": "s3://lakehouse-bucket/iceberg/batch/",
    "s3": {
      "endpoint": "http://lakehouse-garage:3900", "region": "garage",
      "access_key": "secret:lakehouse/s3_access_key",
      "secret_key": "secret:lakehouse/s3_secret_key",
      "path_style_access": true
    },
    "namespace": "oideachais_cdc.batch",
    "table": "curriculum_outcomes",
    "partition_by": "snapshot_date",
    "write_mode": "merge",
    "primary_key": ["outcome_id"]
  },
  "sync": {
    "mode": "incremental",
    "interval_minutes": 15,
    "full_snapshot_cron": "0 2 * * *"
  }
}
```

### 5.2 Dagster orchestration (the 15-min + nightly trigger)

```python
# cianfhoghlaim/assets/_oideachais_dagster_defs/cdc/olake_sync.py
import dagster as dg
from pathlib import Path

OLAKE_CONFIG_DIR = Path("/opt/stacks/lakehouse/olake/configs")

@dg.asset(group_name="cdc", kinds={"olake", "iceberg"})
def olake_batch_curriculum_outcomes(context: dg.AssetExecutionContext):
    """15-min incremental + nightly full snapshot CDC via olake."""
    result = context.resources.subprocess.run([
        "olake", "sync",
        "--config", str(OLAKE_CONFIG_DIR / "curriculum_outcomes.json"),
        "--catalog", str(OLAKE_CONFIG_DIR / "catalog.json"),
        "--destination", str(OLAKE_CONFIG_DIR / "writer.json"),
        "--state", str(OLAKE_CONFIG_DIR / "state" / "curriculum_outcomes.json"),
    ], check=True, capture_output=True, text=True)
    rows = int([l for l in result.stdout.splitlines() if '"rows_synced"' in l][0]
               .split('"rows_synced":')[1].split(',')[0])
    return dg.MaterializeResult(metadata={"rows_synced": rows,
        "destination": "oideachais_cdc.batch.curriculum_outcomes"})
```

### 5.3 olake vs RisingWave — who owns what

| Table class | Owner | Why |
|:--|:--|:--|
| High-frequency narrow rows (`student_progress`, `assessment_results`) | **RisingWave** | Sub-second freshness required for tutor UX |
| Slowly-changing dimensions (`curriculum_strands`, `school_enrolment`) | **olake** | Nightly snapshot is fine; merge-on-read dedup is cheap |
| Reference data with no WAL (MongoDB, crown deps) | **olake** | RisingWave only speaks Postgres CDC |
| Crown-dependency legal PDFs (IoM / Jersey / Guernsey) | **olake** | Not relational; no CDC stream |

---

## 6. Reconciliation — how the two paths don't double-write

### 6.1 The problem

If RisingWave (append) and olake (upsert) both write to the same `oideachais_cdc.curriculum_outcomes` table: RisingWave appends `outcome_id=42, _rw_lsn=100`; olake's next 15-min sync also writes the same row (full snapshot caught it); Iceberg ends up with duplicates; merge-on-read in olake conflicts with append-only from RisingWave.

### 6.2 The solution (3 mechanisms, layered)

1. **Separate namespaces.** `oideachais_cdc.streaming.*` (RisingWave) vs `oideachais_cdc.batch.*` (olake). The two writers never touch the same Iceberg table.
2. **Partition-column contract.** RisingWave partitions by `event_date`; olake partitions by `snapshot_date`. Different columns → different Iceberg partition specs → physically disjoint files in S3.
3. **Freshness window for the read path.** A read view picks streaming (last 24 h) ∪ batch (last 7 days) and dedupes by `primary_key` taking `max(_rw_lsn) / max(snapshot_ts)` per row.

```sql
-- oideachais_cdc.curriculum_outcomes_recent (created in DuckDB / MotherDuck)
CREATE OR REPLACE VIEW oideachais_cdc.curriculum_outcomes_recent AS
WITH s AS (
    SELECT *, 'streaming' AS _src, _rw_lsn AS _ver
    FROM oideachais_cdc.streaming.curriculum_outcomes
    WHERE event_time > NOW() - INTERVAL '24 hours'
),
b AS (
    SELECT *, 'batch' AS _src, snapshot_ts AS _ver
    FROM oideachais_cdc.batch.curriculum_outcomes
    WHERE snapshot_date >= CURRENT_DATE - INTERVAL '7 days'
),
unioned AS (SELECT * FROM s UNION ALL BY NAME SELECT * FROM b)
SELECT DISTINCT ON (outcome_id)
    outcome_id, strand_code, subject, cycle,
    description_en, description_ga, updated_at, _src, _ver
FROM unioned
ORDER BY outcome_id, _ver DESC;
```

### 6.3 Edge case: olake's full snapshot covers the last 24 h

When olake's nightly full snapshot runs at 02:00 UTC, it captures **all** rows including the ones RisingWave streamed yesterday. The `unioned` query dedupes by `_ver DESC` → the most recent write wins, regardless of source. **Worst case:** a `description_ga` edit made at 23:55 yesterday and streamed by RisingWave gets overwritten by olake's 02:00 snapshot. **Mitigation:** the olake config's `incremental_mode: logical_replication` means the 15-min sync is **WAL-based, not full-snapshot** — only the 02:00 nightly is a full snapshot. Lag is bounded to the 02:00 snapshot window, same as the existing marimo dashboard's max(2-hour) staleness (no regression).

### 6.4 Sort key for fast dedup

Both Iceberg tables get a **Z-order sort** on `(outcome_id, _ver DESC)` to make the `DISTINCT ON` query O(partition) instead of O(table). For Iceberg: `table.sort-order = 'ZORDER(outcome_id, _ver)'` in the writer config.

---

## 7. Deployment + monitoring

### 7.1 compose.yaml — multi-node RisingWave (per Agent 14 §REFACTOR #1)

Replace the single all-in-one container in `infrastructure/stacks/risingwave/compose.yaml:17-53` with 4 services (Agent 14 §CODE lines 53-76):

```yaml
name: risingwave

x-risingwave-common: &risingwave-common
  image: risingwavelabs/risingwave:v3.0.0          # pin (Agent 14 §ANTI-PATTERN #7)
  restart: unless-stopped
  environment: &risingwave-env
    RW_STATE_STORE_URL: "hummock+minio://risingwave-minio:9201/hummock"
    RW_OBJECT_STORE_URL: "minio://risingwave-minio:9201/hummock"
    RW_META_ADDR: "meta:5690"
    RW_COMPACTOR_ADDR: "compactor:6660"
    RW_DATABASE_URL: ${RISINGWAVE_DATABASE_URL}
    RW_MEMORY_MODE: "true"                         # KCG deviation (Agent 14)
  networks: [cianfhoghlaim, lakehouse]
  volumes: ["./risingwave.toml:/risingwave.toml:ro"]

services:
  meta:
    <<: *risingwave-common
    command: "meta-node --config-path /risingwave.toml"
    ports: ["5690:5690"]
    healthcheck: {test: ["CMD-SHELL", "curl -sf http://localhost:5690/api/v1/healthy"], interval: 15s}
  compactor:
    <<: *risingwave-common
    command: "compactor-node --config-path /risingwave.toml"
  compute:
    <<: *risingwave-common
    command: "compute-node --config-path /risingwave.toml"
    deploy: {resources: {limits: {memory: 16G, cpus: '8'}}}    # 2:1 compute:compactor (Agent 14 §ANTI-PATTERN #6)
  frontend:
    <<: *risingwave-common
    command: "frontend-node --config-path /risingwave.toml"
    ports: ["4566:4566"]                            # PostgreSQL wire protocol
  minio:
    image: minio/minio:RELEASE.2025-06-13T16-33-19Z
    command: server /data --console-address ":9001"
    environment: {MINIO_ROOT_USER: ${RISINGWAVE_MINIO_USER:-risingwave}, MINIO_ROOT_PASSWORD: ${RISINGWAVE_MINIO_PASSWORD}}
    volumes: ["risingwave_minio_data:/data"]
    ports: ["9201:9001"]
    networks: [cianfhoghlaim]
  dashboard:
    image: risingwavelabs/risingwave-dashboard:latest
    depends_on: {frontend: {condition: service_healthy}}
    ports: ["5691:5691"]
    environment: {RW_API_ENDPOINT: "http://frontend:4566"}
    networks: [cianfhoghlaim]

volumes: {risingwave_minio_data:}
```

### 7.2 olake service (already in `infrastructure/stacks/lakehouse/compose.yaml`)

Per `DEPRECATED.md:9-13`, olake lives at `infrastructure/stacks/lakehouse/compose.yaml` as service `olake`, with `infrastructure/stacks/lakehouse/olake/{config,catalog,writer}.json` mounted. **No new file needed** — verify it uses the same Lakekeeper REST catalog and Garage S3 credentials as RisingWave.

### 7.3 Dagster asset check for CDC lag (canonical 1.13.x pattern)

Per `refactors/37-dagster-asset-check-rollout.md` (lines 52-79), the canonical 1.13.x CDC lag check uses `@multi_asset_check` (one `async def` + N yielded results):

```python
# cianfhoghlaim/dagster_defs/checks/cdc_lag.py
import time, dagster as dg, httpx
from cianfhoghlaim.assets._oideachais_dagster_defs.resources import (
    RisingWaveResource, OlakeStateResource)

CDC_TABLES = ["curriculum_outcomes", "curriculum_strands", "school_enrolment",
              "assessment_results", "student_progress"]

@dg.multi_asset_check(specs=[
    dg.AssetCheckSpec(
        name=f"cdc_lag_{t}",
        asset=dg.AssetKey(["oideachais", "cdc", t]),
        description=f"Streaming + batch lag for {t} (target: streaming<60s, batch<26h)",
        blocking=True,                            # per Refactor 37 §2 (#2)
    ) for t in CDC_TABLES
])
async def check_cdc_lag(context: dg.AssetExecutionContext):
    """Combined streaming + batch lag check — 1 round-trip per source."""
    rw, olake = context.resources.risingwave, context.resources.olake_state
    async with httpx.AsyncClient() as client:
        for table in CDC_TABLES:
            rw_lag = await rw.query_scalar(
                f"SELECT EXTRACT(EPOCH FROM (NOW() - MAX(event_time))) FROM streaming_{table}")
            batch_lag_seconds = time.time() - olake.last_snapshot_ts(table)
            streaming_ok, batch_ok = rw_lag < 60, batch_lag_seconds < 26 * 3600
            yield dg.AssetCheckResult(
                passed=streaming_ok and batch_ok,
                severity=dg.AssetCheckSeverity.WARN
                       if (streaming_ok and not batch_ok) else dg.AssetCheckSeverity.ERROR,
                metadata={"streaming_lag_seconds": float(rw_lag),
                          "batch_lag_seconds": float(batch_lag_seconds),
                          "streaming_threshold_seconds": 60,
                          "batch_threshold_seconds": 26 * 3600,
                          "premium_exactly_once": False},
            )
```

**`blocking=True`** (per `refactors/37-dagster-asset-check-rollout.md:33`): when the check fails, downstream assets (the marimo `agent_queries` dashboard, Cognee cognify tasks, RAGAS eval runs) **do not materialize** — prevents stale-data corruption in the tutor UX.

### 7.4 Alerting (Komodo alerter + sensor)

```toml
# infrastructure/komodo/alerters/cdc-lag.toml
[[alerter]]
name = "cdc-lag-pager"
[[alerter.config.endpoint]]
type = "Discord"
url = "[[ALERTER_CDC_LAG_DISCORD_WEBHOOK]]"
[[alerter.config.resolved_endpoint]]
type = "Discord"
url = "[[ALERTER_CDC_LAG_DISCORD_WEBHOOK]]"
```

Dagster sensor pattern: when `cdc_lag_curriculum_outcomes` flips red, the sensor fires the Komodo alerter via `https://komodo.cianfhoghlaim.ie/listener/github/alerter/cdc-lag-pager/alert` (URL pattern from `agent-17-komodo.md:168-177`).

### 7.5 RAGAS drift check (per program-2 every-5th rule)

For F-01, the RAGAS eval is on the **reconciliation view query latency + duplication rate**:

| Metric | Target | Failure mode |
|:--|:--|:--|
| `view_query_p95_ms` (DuckDB over Iceberg) | < 5 000 ms | Partition spec wrong (full-table scan) |
| `duplicate_rate` (DISTINCT ON result) | < 0.001 | olake and RisingWave wrote to the same Iceberg table |
| `streaming_lag_p99_seconds` | < 60 s | RisingWave compute node down or backfill stuck |
| `batch_lag_hours` | < 26 h | olake nightly cron failed or Locket secret rotated |

Use `ragas.metrics.context_precision` on a 20-row sampled `curriculum_outcomes_recent` query.

### 7.6 Phase 0.8 dry-run credit calibration (per system prompt)

Before the bulk run, dry-run 1× per CDC table (5 tables) to calibrate the per-item credit cap. RisingWave `dashboard:5691` UI is cheapest verification (`agent-14:18` — 1 credit per page load); olake is CLI-driven (no credits); Dagster UI is local. **Estimated total: 5 credits for dry-run + 50 credits for full validation = 55 credits** (well within the 250 budget for agent 39).

---

## 8. Open questions for the openspec change

1. **Iceberg v3 exactly-once premium gate** (`agent-14:34-36`) — Enterprise/Cloud license decision blocks `auto.schema.change = 'true'`. Until then we ship at-least-once + idempotent MERGE.
2. **Multi-node RisingWave split** (`agent-14:248-252`) — must ship before F-01 GA (single-node all-in-one is "not recommended for production").
3. **olake replication slot collision with RisingWave** — Postgres allows only **one** logical replication consumer per `publication`. The cleanest split: **RisingWave uses `pgoutput` slot `risingwave_oideachais_slot`**, **olake uses its own dedicated `olake_oideachais_slot` slot on a separate publication `olake_pub`** (disjoint table list, or different tables entirely).
4. **LanceDB read-replica** — should F-01 also include a LanceDB mirror of the Iceberg read view (per `agent-04-lancedb.md`)? Currently the marimo dashboard reads from DuckDB/MotherDuck. Defer to F-10.

---

## 9. Files to write

| Path | Purpose | Effort |
|:--|:--|:--|
| `openspec/changes/2026-06-29-realtime-cdc-pipeline/proposal.md` | OpenSpec proposal | 1 h |
| `openspec/changes/2026-06-29-realtime-cdc-pipeline/tasks.md` | 8-task implementation plan | 30 min |
| `openspec/changes/2026-06-29-realtime-cdc-pipeline/specs/meaisinfhoghlaim-platform/spec.md` | ADDED Requirements for CDC lag check + multi-node split | 1 h |
| `infrastructure/stacks/risingwave/compose.yaml` | Split into 4 services (Refactor #1) | 2 h |
| `infrastructure/stacks/risingwave/init.d/01_init.sql` | Uncomment + extend CDC source + Iceberg sink | 30 min |
| `infrastructure/stacks/lakehouse/olake/configs/curriculum_outcomes.json` | First olake config (per Section 5.1) | 30 min |
| `infrastructure/stacks/lakehouse/olake/configs/curriculum_strands.json` | Second olake config (SCD table) | 30 min |
| `infrastructure/stacks/lakehouse/olake/configs/school_enrolment.json` | Third olake config | 30 min |
| `cianfhoghlaim/dagster_defs/checks/cdc_lag.py` | `@multi_asset_check` for lag (Section 7.3) | 2 h |
| `cianfhoghlaim/dagster_defs/assets/cdc/olake_sync.py` | Dagster asset for 15-min sync (Section 5.2) | 1 h |
| `infrastructure/komodo/alerters/cdc-lag.toml` | Komodo alerter (Section 7.4) | 15 min |
| `infrastructure/komodo/procedures/cdc-replay.toml` | Replay procedure (backfill from olake state) | 1 h |
| Migration plan (planet → 4-node RisingWave) | Zero-downtime cutover procedure | 1 h |

**Total estimated: 11.5 h** (matches F-01 §Effort = L, "cross-team RisingWave + olake + Dagster + Iceberg").

---

## 1-paragraph summary

The F-01 Realtime CDC Pipeline is a **two-path write to the same Lakekeeper Iceberg catalog**: RisingWave v3.0.0 (sub-second streaming, multi-node split) writes **append-only** to `oideachais_cdc.streaming.*` partitioned by `event_date` from a `postgres-cdc` shared source + per-table `CREATE TABLE FROM SOURCE` against PlanetScale Postgres; olake (300K rows/sec batch, every 15-min incremental + 02:00 UTC nightly full snapshot, deployed as a service inside `infrastructure/stacks/lakehouse/compose.yaml`) writes **upsert/merge-on-read** to `oideachais_cdc.batch.*` partitioned by `snapshot_date`; both target the same Garage S3 bucket (`s3://lakehouse-bucket/iceberg/`) but **disjoint namespaces + disjoint partition columns** so they never double-write the same row. Reconciliation is a DuckDB/MotherDuck read view (`curriculum_outcomes_recent`) that picks the streaming tail (last 24 h) ∪ the batch recent (last 7 days) and dedupes via `DISTINCT ON (pk) ORDER BY _ver DESC`, with a Z-order sort on `(pk, _ver DESC)` for O(partition) dedup. A `@multi_asset_check` (Dagster 1.13.11, `blocking=True`) gates downstream assets when streaming lag > 60 s OR batch lag > 26 h, wired to a Komodo `[[alerter]]` for pager rotation. The **premium gate** is Iceberg v3 exactly-once commit (PR #25708, requires RisingWave Enterprise/Cloud) — until the license decision, we ship at-least-once with idempotent retries. Effort ~11.5 h, dependency on the multi-node RisingWave split (Refactor #1 from `agent-14`).
