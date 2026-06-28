# Agent 07 — Apache Iceberg + Lakekeeper (REST Catalog)

**Date:** 2026-06-28 23:08
**Wave:** 1, Agent 07 of 25
**Budget:** ~200 BrowserBase credits (used ~8)
**Sibling spec:** `phase-1b/P1B-08-garage-iceberg-lakekeeper.md`

## TL;DR

Apache Iceberg is the **table format** (open spec, Apache-2.0) that
guarantees ACID writes, hidden partitioning, partition evolution, sort
orders and time-travel on top of Parquet in object storage. PyIceberg is
the **Python client** that lets Dagster / DLT / DuckDB / marimo read
& write Iceberg tables without a JVM (currently **0.11.1** on PyPI,
`pip install "pyiceberg[s3fs,duckdb,pyarrow]"`). **Lakekeeper** is the
**Iceberg REST Catalog implementation** that KCG runs on port 8181 — it
is a **Rust rewrite** at `lakekeeper/lakekeeper` (NOT the older
`treeverse/lakekeeper` referenced in P1B-08), shipped as a single
binary at `quay.io/lakekeeper/catalog:latest`, and exposes the standard
`/v1/*` REST endpoints (`/v1/config`, `/v1/namespaces`,
`/v1/namespaces/{ns}/tables`, `/v1/namespaces/{ns}/tables/{t}`,
`/v1/prefix/{path}`, `/v1/oauth/tokens`) plus first-class features the
KCG stack does not yet use: OIDC, vended credentials, soft-delete +
undrop, row/column security, and **generic-table registration** of
Lance / Delta / Parquet (relevant to the `lance-namespace` sidecar).

The Iceberg v1/v2/v3 spec defines a snapshot model where every write
creates an immutable snapshot pointing to a manifest list of Avro
manifest files, each referencing Parquet data files. Time-travel is
either `snapshot-id`, `as-of-timestamp`, or `branch/tag`. Partition
specs are versioned separately from the schema, so partition evolution
(adding `month(ts)` next to `day(ts)`) is a metadata-only operation —
no data rewrite. Sort orders are likewise versioned; engines can
choose to push down sort-aware readers.

## Code

### KCG anchor files

