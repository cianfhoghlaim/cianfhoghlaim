---
name: motherduck-architecture
description: Decide which MotherDuck storage pattern to use. Use when evaluating fully-managed MotherDuck vs BYOB (Bring Your Own Bucket) vs DuckLake on MotherDuck vs own-compute DuckLake vs native MotherDuck storage. Also covers the "when NOT to use MotherDuck" decision tree, the migration path from Snowflake/Redshift/PostgreSQL/dbt, the pricing + ROI guardrails, the partner-delivery (multi-tenant) provisioning model, and the bulk-pipeline ingestion-to-serving workflow design. Triggers: 'storage pattern', 'BYOB vs managed', 'DuckLake vs native', 'migrate to MotherDuck', 'pricing', 'partner delivery', 'end-to-end pipeline', 'ingestion-to-serving'.
---

# MotherDuck — Architecture & Storage

Pick the right MotherDuck storage pattern. Absorbs the former
`motherduck-build-data-pipeline`, `motherduck-ducklake`,
`motherduck-migrate-to-motherduck`, `motherduck-pricing-roi`, and
`motherduck-partner-delivery` skills.

## When to use this skill

Use this skill when:

- Picking the storage pattern for a new MotherDuck workload
  (managed vs BYOB vs DuckLake vs own-compute).
- Designing an end-to-end pipeline (raw → staging → analytics
  → serving) on top of MotherDuck.
- Migrating from Snowflake / Redshift / PostgreSQL / dbt-heavy
  stacks to MotherDuck.
- Talking to an economic buyer about pricing, ROI, plan fit, or
  spend guardrails.
- Delivering the same architecture to multiple clients as a
  consultancy / partner.

For SQL dialect, data modeling, connections, or MCP usage, use
`sister skills` below.

## The 4 storage patterns

### 1. Fully-managed MotherDuck (default for new workloads)

The platform owns the catalog metadata, the object-storage files,
and the compute. Best for: prototypes, small datasets, teams that
don't want to operate storage.

```sql
-- Create a database; storage is managed
CREATE DATABASE oideachais;
ATTACH 'md:cianfhoghlaim' AS cianfhoghlaim;
```

### 2. BYOB — Bring Your Own Bucket (KCG preferred for production)

You own the S3-compatible bucket; MotherDuck reads/writes through
it. Best for: large-scale, predictable cost, when you already have
a bucket (e.g. Garage S3, Cloudflare R2, AWS S3).

```sql
ATTACH 'md:?motherduck_token=...' AS oideachais;
USE oideachais;
-- All Parquet files live in your bucket; metadata in MotherDuck
```

### 3. DuckLake on MotherDuck (KCG `oideachais` pattern)

DuckLake stores the catalog in a single SQL database (Postgres
in KCG) and the data in Parquet files in object storage.
MotherDuck reads the catalog + files as one logical database.

```sql
ATTACH 'ducklake:postgres://lakehouse-postgres:5432/cianfhoghlaim_catalog
        ?data_path=s3://ducklake/cianfhoghlaim/' AS cianfhoghlaim_ducklake;
USE cianfhoghlaim_ducklake;
```

Pros: ACID transactions, schema evolution, time-travel queries,
zero catalog ops burden. Cons: requires the Postgres catalog
sidecar.

### 4. Own-compute DuckLake

Same DuckLake pattern but you run the DuckDB compute yourself
(on `bunchloch` M4 in KCG). No MotherDuck service. Use when you
need zero-egress, on-prem, or air-gapped.

## Decision tree

```
Need cloud scale + SQL + REST + Dives?  →  MotherDuck (managed)
└─ Own the bucket / want predictable cost?  →  BYOB
   └─ Need ACID + time-travel + schema evolution?  →  DuckLake
      └─ Cannot use cloud?  →  Own-compute DuckLake
```

## When NOT to use MotherDuck

- Workload is < 1 GB and < 10 users → use a single DuckDB file
- Heavy OLTP (1000s of writes/sec) → use Postgres or CockroachDB
- Pure vector search at > 100M rows → use LanceDB Cloud or Qdrant
- Strict data-residency requirement that forbids US data centers
  → use own-compute DuckLake on EU-region Hetzner

## Pricing + ROI (the short version)

| Pattern | $/GB-month | $/query | Min spend | Best when |
|:--|--:|--:|--:|:--|
| Managed MD | 0.029 | serverless | $0 | Prototypes, small workloads |
| BYOB | 0.023 (storage only) | serverless | $0 | Predictable cost, large data |
| DuckLake on MD | 0.023 (storage) + Postgres | serverless | $50/mo Postgres | ACID + time-travel |
| Own-compute | 0 (you own) | 0 | hardware only | Air-gapped, strict residency |

The `motherduck-pricing-roi` material that was a separate skill is
captured here. For deep ROI models or a specific economic-buyer
pitch, see
[the MotherDuck pricing whitepaper](https://motherduck.com/pricing).

## Migration path (from Snowflake / Redshift / Postgres / dbt)

```
1. Identify the highest-value table (one query the team runs daily)
2. CTAS-export it from the source warehouse to Parquet on S3
3. ATTACH the Parquet directory to MotherDuck
4. Rewrite the query in DuckDB SQL
5. Validate row counts + checksum + a few key business metrics
6. Switch the dashboard to MotherDuck
7. Repeat for the next table; cut over one table per week
```

Cut over **one table at a time** so you can rollback. Never do a
big-bang migration. The `motherduck-migrate-to-motherduck` skill's
content is captured in this section.

## End-to-end pipeline (raw → staging → analytics → serving)

```
[DuckLake raw]                    (Parquet on S3, append-only)
   ↓ dlt source → dlt resource
[DuckLake staging]                (typed, deduped, partitioned)
   ↓ BAML extraction (optional)
[DuckLake analytics]              (denormalised, joined, aggregated)
   ↓ MotherDuck Dive / marimo
[Consumer surface]                (dashboard, notebook, agent)
```

The `motherduck-build-data-pipeline` skill's content is captured
here. For DLT-specific ingestion patterns, see
`dlt/SKILL.md` and `cianfhoghlaim-storage/SKILL.md`.

## Partner / multi-tenant delivery

For consultancies delivering the same MotherDuck architecture to
multiple clients:

- **One MotherDuck organisation per client** (not one shared org
  with all clients).
- **Service-account token per client**, scoped to read-only or
  read-write as needed. Token in Infisical `dev-baile` under
  `motherduck/{client_slug}/token`.
- **Per-client database inside the org**; do not share databases
  across clients even if the schema is identical.
- **Region pinning**: pick a MotherDuck region (US-East, EU-West,
  AP-South) per client; never let data cross regions.
- **Residency attestation**: provide a written attestation for
  the client's security review that the data never leaves the
  pinned region.

## Pair this skill with

- `motherduck/SKILL.md` — the master router + the MCP section
- `motherduck-data-modeling/SKILL.md` — schema + ingestion
- `motherduck-analytics/SKILL.md` — SQL + Dives + dashboards
- `motherduck-connections/SKILL.md` — wiring (Postgres endpoint, MCP)
- `cianfhoghlaim-storage/SKILL.md` — the KCG DuckLake-on-MotherDuck
  storage mental model

## Cross-references

- [MotherDuck storage overview](https://motherduck.com/docs)
- [DuckLake 1.0 announcement](https://motherduck.com/blog/announcing-ducklake-1-0-on-motherduck/)
- [MotherDuck pricing](https://motherduck.com/pricing)
- [Migration playbook](https://motherduck.com/learn)
