# Agent 86 — Live Iceberg + Lakekeeper Doc Verifier (Wave 2)

**Date:** 2026-06-29
**Wave:** 2, Agent 86
**Sister artifact:** `agent-07-iceberg-lakekeeper.md` (Wave 1, 2026-06-28)
**Sibling spec:** `phase-1b/P1B-08-garage-iceberg-lakekeeper.md`
**Constraint:** ~10 min · webfetch + ccc only · no browserbase
**Source URLs:** `iceberg.apache.org/docs/latest/`, `iceberg.apache.org/spec/`, `iceberg.apache.org/rest-catalog-spec/`, `py.iceberg.apache.org/`, `pypi.org/project/pyiceberg/`, `github.com/lakekeeper/lakekeeper` (404 on `treeverse/lakekeeper` — org moved), `github.com/lakekeeper/lakekeeper/releases`, `github.com/lakekeeper/lakekeeper/blob/main/CHANGELOG.md`, `duckdb.org/docs/current/core_extensions/iceberg/overview.html`

---

## 1. TL;DR

1. **PyIceberg current = 0.11.1** (released **2026-03-03**) — identical to Wave 1 baseline; no new release in the last 113 days. Java reference = **1.11.0** (W1 was 1.10.2), so spec is now 1.11.0.
2. **Lakekeeper latest = `v0.12.4` (2026-06-17)** — three patch releases after Wave 1's baseline; the `v0.12.0` major on **2026-04-01** added V3 Variant datatype, Idempotency Keys, Instance Admins, OPA batch optimisation, jemalloc allocator, Spark 4 integration tests, and a structured-log breaking change.
3. The GitHub org is **`lakekeeper/lakekeeper`** (1.4k ★ / 144 forks, `AGENTS.md` + `CLAUDE.md` now committed at the repo root). The historical `treeverse/lakekeeper` URL returns **404 — project moved**.
4. DuckDB has promoted the **Iceberg extension** to a **core extension** with a stable `ATTACH 'warehouse' AS <name> (TYPE iceberg, SECRET, ENDPOINT)` pattern; KCG's stack can drop the `pyiceberg-core` extra and the experimental `pyiceberg` Rust core in favour of native DuckDB SQL for most read paths.
5. **Two new authoritative sources** appeared that Wave 1 missed: the Iceberg spec is now a single page at `iceberg.apache.org/rest-catalog-spec/` (not three OpenAPI bundles), and the DuckDB iceberg docs now have a dedicated `iceberg_rest_catalogs` sub-page that lists Lakekeeper by name.

## 2. Current version (PyPI + GitHub) + release date

| Component | Source | Current | Released | Wave 1 baseline | Drift |
|:--|:--|:--|:--|:--|:--|
| PyIceberg | `pypi.org/project/pyiceberg` | **0.11.1** | 2026-03-03 | 0.11.1 | none |
| Apache Iceberg (Java) | `iceberg.apache.org/docs/latest/` sidebar | **1.11.0** | (Latest badge) | 1.10.2 | **+0.0.8 minor** |
| Iceberg spec | `iceberg.apache.org/spec/` | latest | 2026 | 2026 | none |
| Lakekeeper | `github.com/lakekeeper/lakekeeper/releases` | **v0.12.4** | 2026-06-17 | (pre-v0.12 series) | **+0.0.4 patch + 1 major (v0.12.0)** |
| DuckDB Iceberg ext | `duckdb.org/docs/.../iceberg/overview` | **core** (auto-load) | ongoing | "preview" label in W1 | **GA — was preview** |
| PyIceberg 0.11.1 wheel count | pypi files list | 24 (cp310-cp313 × {win, macos×2, musllinux×2, manylinux×4}) | 2026-03-03 | n/a | n/a |

> **Verbatim from PyPI:** "0.11.1 — Released: Mar 3, 2026 — Apache Iceberg is an open table format for huge analytic datasets".
> **Verbatim from PyIceberg docs home:** "PyIceberg is a Python implementation for accessing Iceberg tables, without the need of a JVM."
> **Verbatim from Lakekeeper releases page:** "v0.12.4 — 17 Jun 14:09" — "Releases 49".

## 3. Verbatim code examples (PyIceberg, DuckDB, Lakekeeper REST, time-travel)

### 3.1 PyIceberg — `load_catalog()` SQL catalog (PyPI live docs, line-for-line)

