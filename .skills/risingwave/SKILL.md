---
name: risingwave
description: Expert assistance for RisingWave streaming database. Use when users need real-time analytics, CDC pipelines, materialized views, streaming SQL, or event processing.
---

# RisingWave - Streaming Database

**Version:** 2.x | **Last Updated:** 2025-01

## Overview

RisingWave is a cloud-native streaming database for real-time analytics:

- **Streaming SQL**: Standard SQL for stream processing
- **Materialized Views**: Incrementally maintained query results
- **CDC Support**: PostgreSQL, MySQL change data capture
- **Connectors**: Kafka, Kinesis, S3, Iceberg, ClickHouse
- **Exactly-Once**: Guaranteed processing semantics

**Documentation**: https://docs.risingwave.com

## When to Use This Skill

Activate when users need:

- "Build real-time analytics pipelines"
- "Create CDC replication from PostgreSQL"
- "Process streaming data with SQL"
- "Create materialized views that auto-update"
- "Set up event-driven architectures"

## Core Concepts

### 1. Source Creation (Kafka)

```sql
CREATE SOURCE events (
  event_id VARCHAR,
  user_id INT,
  event_time TIMESTAMP,
  payload JSONB,
  -- Watermark for event-time processing
  WATERMARK FOR event_time AS event_time - INTERVAL '5 seconds'
) WITH (
  connector = 'kafka',
  topic = 'events',
  properties.bootstrap.server = 'localhost:9092',
  scan.startup.mode = 'earliest'
) FORMAT PLAIN ENCODE JSON;
```

### 2. CDC Source (PostgreSQL)

```sql
CREATE TABLE orders WITH (
  connector = 'postgres-cdc',
  hostname = 'localhost',
  port = '5432',
  username = 'user',
  password = 'password',
  database.name = 'mydb',
  schema.name = 'public',
  table.name = 'orders',
  slot.name = 'orders_slot'
);
```

### 3. Materialized Views

```sql
-- Real-time aggregation
CREATE MATERIALIZED VIEW hourly_stats AS
SELECT
  window_start,
  window_end,
  user_id,
  COUNT(*) as event_count,
  SUM(amount) as total
FROM TUMBLE(events, event_time, INTERVAL '1 hour')
GROUP BY window_start, window_end, user_id;

-- Simple aggregation (no window)
CREATE MATERIALIZED VIEW user_totals AS
SELECT
  user_id,
  COUNT(*) as total_events,
  SUM(amount) as total_amount,
  MAX(event_time) as last_activity
FROM events
GROUP BY user_id;
```

### 4. Window Functions

```sql
-- Tumbling window (non-overlapping)
SELECT *
FROM TUMBLE(events, event_time, INTERVAL '1 hour')
GROUP BY window_start, window_end;

-- Hopping window (overlapping)
SELECT *
FROM HOP(events, event_time, INTERVAL '5 minutes', INTERVAL '1 hour')
GROUP BY window_start, window_end;

-- Session window (gap-based)
SELECT
  user_id,
  session_start,
  session_end,
  COUNT(*) as events
FROM events
GROUP BY user_id, session(event_time, INTERVAL '30 minutes')
EMIT ON WINDOW CLOSE;
```

### 5. Temporal Joins

```sql
-- Join stream with dimension table
CREATE MATERIALIZED VIEW enriched_events AS
SELECT
  e.event_id,
  e.amount,
  u.name as user_name,
  u.tier as user_tier
FROM events e
JOIN users FOR SYSTEM_TIME AS OF PROCTIME() u
ON e.user_id = u.id;

-- Interval join (time-bounded)
CREATE MATERIALIZED VIEW matched_events AS
SELECT
  a.event_id,
  b.event_id as related_event
FROM stream_a a
JOIN stream_b b
ON a.user_id = b.user_id
AND b.event_time BETWEEN a.event_time - INTERVAL '1 hour'
                     AND a.event_time + INTERVAL '1 hour';
```

### 6. Sink Configuration