| Path | Purpose |
|:--|:--|
| `infrastructure/stacks/lakehouse/compose.yaml:189-228` | `lakekeeper-migrate` + `lakekeeper` services, `quay.io/lakekeeper/catalog:latest`, port 8181 + metrics 9100 |
| `infrastructure/stacks/lakekeeper/README.md` | Standalone lakekeeper README (older `treeverse` reference, see Refactor #1) |
| `infrastructure/stacks/lakehouse/init-db.sql` | Postgres schema for catalog metadata |
| `infrastructure/stacks/lakehouse/notebooks/README.md` | marimo notebook architecture showing Lakekeeper → Garage layering |
| `openspec/changes/2026-06-28-browserbase-phase-1a-decisions/specs/oideachais-pipeline/spec.md:25-38` | `Lakehouse uses Iceberg format on Garage S3 via Lakekeeper catalog` requirement (Phase 1A delta) |

### Canonical Lakekeeper `compose.yaml` block (excerpted, lines 219-228)

```yaml
lakekeeper:
  image: quay.io/lakekeeper/catalog:latest
  container_name: lakehouse-lakekeeper
  restart: unless-stopped
  command: ["serve"]
  ports:
    - "${LAKEKEEPER_PORT:-8181}:8181"
    - "${LAKEKEEPER_METRICS_PORT:-9100}:9000"
  environment:
    LAKEKEEPER__PG_DATABASE_URL_READ:  ${PLANETSCALE_DATABASE_URL:-postgresql://lakekeeper:devpassword@postgres:5432/lakekeeper}
    LAKEKEEPER__PG_DATABASE_URL_WRITE: ${PLANETSCALE_DATABASE_URL:-postgresql://lakekeeper:devpassword@postgres:5432/lakekeeper}
    LAKEKEEPER__PG_ENCRYPTION_KEY:    ${LAKEKEEPER_ENCRYPTION_KEY:-abcdef0123…}
    LAKEKEEPER__PG_SSL_MODE:          ${LAKEKEEPER_SSL_MODE:-prefer}
    LAKEKEEPER__LISTEN_PORT:          "8181"
    LAKEKEEPER__BASE_URI:             ${LAKEKEEPER_BASE_URI:-http://lakekeeper.cianfhoghlaim.ie}
    LAKEKEEPER__SERVE_SWAGGER_UI:     "true"
```

### PyIceberg → Lakekeeper client wiring (canonical pattern)

```python
from pyiceberg.catalog import load_catalog

# Connect to the KCG Lakekeeper instance (port 8181 inside lakehouse-net)
catalog = load_catalog(
    "kcg_lakehouse",
    **{
        "type": "rest",
        "uri":   "http://lakehouse-lakekeeper:8181",   # LAKEKEEPER_URI
        "s3.endpoint":   "http://lakehouse-garage:3900",  # GARAGE_ENDPOINT_URL
        "s3.region":     "garage",
        "s3.access-key-id":     "${GARAGE_ACCESS_KEY}",
        "s3.secret-access-key": "${GARAGE_SECRET_KEY}",
        "warehouse": "s3://lakehouse-bucket/iceberg/",
    },
)

# Time-travel via snapshot ID
table = catalog.load_table("curriculum.leaving_cert_mathematics")
snap = table.history()[-1].snapshot_id
old = table.scan(snapshot_id=snap).to_arrow()

# Or as-of-timestamp
old = table.scan(as_of_timestamp=1719500000000).to_arrow()

# Partition evolution: add `month(ts)` next to existing `day(ts)`
with table.update_spec() as spec:
    spec.add_field("month(ts)")

# Sort-order evolution (Z-order for vector index hot loop)
with table.replace_sort_order() as order:
    order.z_order("embedding_id", "doc_id")
```

### Iceberg REST Catalog — canonical endpoint surface (from `iceberg.apache.org/spec/` and the Iceberg OpenAPI bundle at `iceberg-rest-catalog-spec.yaml`)

```
GET    /v1/config                                              # Server config (overrides, defaults)
POST   /v1/oauth/tokens                                        # OAuth2 client-credentials / token-exchange
GET    /v1/namespaces                                          # List namespaces
POST   /v1/namespaces                                          # Create namespace ({"namespace":[...],"properties":{}})
GET    /v1/namespaces/{ns}                                     # Load namespace properties
HEAD   /v1/namespaces/{ns}                                     # Existence check
DELETE /v1/namespaces/{ns}                                     # Drop namespace (cascading tables if `purge`)
POST   /v1/namespaces/{ns}/properties                          # Set / remove properties
GET    /v1/namespaces/{ns}/tables                              # List tables
POST   /v1/namespaces/{ns}/tables                              # Create table (full Iceberg CreateTableRequest)
GET    /v1/namespaces/{ns}/tables/{t}                          # Load table metadata (returns metadata.json snapshot pointer)
HEAD   /v1/namespaces/{ns}/tables/{t}                          # Existence check
DELETE /v1/namespaces/{ns}/tables/{t}                          # Drop table (optional `purge=true`)
POST   /v1/namespaces/{ns}/tables/{t}                          # Commit table update (atomic snapshot swap)
GET    /v1/namespaces/{ns}/tables/{t}/metrics                  # Commit metrics (optional, opt-in)
POST   /v1/namespaces/{ns}/tables/{t}/credentials              # Get vended credentials (S3 / GCS / ADLS)
POST   /v1/namespaces/{ns}/register                            # Register an existing metadata.json
POST   /v1/namespaces/{ns}/tables/{t}/plan                     # Plan server-side scan tasks (optional)
POST   /v1/tables/rename                                       # Atomic rename across namespaces
POST   /v1/tables/{t}/commit                                   # Atomic multi-table commit (multi-warehouse txn)
POST   /v1/prefix/{path}                                       # S3-like list for storage credential vending
GET    /v1/warehouses                                          # (Lakekeeper extension) Manage warehouses
```

Authentication: OAuth2 bearer (`Authorization: Bearer …`) for
production; SIGv4 (`rest-sigv4` extra in PyIceberg) for AWS-native
catalogs; `IcebergErrorHandler` translates HTTP 4xx → `pyiceberg.exceptions`.

### Iceberg table snapshot model (conceptual)

```
metadata.json (current)                  ── replaced atomically on every write
  ├─ schemas[N]          (id-keyed, evolves via union-by-name / add-field)
  ├─ partition-specs[N]  (id-keyed, partition evolution = metadata-only)
  ├─ sort-orders[N]      (id-keyed, Z-order / lexicographic)
  ├─ snapshot-log[]      (each entry: {snapshot-id, timestamp-ms, schema-id, summary})
  ├─ snapshots[N]        (each: {manifest-list, summary, schema-id, partition-spec-id})
  └─ refs                 (main, audit branches, tags)

manifest-list (Avro)            ── N manifest files
  └─ manifest (Avro)            ── M data files + M delete files
       ├─ data_file:    s3://…/part-00000-…parquet  (file_path, partition_tuple, metrics)
       └─ delete_file:  positional (roaring bitmap) OR equality (Parquet)
```

## Env

| Env var (KCG) | Value | Source |
|:--|:--|:--|
| `LAKEKEEPER_URI` | `http://lakehouse-lakekeeper:8181` | `compose.yaml:221-228` |
| `LAKEKEEPER_PORT` | `8181` | compose env |
| `LAKEKEEPER_METRICS_PORT` | `9100` | compose env (scrape → Prom / OTel collector) |
| `LAKEKEEPER_BASE_URI` | `http://lakekeeper.cianfhoghlaim.ie` | compose env |
| `LAKEKEEPER_ENCRYPTION_KEY` | `infisical://dev-baile/lakekeeper/encryption_key` (64-char hex) | Locket sidecar |
| `PLANETSCALE_DATABASE_URL` | `postgresql://lakekeeper:…@postgres:5432/lakekeeper` | compose env |
| `GARAGE_ENDPOINT_URL` | `http://lakehouse-garage:3900` | compose env |
| `AWS_DEFAULT_REGION` | `garage` | compose env |
| `LAKEKEEPER__AUTH_DISABLE` | `"true"` (dev only) | P1B-08 §"Env" |
| PyIceberg extras | `s3fs,duckdb,pyarrow,rest-sigv4` | `py.iceberg.apache.org/` installation table |

PyIceberg install: `pip install "pyiceberg[s3fs,duckdb,pyarrow,rest-sigv4]"`
(currently 0.11.1, tagged `pyiceberg-0.11.1` on GitHub). The new
optional `pyiceberg-core` extra pulls in `iceberg-rust` for JVM-free
performance on heavy scans.

## CCC anchors

- `infrastructure/stacks/lakehouse/compose.yaml:189` — `lakekeeper-migrate` service with `command: migrate`
- `infrastructure/stacks/lakehouse/compose.yaml:211` — `lakekeeper` service `image: quay.io/lakekeeper/catalog:latest`
- `infrastructure/stacks/lakehouse/compose.yaml:194` — `LAKEKEEPER__PG_DATABASE_URL_WRITE` template
- `infrastructure/stacks/lakehouse/compose.yaml:223` — `LAKEKEEPER__PG_ENCRYPTION_KEY`
- `infrastructure/stacks/lakehouse/compose.yaml:227` — `LAKEKEEPER__BASE_URI`
- `infrastructure/stacks/lakehouse/README.md:87` — Lakekeeper row in lakehouse stack table (image, port, role)
- `infrastructure/stacks/lakekeeper/README.md:38-55` — env var table (older dev-only stack)
- `openspec/changes/2026-06-28-browserbase-phase-1a-decisions/specs/oideachais-pipeline/spec.md:25-38` — capability requirement
- `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/P1B-08-garage-iceberg-lakekeeper.md` — sibling Phase 1B spec

Search terms: `"lakekeeper"`, `"LAKEKEEPER__"`, `"iceberg"`,
`"pyiceberg"`, `"rest-catalog-spec"`, `"snapshot_id"`,
`"as_of_timestamp"`, `"vended credentials"`, `"soft-delete"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-09 | Initial Garage deploy (single node) |
| 2025-12 | Migrated to 3-node Garage cluster (HA) |
| 2026-01 | Added Lakekeeper (Iceberg REST Catalog) — `treeverse/lakekeeper` Java impl |
| 2026-03 | Migrated from raw Parquet to Iceberg format |
| 2026-04 | Added Lance Blob (large object support) |
| 2026-05 | Lakekeeper upstream moved from `treeverse/lakekeeper` (Java) to `lakekeeper/lakekeeper` (Rust rewrite, `iceberg-rust` core) |
| 2026-06 | P1B-08 written — still references `treeverse/lakekeeper` (drift!); see Refactor #1 |
| 2026-06 | `extend-lakehouse-with-nimtable-olake-lancedb` change adds Nimtable UI + Olake CDC + LanceDB Viewer |
| 2026-06 | PyIceberg 0.11.1 latest on PyPI (sibling `iceberg-python` repo) |
| 2026-06-28 | Phase 2 Agent 07 reconciles spec ↔ upstream, surfaces 8 refactor opportunities |

## Anti-patterns

1. **Don't bypass Lakekeeper for direct S3 writes** — Iceberg ACID requires the catalog to atomically swap `metadata.json`. PyIceberg / DuckDB-Iceberg → Garage without Lakekeeper writes a "ghost" table that no future snapshot can resolve.
2. **Don't run Lakekeeper in `AUTH_DISABLE=true` in production** — P1B-08 notes dev-only; production must wire `LAKEKEEPER__AUTH__*` + Pocket ID OIDC (`/v1/oauth/tokens`).
3. **Don't keep the dev 64-hex `LAKEKEEPER_ENCRYPTION_KEY` in prod** — `compose.yaml:195` ships a placeholder; rotation requires re-encryption of all stored credentials.
4. **Don't write `metadata.json` next to data files directly** — always go through the catalog `commit` endpoint, otherwise snapshots collide and only one writer "wins" silently.
5. **Don't assume v1 schema evolution is enough** — `union_by-name` for nested structs needs PyIceberg ≥ 0.9; pinned to <0.7 it silently drops fields. Pin a floor in `pyproject.toml`.
6. **Don't query partition columns that no longer exist in the spec** — old data files reference the old partition-spec-id; use `table.scan(selected_fields=("…",))` + `partition_filter` and let the planner rewrite.
7. **Don't rely on positional delete files for streaming workloads** — equality deletes are slower to compact but cheaper to merge; Lakekeeper + Iceberg v2 supports both, but PyIceberg's default writer emits positional only.
8. **Don't share `pg_database_url_read == pg_database_url_write`** — single Postgres is fine for dev (current setup) but production should split read-replica writes to a primary + reads from a replica, requiring both `LAKEKEEPER__PG_DATABASE_URL_{READ,WRITE}` (already templated, just needs separate Infisical entries).
9. **Don't enable `LAKEKEEPER__SERVE_SWAGGER_UI=true` in prod** — leak schema + exposes mutations to anyone with network reach; gateway via Pocket ID first.
10. **Don't disable Iceberg's `write.object-storage.enabled` checks** — Lakekeeper vends S3 credentials with `s3:PutObject` only; missing IAM permission surfaces as `403` deep in the writer stack, not at commit time.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Table format | Iceberg v2 (current 0.11.1 writes v2; v3 preview) | ACID + hidden partitioning + Python ergonomics |
| Catalog | Lakekeeper (`quay.io/lakekeeper/catalog`) | Rust rewrite, OIDC-native, soft-delete, generic-tables, Apache-2.0 |
| Catalog implementation language | Rust (`iceberg-rust`) | Single binary, no JVM, low memory, fast cold start |
| Storage layer | Garage (S3-compatible) on port 3900 | Self-hosted, no AWS dependency |
| Metadata DB | Postgres / PlanetScale (`lakehouse_catalog`) | Already used; Lakekeeper is just another tenant |
| Auth | Pocket ID OIDC → `LAKEKEEPER__AUTH__*` (prod) / `AUTH_DISABLE=true` (dev) | Single sign-on across lakehouse + Pulumi + Langfuse |
| Python client | `pyiceberg[s3fs,duckdb,pyarrow]` | Dagster + DLT + marimo all already on pyarrow |
| Snapshot policy | `cherry-pick` from main + tag for canonical releases | Standard Iceberg pattern; maps to marimo "snapshot as of" |
| Partitioning | Hive-style `day(event_ts)` → evolve to `month(event_ts)` | KCG time-series curriculum data; partition evolution = metadata only |
| Sort orders | None by default; Z-order on `(embedding_id)` for the vector-search hot path | Lazy; enable when query profiler shows sort savings |
| Soft-delete window | 7 days (Lakekeeper default) | Recover from accidental DLT `replace-mode` overwrite |
| Generic-tables | Register Lance tables in Lakekeeper via `lance-namespace` sidecar (port 8182) | Single catalog governs Parquet + Lance + Delta |
| CDC ingestion | Olake 0.1.5 → Iceberg (`lakehouse-olake`, ephemeral) | Postgres / MySQL / Mongo → Iceberg without dlt |
| Catalog UI | Nimtable 0.1.6 (port 3018, private) | Snapshot history + schema inspection + data preview |

## §8 Refactor opportunities

1. **Update repo references** — P1B-08 still says
   `github.com/treeverse/lakekeeper`; the upstream moved to
   `github.com/lakekeeper/lakekeeper` (Rust rewrite, Apache-2.0,
   `iceberg-rust` core). Update P1B-08 §"CCC anchors" + README +
   `.agents/skills/lakehouse/SKILL.md` (if any) to point to the new
   repo; the Phase 1A spec at `oideachais-pipeline/spec.md:25-38` is
   already repo-agnostic and survives.
2. **Promote `LAKEKEEPER__AUTH__OIDC` to non-dev compose** — `AUTH_DISABLE=true` ships in `compose.yaml:228` of the lakehouse stack (comment says "dev only"). Add a `lakehouse.prod.yaml` overlay (or use Komodo template) that wires Pocket ID discovery URL + client ID/secret via Infisical. Keeps dev fast, prod safe.
3. **Drop the `rest-sigv4` extra from the default PyIceberg install in KCG** — we never target AWS Glue / S3 Tables directly; pulling in `rest-sigv4` is unnecessary attack surface. Keep it in the dlthub-platform workspace.
4. **Add `LAKEKEEPER__LISTEN_ADDR` not just `LISTEN_PORT`** — current compose (line 226) sets `LISTEN_PORT=8181` but not `LISTEN_ADDR`; Lakekeeper defaults to `0.0.0.0` which is fine for the Docker network but should be explicit for K8s / Komodo IPv6 dual-stack.
5. **Add a Dagster asset_check for Lakekeeper `/v1/config`** — the
   `cognify/rules/garage_health.py` already has a Garage node check;
   sibling `cognify/rules/lakekeeper_health.py` should poll
   `GET /v1/config` and assert the catalog returns the configured
   `overrides` + `defaults`. Catches drift between `LAKEKEEPER__BASE_URI`
   and the actual deployed route.
6. **Wire PyIceberg `REST_CATALOG_TESTING__KEEP_RESPONSES=true` in
   tests only** — P1B-08 doesn't have a CI test that exercises
   Lakekeeper; add a marimo smoke-test under `stacks/lakehouse/notebooks/`
   that creates a namespace, writes a 1-row table, time-travels to
   snapshot 0, and asserts equality.
7. **Promote soft-delete + undrop** — Lakekeeper supports time-bounded
   soft-delete (`/v1/namespaces/{ns}/tables/{t}` with `?purge=false`).
   KCG's DLT pipelines run in `replace-mode`; enabling soft-delete in
   Lakekeeper means a Dagster sensor can `undrop` a table within 7
   days. Costs nothing in storage; gives free rollback.
8. **Wire `lance-namespace` to register Lance tables as Lakekeeper
   "generic tables"** — the `lakehouse-lance-namespace` sidecar (port
   8182) currently ships separately; the upstream docs
   (`docs.lakekeeper.io` feature #6) explicitly support registering
   non-Iceberg tables as first-class governed objects. Unifying means
   one RBAC surface for Parquet + Lance + Delta instead of three.

## Files to read next

- `infrastructure/stacks/lakehouse/README.md` (line 87 — lakehouse stack table)
- `infrastructure/stacks/lakehouse/compose.yaml` (lines 189-228 — full Lakekeeper block)
- `infrastructure/stacks/lakehouse/init-db.sql` (Postgres schema)
- `openspec/changes/2026-06-28-browserbase-phase-1a-decisions/specs/oideachais-pipeline/spec.md:25-38`
- `.agents/skills/oideachais-pipeline/SKILL.md` (downstream consumer)
- `.agents/skills/infrastructure-stacks/SKILL.md` (6-file GOLD_STANDARD pattern)
- `py.iceberg.apache.org/api/` (Python `Table` class API)
- `py.iceberg.apache.org/configuration/` (catalog properties reference)
- `iceberg.apache.org/spec/#the-rest-catalog` (canonical REST spec)
- `github.com/lakekeeper/lakekeeper/tree/main/examples` (docker-compose reference)
- `docs.lakekeeper.io/getting-started/` (helm + binary + k8s operator)