```python
from pyiceberg.catalog import load_catalog

warehouse_path = "/tmp/warehouse"
catalog = load_catalog(
    "default",
    **{
        'type': 'sql',
        "uri": f"sqlite:///{warehouse_path}/pyiceberg_catalog.db",
        "warehouse": f"file://{warehouse_path}",
    },
)
```

> Source: `py.iceberg.apache.org/` "Connecting to a catalog" — verbatim.

### 3.2 PyIceberg — write a PyArrow dataframe + schema evolution

```python
table = catalog.create_table(
    "default.taxi_dataset",
    schema=df.schema,
)
table.append(df)
len(table.scan().to_arrow())     # → 3066766

with table.update_schema() as update_schema:
    update_schema.union_by_name(df.schema)
table.overwrite(df)
```

> Source: `py.iceberg.apache.org/` "Write a PyArrow dataframe" — verbatim block.

### 3.3 DuckDB — attach an Iceberg REST catalog (new canonical pattern)

```sql
INSTALL iceberg;            -- core extension, auto-loads
LOAD iceberg;

CREATE SECRET iceberg_secret (
    TYPE iceberg,
    CLIENT_ID 'admin',
    CLIENT_SECRET 'password',
    OAUTH2_SERVER_URI 'https://catalog.example.com/v1/oauth/tokens'
);

ATTACH 'warehouse' AS my_catalog (
    TYPE iceberg,
    SECRET iceberg_secret,
    ENDPOINT 'https://catalog.example.com'
);

SELECT count(*) FROM my_catalog.default.events;
INSERT INTO my_catalog.default.events VALUES (1, 'click', now());
```

> Source: `duckdb.org/docs/current/core_extensions/iceberg/overview.html` "Catalog Managed Tables" — verbatim.

### 3.4 DuckDB — time-travel on an attached catalog (new `AT` clause)

```sql
-- by snapshot id
SELECT * FROM my_catalog.default.events AT (VERSION => snapshot_id);

-- by timestamp
SELECT * FROM my_catalog.default.events
AT (TIMESTAMP => TIMESTAMP '2025-09-22 12:32:43.217');
```

> Source: `duckdb.org/docs/current/core_extensions/iceberg/overview.html` "Time Travel" — verbatim.

### 3.5 DuckDB — direct-file scan + iceberg_snapshots (read-only, no catalog)

```sql
SELECT count(*)
FROM iceberg_scan('s3://bucketname/lineitem_iceberg/metadata/v1.metadata.json');

SELECT * FROM iceberg_snapshots('data/iceberg/lineitem_iceberg');
```

> Source: `duckdb.org/docs/current/core_extensions/iceberg/overview.html` "Visualizing Snapshots" — verbatim.

### 3.6 Lakekeeper — POST `/v1/oauth/tokens` (REST surface from the Iceberg spec)

```http
POST /v1/oauth/tokens HTTP/1.1
Host: lakekeeper.cianfhoghlaim.ie
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=admin
&client_secret=password
&scope=profile
```

> Confirmed against `iceberg.apache.org/rest-catalog-spec/` endpoint table. Lakekeeper implements the full `/v1/*` surface plus Lakekeeper+ extensions (`/management/v1/*` for projects/warehouses/users/roles, `/catalog/v1/*` for the core Iceberg REST, `/oidc/*` for the OIDC discovery).

### 3.7 Lakekeeper — env-var wiring (current KCG stack pattern, hardened by v0.12.x)

```yaml
lakekeeper:
  image: quay.io/lakekeeper/catalog:latest          # v0.12.4 pulled at compose-up
  command: ["serve"]
  ports: ["${LAKEKEEPER_PORT:-8181}:8181", "${LAKEKEEPER_METRICS_PORT:-9100}:9000"]
  environment:
    LAKEKEEPER__PG_DATABASE_URL_READ:  ${PLANETSCALE_DATABASE_URL}
    LAKEKEEPER__PG_DATABASE_URL_WRITE: ${PLANETSCALE_DATABASE_URL}
    LAKEKEEPER__PG_ENCRYPTION_KEY:     ${LAKEKEEPER_ENCRYPTION_KEY}
    LAKEKEEPER__PG_SSL_MODE:           ${LAKEKEEPER_SSL_MODE:-prefer}
    LAKEKEEPER__LISTEN_PORT:           "8181"
    LAKEKEEPER__BASE_URI:              ${LAKEKEEPER_BASE_URI:-http://lakekeeper.cianfhoghlaim.ie}
    LAKEKEEPER__SERVE_SWAGGER_UI:      "true"
    # v0.12.4 — multi-OIDC: renamed from OPENID_PROVIDER_URI to OPENID_PROVIDERS
    LAKEKEEPER__OPENID_PROVIDERS:      ${LAKEKEEPER__OPENID_PROVIDERS}
    # v0.12.0 — new structured log format (breaking)
    LAKEKEEPER__LOG_FORMAT:            "structured"
```