```sql
-- Kafka sink (upsert mode)
CREATE SINK events_sink FROM hourly_stats WITH (
  connector = 'kafka',
  properties.bootstrap.server = 'localhost:9092',
  topic = 'hourly_stats'
) FORMAT UPSERT ENCODE JSON;

-- JDBC sink (PostgreSQL/MySQL)
CREATE SINK pg_sink FROM user_totals WITH (
  connector = 'jdbc',
  jdbc.url = 'jdbc:postgresql://localhost:5432/warehouse',
  table.name = 'user_totals',
  type = 'upsert',
  primary_key = 'user_id'
);

-- Iceberg sink
CREATE SINK iceberg_sink FROM events WITH (
  connector = 'iceberg',
  type = 'upsert',
  primary_key = 'event_id',
  catalog.type = 'storage',
  warehouse.path = 's3://bucket/warehouse',
  database.name = 'mydb',
  table.name = 'events'
);
```

### 7. Deduplication

```sql
-- Keep latest event per key
CREATE MATERIALIZED VIEW deduplicated_events AS
SELECT *
FROM (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY event_id
      ORDER BY event_time DESC
    ) as rn
  FROM events
)
WHERE rn = 1;
```

### 8. JSON Processing

```sql
-- Extract JSON fields
SELECT
  payload->>'name' as name,
  (payload->>'amount')::DECIMAL as amount,
  payload->'address'->>'city' as city
FROM events;

-- Unnest JSON arrays
SELECT
  event_id,
  item.value->>'product_id' as product_id,
  (item.value->>'quantity')::INT as quantity
FROM events,
LATERAL jsonb_array_elements(payload->'items') as item;
```

### 9. Performance Tuning

```sql
-- Set parallelism for new materialized views
SET streaming_parallelism = 4;

-- Create index for point lookups
CREATE INDEX idx_user_id ON events (user_id);

-- Distributed index
CREATE INDEX idx_time ON events (event_time)
DISTRIBUTED BY (user_id);

-- Checkpoint configuration (per database)
ALTER DATABASE mydb SET checkpoint_frequency = 5;
ALTER DATABASE mydb SET barrier_interval_ms = 1000;
```

### 10. Monitoring

```sql
-- Check materialized view freshness
SELECT * FROM rw_catalog.rw_materialized_views;

-- View streaming jobs
SHOW JOBS;

-- Check source lag
SELECT * FROM rw_catalog.rw_sources;

-- Cancel running job
CANCEL JOB <job_id>;
```

## Architecture Patterns

### Lambda Alternative
```
Sources → Materialized Views → Sinks
           (real-time)       (serving)
```

### CDC Replication
```
PostgreSQL → CDC Source → MV (transform) → Warehouse Sink
```

### Feature Store
```
Events → MV (window agg) → MV (features) → Redis/JDBC Sink
```

## Connector Reference

### Sources
| Connector | Use Case |
|-----------|----------|
| kafka | Message streaming |
| postgres-cdc | PostgreSQL replication |
| mysql-cdc | MySQL replication |
| kinesis | AWS streaming |
| pulsar | Apache Pulsar |
| s3 | Batch file ingestion |
| google_pubsub | GCP messaging |

### Sinks
| Connector | Use Case |
|-----------|----------|
| kafka | Message output |
| jdbc | PostgreSQL, MySQL |
| redis | Cache layer |
| elasticsearch | Search |
| clickhouse | OLAP warehouse |
| iceberg | Data lake |
| deltalake | Delta Lake |
| bigquery | BigQuery |
| snowflake | Snowflake |

## Best Practices

1. **Define Watermarks**: Always set watermarks for event-time processing
2. **Use Temporal Filters**: Bound state growth with time-based filters
3. **Create Indexes**: Add indexes on frequently filtered columns
4. **Set Primary Keys**: Required for upsert sinks
5. **Tune Checkpoints**: Balance latency vs durability
6. **Monitor Lag**: Watch source and sink lag metrics

## Troubleshooting

### Materialized View Not Updating
1. Check source is receiving data
2. Verify watermark isn't blocking
3. Check temporal filter conditions
4. Look for empty dimension tables in joins

### High Latency
1. Reduce checkpoint interval
2. Increase parallelism: `SET streaming_parallelism = N`
3. Add indexes on join keys
4. Check for backpressure in sinks

### Out of Memory
1. Add temporal filters to bound state
2. Reduce memory cache sizes
3. Increase compactor resources
4. Check for unbounded joins

### Sink Not Producing
1. Verify primary key for upsert sinks
2. Check connector configuration
3. Verify downstream system access
4. Check logs for serialization errors

## Resources

- **Documentation**: https://docs.risingwave.com
- **SQL Reference**: https://docs.risingwave.com/sql/
- **Connectors**: https://docs.risingwave.com/connectors/
- **GitHub**: https://github.com/risingwavelabs/risingwave
