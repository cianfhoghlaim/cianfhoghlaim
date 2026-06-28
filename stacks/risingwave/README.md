# RisingWave — Streaming Database for Real-Time Analytics

## Overview

RisingWave is an open-source streaming database that processes real-time data using SQL. It ingests streams from Kafka, PostgreSQL CDC, and other sources, and maintains incrementally-updated materialized views — enabling real-time analytics with standard SQL syntax. Built in Rust, it is PostgreSQL-compatible at the wire protocol level.

## Why This Matters for Kings' College Galway

The curriculum platform generates continuous streams of events: LLM call traces (from Langfuse), curriculum extraction runs (from Dagster), student interaction data (from the web app), and infrastructure metrics (from Prometheus). RisingWave ties these streams together into real-time materialized views, enabling dashboards that update live as data flows in — rather than running batch queries that are always behind. For example: "show me a live dashboard of extraction quality scores across all subjects, updated as each exam paper finishes processing."

## Key Features

- **Streaming SQL** — Standard PostgreSQL SQL on streaming data
- **Materialized views** — Incrementally updated, always-current query results
- **PostgreSQL-compatible** — Connect any PostgreSQL client or BI tool
- **Kafka/Pulsar/CDC sources** — Ingest from multiple streaming sources
- **Rust-native performance** — Sub-second latency on high-throughput streams

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/risingwave
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Locket resolves PostgreSQL credentials and Kafka connection details from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `RW_PORT` | No | SQL port | `4566` |
| `RW_META_PORT` | No | Meta service port | `5690` |
| `KAFKA_BROKERS` | Yes | Kafka bootstrap servers | — |

## Access

- **SQL Interface**: `postgresql://localhost:4566/dev`
- **Meta Dashboard**: `http://localhost:5690`
- **Auth**: PostgreSQL username/password

## Upstream

- **Repository**: <https://github.com/risingwavelabs/risingwave>
- **Documentation**: <https://docs.risingwave.com>
- **Latest**: v2.x (2025) — PostgreSQL compatibility improvements, Iceberg sink, WebSocket source, Python UDF support

## Screenshot

RisingWave provides a meta dashboard at port 5690 showing cluster status, materialized view health, source/sink throughput, and memory usage. The SQL interface is accessed via any PostgreSQL client — `psql -h localhost -p 4566 -d dev` — and supports standard `CREATE MATERIALIZED VIEW`, `SELECT`, and `EXPLAIN` statements.