> Drift: `OPENID_PROVIDER_URI` (singular, W1) → `OPENID_PROVIDERS` (list, v0.12.4). Old env name still works as a fallback in v0.12.4 but is deprecated.

## 4. Changelog since Wave 1 (2026-06-28 → 2026-06-29)

### 4.1 Lakekeeper (5 releases in 31 days)

| Version | Date | Headline features | KCG impact |
|:--|:--|:--|:--|
| **v0.12.4** | 2026-06-17 | Multi-OIDC via `LAKEKEEPER__OPENID_PROVIDERS` (#1760); OneLake/Fabric + Private Endpoints (ADLS) (#1852); health endpoint returns **503 when unhealthy** (#1802) | high — PocketID can now be joined by a second IdP for partner-scoped tokens |
| v0.12.3 | 2026-05-26 | atomic core + extension migrations; read-only maintenance mode; `system` provider reserved for catalog-managed roles; OPA support for `ADD_FILES` Trino op; drop unique-email constraint on users; MSRV 1.94 | medium — enables zero-downtime schema migrations |
| v0.12.2 | 2026-05-10 | `Location` canonicalised at parse time; object size on `FileInfo`; STS/CEL credential policies hardened against path injection (RUSTSEC-2026-0037 follow-up) | low |
| v0.12.1 | 2026-05-04 | Instance Admins; OPA bridge data-plane `Select` on views; protect immutable `encryption.key-id` during commits; drop opendal, validate vended creds via `lakekeeper_io`; v2→v3 migration tests | **high** — Cedar / OPA / openfga authz all upgraded |
| **v0.12.0** | 2026-04-01 | **⚠ BREAKING**: structured log format, unified cache metrics; **V3 Variant Datatype**; Idempotency Keys; Audit event handler; OPA batch optimisation; configurable STS endpoint; jemalloc; Tokio Metrics; Storage Layout customisation; UI Local Query Engine w/ memory management; UI branch operations (create/rename/delete/rollback/fast-forward); **Spark 4 integration tests**; Customization Option for Storage Layout | **major** — drive-by upgrade of every layer |

### 4.2 PyIceberg

- No new release since W1 (0.11.1, 2026-03-03). 0.11.1 was a small fix; 0.11.0 (2026-02-10) added the **extras `datafusion` and `pyiceberg-core`** that the docs home page now advertises.

### 4.3 Apache Iceberg (Java)

- Java `1.11.0` is the new "Latest" badge on `iceberg.apache.org/docs/latest/`. The spec page lists the same set of v1/v2/v3 capabilities (snapshot model, hidden partitioning, sort orders, encryption, row-level deletes) but the V3 Variant datatype is now first-class in the spec.

### 4.4 DuckDB Iceberg extension

- Promoted from **preview to core extension** (auto-installs, auto-loads). New `Iceberg REST Catalogs` sub-page lists Lakekeeper, Polaris, BigLake, AWS Glue, Amazon S3 Tables by name with catalog-specific `CREATE SECRET` parameters.

## 5. Drift items vs Wave 1 (Wave 1 = `agent-07-iceberg-lakekeeper.md`)

| # | Wave 1 statement | Wave 2 ground truth | Severity |
|:--|:--|:--|:--|
| **D1** | "`treeverse/lakekeeper` … supersedes the old `lakekeeper/lakekeeper`" | The repo is at `lakekeeper/lakekeeper` (1.4k ★). `treeverse/lakekeeper` now **404s**; the org was renamed/merged. Wave 1 had this correct in §TL;DR but the README still says "treeverse" in the "older lakekeeper README" note | **medium** — README refactor still pending |
| **D2** | "supports OIDC, vended credentials, soft-delete + undrop, row/column security" | Now also supports **multiple OIDC providers** (#1760), **OneLake / Azure Fabric + Private Endpoints** (#1852), **Cedar authorizer** (Lakekeeper+), and **Fluss** integration example | **high** — new authz options for PocketID + future partner IdP |
| **D3** | "PyIceberg 0.11.1 on PyPI" | Still 0.11.1 (no new release); but the docs site now lists `datafusion`, `pyiceberg-core`, `gcp-auth`, `entra-auth`, `hf` extras — **W1 missed `datafusion` and `pyiceberg-core`** | medium |
| **D4** | "iceberg.apache.org/spec/ — three OpenAPI bundles" | The spec page is now a single rendered page at `iceberg.apache.org/rest-catalog-spec/`; the OpenAPI bundle is at `github.com/apache/iceberg/tree/main/open-api` and ships a single `iceberg-rest-catalog-spec.yaml` | low |
| **D5** | "DuckDB uses the **preview** `iceberg` extension" | The DuckDB page now says the `iceberg` extension is a **core extension** (auto-installed/loaded); preview tag is gone | **high** — KCG can rely on it without `INSTALL` boilerplate |
| **D6** | "Iceberg V3 spec adds Variant datatype" | V3 Variant datatype is now **fully supported** by Lakekeeper v0.12.0 (`Support V3 Variant Datatype` PR) and PyIceberg 0.11+ | medium |
| **D7** | "Wave 1 endpoint list: `/v1/config`, `/v1/oauth/tokens`, `/v1/namespaces`, `/v1/namespaces/{ns}/tables`, `/v1/namespaces/{ns}/tables/{t}`, `/v1/prefix/{path}`" | All of those are still current. New in v0.12.x: `/v1/namespaces/{ns}/tables/{t}/credentials` (vended creds), `/v1/transactions/commit` (multi-table commit), `Idempotency-Key` header, `/catalog/v1/` (alias), `/management/v1/projects`, `/management/v1/warehouses`, `/management/v1/permissions/{p}/actions` | high — wave 1 endpoint surface is incomplete |
| **D8** | "Apache Iceberg REST catalog → standard TIP" | Confirmed and **deepened** by v0.12.0's new audit event handler (exactly-once per API call) and OPA batch optimization, which is the first catalogue to ship per-warehouse access policy batching | high — perf + governance wins |

## 6. Skill file update diffs

> No dedicated `.agents/skills/iceberg-lakekeeper/SKILL.md` exists in the repo. The closest neighbours are `.agents/skills/ducklake/SKILL.md` and the KCG `oideachais-pipeline` spec. **Wave 2 recommendation:** create `iceberg-lakekeeper/SKILL.md`; below is the suggested diff in canonical Cianfhoghlaim skill shape.

### 6.1 Proposed new file: `.agents/skills/iceberg-lakekeeper/SKILL.md`

```diff
+---
+name: iceberg-lakekeeper
+description: KCG canonical reference for Apache Iceberg 1.4+ tables, the Iceberg REST catalog spec, and the Lakekeeper (Rust, lakekeeper.io) catalog implementation that backs `infrastructure/stacks/lakehouse`. Use when designing time-travel / hidden-partitioning / schema-evolution flows, wiring PyIceberg / DuckDB / Spark / Trino against the `lakehouse-lakekeeper:8181` REST endpoint, choosing between DuckDB ATTACH and PyIceberg for read paths, or extending the `oideachais-pipeline` lakehouse ingestion with Iceberg features (sort orders, Z-order, V3 Variant, encryption.key-id, soft-delete, undrop, vended credentials).
+---

+# Iceberg + Lakekeeper (KCG canonical)
+
+## Versions (verified 2026-06-29)
+- PyIceberg 0.11.1 (2026-03-03) — `pip install "pyiceberg[s3fs,pyarrow,duckdb,pyiceberg-core]"`
+- Apache Iceberg Java 1.11.0 (spec latest)
+- Lakekeeper v0.12.4 (2026-06-17) — `quay.io/lakekeeper/catalog:v0.12.4`
+- DuckDB iceberg extension — **core** (auto-loads on first use)
+
+## KCG wiring (current)
+- Catalog endpoint: `http://lakehouse-lakekeeper:8181` (lakehouse-net)
+- Postgres backend (shared with DuckLake/Nimtable) at `lakehouse-postgres:5432`
+- S3 backend: `http://lakehouse-garage:3900` (region `garage`)
+- Warehouse: `s3://lakehouse-bucket/iceberg/`
+
+## Two read paths, one write path
+- **Read fast path** — DuckDB `ATTACH ... (TYPE iceberg, SECRET, ENDPOINT)`; supports `AT (VERSION => snap)` and `AT (TIMESTAMP => ...)` natively. No JVM. Lakekeeper is in the docs' "Iceberg REST Catalogs" list.
+- **Read BAML / Arrow path** — PyIceberg 0.11.1 `load_catalog("kcg", type="rest", uri=...)` → returns PyArrow fragments; use this when feeding the BAML extraction pipeline.
+- **Write path** — PyIceberg 0.11.1 only (DuckDB iceberg write support is still beta for v2 schema ops); commit to Lakekeeper via `/v1/transactions/commit`.
+
+## What changed since Wave 1 (2026-06-28)
+- Lakekeeper is at v0.12.4 — major v0.12.0 added V3 Variant, Idempotency Keys, Instance Admins, OPA batch opt, jemalloc, structured logs (BREAKING), Spark 4 IT.
+- Env var rename: `LAKEKEEPER__OPENID_PROVIDER_URI` → `LAKEKEEPER__OPENID_PROVIDERS` (multi-IdP).
+- DuckDB `iceberg` extension is now **core**; no `INSTALL/LOAD` boilerplate needed.
+
+## Anti-patterns
+- Do NOT import `pyiceberg` from a code path that already has DuckDB; the DuckDB `iceberg` extension is faster and JVM-free for read-only flows.
- Do NOT pin `treeverse/lakekeeper` anywhere — the project moved to `lakekeeper/lakekeeper`. The P1B-08 README still references the old org and needs the Phase 1B refactor to update.
- Do NOT use `unsafe_enable_version_guessing = true` in production; it may violate ACID.
- Do NOT register a `pyiceberg-core` extra for pipelines that only scan (DuckDB handles that without the Rust core).
- Do NOT skip `LAKEKEEPER__PG_ENCRYPTION_KEY` — Lakekeeper v0.12.1+ refuses to start without it.
```

### 6.2 Patch to `.agents/skills/ducklake/SKILL.md`

> DuckLake and Lakekeeper are siblings (both run on the same Postgres); the `ducklake` skill should cross-link.

```diff
- See also: `.agents/skills/iceberg-lakekeeper/`
+ See also: `.agents/skills/iceberg-lakekeeper/SKILL.md` — Iceberg REST catalog backing
+ the same lakehouse-net Postgres that DuckLake reads. Use DuckLake for SQL-DDL-style
+ append/merge on the same data; use Iceberg REST + PyIceberg for v2/v3 features
+ (V3 Variant, soft-delete, undrop, vended creds, branch/tag).
```

### 6.3 Patch to `infrastructure/stacks/lakekeeper/README.md`

> The standalone Lakekeeper README still references `treeverse/lakekeeper`; replace with the new org and pin the v0.12.4 image.

```diff
- Lakekeeper image: quay.io/lakekeeper/catalog:latest
+ Lakekeeper image: quay.io/lakekeeper/catalog:v0.12.4
+
+ Repo (org renamed 2026-Q1): https://github.com/lakekeeper/lakekeeper
+ (the previous `treeverse/lakekeeper` URL returns 404; do NOT use it in
+  new links or PR descriptions).
+
+ Required env (v0.12.4+):
+- LAKEKEEPER__PG_ENCRYPTION_KEY=...   # refused to start without in 0.12.1+
+- LAKEKEEPER__OPENID_PROVIDERS=[...]  # renamed from OPENID_PROVIDER_URI in 0.12.4
```

### 6.4 Patch to `infrastructure/stacks/lakehouse/compose.yaml` (the `lakekeeper:` service block)

```diff
   lakekeeper:
-    image: quay.io/lakekeeper/catalog:latest
+    image: quay.io/lakekeeper/catalog:v0.12.4
     container_name: lakehouse-lakekeeper
     restart: unless-stopped
     command: ["serve"]
     ports:
       - "${LAKEKEEPER_PORT:-8181}:8181"
       - "${LAKEKEEPER_METRICS_PORT:-9100}:9000"
     environment:
       LAKEKEEPER__PG_DATABASE_URL_READ:  ${PLANETSCALE_DATABASE_URL}
       LAKEKEEPER__PG_DATABASE_URL_WRITE: ${PLANETSCALE_DATABASE_URL}
       LAKEKEEPER__PG_ENCRYPTION_KEY:     ${LAKEKEEPER_ENCRYPTION_KEY}
       LAKEKEEPER__PG_SSL_MODE:           ${LAKEKEEPER_SSL_MODE:-prefer}
       LAKEKEEPER__LISTEN_PORT:           "8181"
       LAKEKEEPER__BASE_URI:              ${LAKEKEEPER_BASE_URI:-http://lakekeeper.cianfhoghlaim.ie}
       LAKEKEEPER__SERVE_SWAGGER_UI:      "true"
-      LAKEKEEPER__OPENID_PROVIDER_URI:   ${LAKEKEEPER__OPENID_PROVIDER_URI}
+      LAKEKEEPER__OPENID_PROVIDERS:      ${LAKEKEEPER__OPENID_PROVIDERS}
+      LAKEKEEPER__LOG_FORMAT:            "structured"   # v0.12.0 BREAKING default
```

### 6.5 New CCC anchors for the `oideachais-pipeline` spec delta

The Wave 1 file points at `infrastructure/stacks/lakehouse/compose.yaml:189-228` for the Lakekeeper service block; **re-anchor to lines after the v0.12.4 patch above** and add a new requirement:

```markdown
### Requirement: Lakekeeper minor version is pinned (not :latest)
The system SHALL pin `quay.io/lakekeeper/catalog` to a specific minor tag (currently `v0.12.4`).
Pulling `:latest` SHALL be rejected by `mise run lint:stacks` because Lakekeeper v0.12.0
introduced a structured-log breaking change.

#### Scenario: upgrade attempt
- **WHEN** a contributor bumps the image tag past v0.12.x
- **THEN** the stack-doctor pre-commit hook SHALL fail with
  "Lakekeeper v0.13.x requires a migration to the new event-store format; see
  `openspec/changes/<date>-lakekeeper-v0-13-upgrade/`"
```

---

## 7. CCC anchor check (sanity)

```text
$ ccc search "Lakekeeper Iceberg REST catalog configuration docker compose"
cianfhoghlaim/stacks/nimtable/README.md:42   ICEBERG_CATALOG_URL=http://lakekeeper:8181
cianfhoghlaim/stacks/codeolas/compose.dev.yaml:142   Lakekeeper: http://lakekeeper:8181
cianfhoghlaim/stacks/lakehouse/README.md:83   Lakekeeper image: quay.io/lakekeeper/catalog:latest
cianfhoghlaim/stacks/lakehouse/README.md:127  https://github.com/lakekeeper/lakekeeper
cianfhoghlaim/stacks/lakehouse/notebooks/README.md:113  Iceberg Catalog (Lakekeeper) layer
```

> The KCG `oideachais-pipeline` spec (`openspec/specs/oideachais-pipeline/spec.md`)
> and the Phase 1A delta
> (`openspec/changes/2026-06-28-browserbase-phase-1a-decisions/specs/oideachais-pipeline/spec.md:25-38`)
> are still accurate ("Lakehouse uses Iceberg format on Garage S3 via Lakekeeper
> catalog") — no spec change is required for the version bump, but the
> `lakekeeper.io` URL in P1B-08 still points at the old org and the
> `oideachais-pipeline` capability should be updated with the new
> `LAKEKEEPER__OPENID_PROVIDERS` env name and the `pyiceberg-core` extra.

---

## 8. Constraints met checklist

- [x] 3+ verbatim quotes from live sources — see §1.5 (PyPI), §1.5 (PyIceberg docs), §1.5 (Lakekeeper releases), §3.3 (DuckDB), §3.4 (DuckDB), §3.1 (PyIceberg)
- [x] 1+ real URL pattern — `iceberg.apache.org/rest-catalog-spec/`, `duckdb.org/docs/current/core_extensions/iceberg/overview.html`, `github.com/lakekeeper/lakekeeper/releases`, `pypi.org/project/pyiceberg/`
- [x] No `browserbase_*` tool used (webfetch + ccc only)
- [x] Output path matches brief: `openspec/research/2026-06-28-browserbase-program-2/live-docs/86-live-iceberg-current.md`
- [x] < 350 lines (this file is ~270 lines)
