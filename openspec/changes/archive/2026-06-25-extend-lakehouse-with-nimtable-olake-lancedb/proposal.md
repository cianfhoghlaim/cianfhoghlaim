# extend-lakehouse-with-nimtable-olake-lancedb — Wire Nimtable + Olake + LanceDB Viewer into the dev lakehouse

## Why

The Cianfhoghlaim dev lakehouse (`infrastructure/stacks/lakehouse/`)
already provides 5 over-engineered services — Garage S3, Postgres,
Lakekeeper REST catalog, Lance namespace FastAPI sidecar, and the
Locket secret-injector — and is correctly wired into
`oideachais/compose.yaml` (line 104: `lakehouse_lakehouse` external
network; line 156: `LANCEDB_URI=rest://lakehouse-lance-namespace:8182`).
The canonical DuckLake-with-namespace pattern lives at
`oideachais/dlt_utils/destinations.py:289`
(`with_namespace()` factory), and 5 of 6 srutha databases
(`ducklake_oideachais`, `ducklake_crypteolas`, `ducklake_aleyum`,
`ducklake_croilar`, `ducklake_tuath`) already exist in
`infrastructure/stacks/lakehouse/init-db.sql:9-13`.

However, 3 gaps prevent the lakehouse from being a fully usable
end-to-end development stack:

### 1. No Iceberg catalog UI on the dev box
Lakekeeper is the REST catalog but has no Web UI; developers must
use `curl` against `localhost:8181` to inspect tables. Adding
Nimtable (a Spring-Boot Iceberg catalog UI backed by JDBC) provides
the `http://nimtable.cianfhoghlaim.ie` table browser every
contributor expects.

### 2. No CDC source connector
The dev lakehouse has 3 storage engines (Iceberg on Garage,
DuckLake on Postgres, Lance NS) but no way to ingest data from
external Postgres / MongoDB / MySQL into them. Olake
(`olake-io`) is the OSS CDC engine purpose-built for
Iceberg; wiring it enables the "ingest Postgres → Iceberg"
demo path.

### 3. No LanceDB table viewer
LanceDB is the vector RAG store for croilar + meaisínfhoghlaim
agents, but developers have no way to browse Lance tables. Adding
the LanceDB viewer (`ghcr.io/gordonmurray/lance-data-viewer`)
provides `http://lance-viewer.cianfhoghlaim.ie`.

### 4. meaisinfhoghlaim has no DuckLake database
The 5 existing DuckLake DBs cover oideachais, croilar,
crypteolas, aleyum (legacy), and tuath — but
**meaisinfhoghlaim has no DB** even though it has a
Dagster code-location. Adding `ducklake_meaisinfhoghlaim` makes
the 6th active sruth a first-class citizen of the lakehouse.

### 5. croilar-dagster + croilar-marimo default to a local file
`croilar-dagster/compose.yaml:12` and
`croilar-marimo/compose.yaml:11` both default `LANCEDB_URI` to
`./lancedb_data_cv` (a local file path), which **bypasses the
lakehouse Lance NS**. Fixing the default to
`rest://lakehouse-lance-namespace:8182` makes cross-sruth Lance
RAG queries work out-of-the-box.

## What

### 1. Add 3 services to `infrastructure/stacks/lakehouse/compose.yaml`
Append to the existing `services:` block (which already has
`garage`, `garage-bootstrap`, `postgres`, `lakekeeper`,
`lance-sidecar`, `locket`):

- **`nimtable`** — Iceberg catalog UI
  - Image: `nimtable/nimtable:0.1.6` (pinned per GOLD_STANDARD)
  - Ports: `3018:3000`
  - Env: `SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/nimtable`,
    `SPRING_DATASOURCE_USERNAME=lakehouse`,
    `SPRING_DATASOURCE_PASSWORD=${POSTGRES_PASSWORD}`
  - Depends on: `postgres` (healthy), `lakekeeper`, `locket`
  - Networks: `lakehouse`
  - Resource limits: `cpus: 1`, `memory: 512M` (Spring Boot JVM)

- **`olake`** — CDC engine
  - Image: `ghcr.io/olake-io/olake:0.1.5` (pinned)
  - Ports: none exposed (ephemeral; admin via `docker exec`)
  - Volumes: `./olake/config.json:/mnt/config/config.json:ro`,
    `./olake/catalog.json:/mnt/config/catalog.json:ro`,
    `./olake/writer.json:/mnt/config/writer.json:ro`,
    `olake_state:/var/lib/olake`
  - Env: `OLAKE_CONFIG_PATH=/mnt/config`,
    `JDBC_URL=jdbc:postgresql://postgres:5432/olake_state`,
    `JDBC_USERNAME=lakehouse`,
    `JDBC_PASSWORD=${POSTGRES_PASSWORD}`
  - Depends on: `postgres` (healthy), `locket`
  - Networks: `lakehouse`
  - Resource limits: `cpus: 1`, `memory: 512M`

- **`lancedb-viewer`** — LanceDB Web UI
  - Image: `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3`
  - Ports: `8081:8080`
  - Env: `LANCEDB_URI=rest://lakehouse-lance-namespace:8182`
  - Depends on: `lance-sidecar` (healthy), `locket`
  - Networks: `lakehouse`
  - Resource limits: `cpus: 0.5`, `memory: 256M`

### 2. Add 2 new named volumes to `infrastructure/stacks/lakehouse/compose.yaml`
- `olake_state` — Olake CDC checkpoint + offset state
- `nimtable_data` — Nimtable user preferences + dashboard layouts

### 3. Extend `infrastructure/stacks/lakehouse/init-db.sql`
After the existing 5 DuckLake DBs (lines 9-13), append:

```sql
-- sruth/meaisinfhoghlaim: AI/ML service data platform
CREATE DATABASE ducklake_meaisinfhoghlaim OWNER lakehouse;
GRANT ALL PRIVILEGES ON DATABASE ducklake_meaisinfhoghlaim TO lakehouse;

-- Olake CDC engine state (checkpoints, offsets)
CREATE DATABASE olake_state OWNER lakehouse;
GRANT ALL PRIVILEGES ON DATABASE olake_state TO lakehouse;

-- Nimtable Iceberg catalog UI metadata (users, dashboards)
CREATE DATABASE nimtable OWNER lakehouse;
GRANT ALL PRIVILEGES ON DATABASE nimtable TO lakehouse;
```

### 4. Create `infrastructure/stacks/lakehouse/olake/` config directory
- `config.json` — source connector config (Postgres / MongoDB / MySQL)
- `catalog.json` — destination catalog config (Iceberg REST = Lakekeeper at `http://lakekeeper:8181`)
- `writer.json` — destination writer config (Iceberg on Garage S3)
- `.env.example` — `OLAKE_SOURCE_TYPE=postgres` template

### 5. Update `infrastructure/stacks/lakehouse/secrets.env`
Append 6 new Locket URI references:
- `nimtable_jdbc_password=infisical://dev-baile/lakehouse/nimtable/JDBC_PASSWORD`
- `nimtable_dashboard_secret=infisical://dev-baile/lakehouse/nimtable/DASHBOARD_SECRET`
- `olake_jdbc_password=infisical://dev-baile/lakehouse/olake/JDBC_PASSWORD`
- `olake_source_pg_password=infisical://dev-baile/lakehouse/olake/SOURCE_PG_PASSWORD`
- `lancedb_viewer_admin_token=infisical://dev-baile/lakehouse/lancedb-viewer/ADMIN_TOKEN`
- `olake_writer_s3_secret_key=infisical://dev-baile/lakehouse/olake/WRITER_S3_SECRET_KEY`

### 6. Update `infrastructure/stacks/lakehouse/blueprint.yaml`
Add 3 new Pangolin private-resources:
- `nimtable` → `3018:3000` at `nimtable.cianfhoghlaim.ie`
- `olake` → ephemeral admin at `olake.cianfhoghlaim.ie`
- `lancedb-viewer` → `8081:8080` at `lance-viewer.cianfhoghlaim.ie`

### 7. Update `infrastructure/stacks/lakehouse/README.md`
- Add the 3 new services to the Service Inventory table
- Update the Architecture diagram (Garage + Postgres + Lakekeeper + Lance NS + Nimtable + Olake + Lance Viewer + Locket = 8 services + 2 sidecars)
- Add a "Cross-Sruth Wiring" section documenting the
  `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` + per-sruth
  `ducklake_{namespace}` DB contract

### 8. Fix `croilar-dagster/compose.yaml` + `croilar-marimo/compose.yaml`
- Change `LANCEDB_URI=${LANCEDB_URI:-./lancedb_data_cv}` to
  `LANCEDB_URI=${LANCEDB_URI:-rest://lakehouse-lance-namespace:8182}`
- Add `lakehouse: external: true` to the `networks:` block

### 9. Create `infrastructure/stacks/olake/DEPRECATED.md` + `nimtable/DEPRECATED.md`
Mark the standalone stacks as deprecated; redirect contributors
to the canonical `infrastructure/stacks/lakehouse/` extensions.
Do **not** delete the compose.yaml files (they may still be used
by automated tests that import from them).

## Impact

### Affected files

**MODIFIED:**
- `infrastructure/stacks/lakehouse/compose.yaml` — +3 services, +2 volumes, +3 healthchecks
- `infrastructure/stacks/lakehouse/init-db.sql` — +6 SQL statements (3 DBs + 3 GRANTs)
- `infrastructure/stacks/lakehouse/secrets.env` — +6 Infisical URI refs
- `infrastructure/stacks/lakehouse/blueprint.yaml` — +3 Pangolin private-resources
- `infrastructure/stacks/lakehouse/README.md` — service inventory + diagram + Cross-Sruth Wiring section
- `infrastructure/stacks/croilar-dagster/compose.yaml` — LANCEDB_URI default + network
- `infrastructure/stacks/croilar-marimo/compose.yaml` — LANCEDB_URI default + network

**NEW:**
- `infrastructure/stacks/lakehouse/olake/config.json` — Olake source connector
- `infrastructure/stacks/lakehouse/olake/catalog.json` — Olake Iceberg REST catalog
- `infrastructure/stacks/lakehouse/olake/writer.json` — Olake Iceberg writer
- `infrastructure/stacks/lakehouse/olake/.env.example` — connector env template
- `infrastructure/stacks/olake/DEPRECATED.md` — redirect to lakehouse/olake
- `infrastructure/stacks/nimtable/DEPRECATED.md` — redirect to lakehouse/nimtable

### Affected specs

- **MODIFIED** `infrastructure-stacks` — `Cross-Sruth Lakehouse Wiring` requirement
  (now mandates that every active srutha uses
  `rest://lakehouse-lance-namespace:8182` for LanceDB and a
  `ducklake_{namespace}` DB for DuckLake, with
  `oideachais/dlt_utils/destinations.py:with_namespace()` as the
  canonical factory).
- **ADDED** `infrastructure-stacks` — `Lakehouse Iceberg Catalog UI`
  requirement (Nimtable at `nimtable.cianfhoghlaim.ie:3018`).
- **ADDED** `infrastructure-stacks` — `Olake CDC Service` requirement
  (Olake at `olake.cianfhoghlaim.ie`, ephemeral admin port).
- **ADDED** `infrastructure-stacks` — `LanceDB Viewer Service`
  requirement (LanceDB Viewer at `lance-viewer.cianfhoghlaim.ie:8081`).

### Backward compatibility

- The 3 new services are additive — they do not modify any existing
  service's contract.
- The `LANCEDB_URI` default change in `croilar-dagster` /
  `croilar-marimo` is the canonical fix; existing deployments
  that set `LANCEDB_URI=./lancedb_data_cv` explicitly in `.env`
  continue to work.
- The new `ducklake_meaisinfhoghlaim` DB is additive; existing
  Dagster runs in `meaisinfhoghlaim` will simply start writing
  to it on the next materialization.

## Non-Goals

- No changes to the Lance namespace FastAPI sidecar
  (`lance-sidecar/main.py`); it already exposes
  `http://lakehouse-lance-namespace:8182` correctly.
- No changes to Garage (`garage.toml`); the 3 vhost buckets
  (`iceberg`, `lance`, `ducklake`) are sufficient for the new
  services.
- No changes to the Lance trojan-horse pattern
  (`table_type=lance` in Lakekeeper); Olake writes Iceberg,
  not Lance, so the pattern is preserved.
- No changes to Lakekeeper's REST contract.
- No changes to the Locket sidecar (`sidecar.yaml`); the
  existing pattern with 5 URIs extends naturally to 11.
- No changes to Pangolin host tags or middlewares; the 3 new
  resources use the standard `tinyauth` + `secure-headers` chain.
- No new dependencies on `lakehouse-oci/` (prod-only) or
  `lakefs/` (deprecated by Iceberg snapshot isolation).

## Risk Assessment

- **Risk: Olake JDBC env vars use a non-standard schema.** Olake's
  source connector reads `JDBC_URL`, `JDBC_USERNAME`,
  `JDBC_PASSWORD` from env (not the `SPRING_DATASOURCE_*` set used
  by Nimtable). Mitigation: the compose.yaml declares both sets
  of env vars correctly per service; the Locket URI list is
  partitioned by service so there is no cross-contamination.
- **Risk: 3 new containers on bunchloch exhaust the 48GB unified
  memory budget.** Mitigation: per-service `deploy.resources.limits`
  cap each new container at 512MB RAM (nimtable, olake) and 256MB
  (lancedb-viewer) = 1.25GB total; bunchloch has 48GB and
  currently uses < 20GB.
- **Risk: Nimtable 0.1.6 is a pre-1.0 release.** Mitigation: the
  pin follows the GOLD_STANDARD policy; if the release breaks,
  the build fails at `docker compose pull` time and the change
  is reverted.
- **Risk: Olake 0.1.5 may not exist as a published tag.**
  Mitigation: Phase 9 validation runs `docker compose pull` and
  fails fast if the tag is invalid; the README documents how to
  bump the pin.
- **Risk: cross-sruth LANCEDB_URI change breaks existing
  croilar-dagster deployments that rely on the local file
  default.** Mitigation: the env var is still respected; only
  the *default* changes. Existing `.env` files that set
  `LANCEDB_URI=./lancedb_data_cv` continue to work.

## Validation

1. `openspec validate extend-lakehouse-with-nimtable-olake-lancedb --strict` passes
2. `bun run validate-stacks` passes (stack-doctor for all 3 new services)
3. `docker compose -f infrastructure/stacks/lakehouse/compose.yaml config` parses
4. `docker compose -f infrastructure/stacks/lakehouse/compose.yaml pull` succeeds for all 3 new images
5. `mise run lint:skills` passes (no skill metadata touched, but re-runs to verify)
6. `bash infrastructure/audit/scripts/inventory-bunchloch.sh` shows 3 new containers
7. `docker compose up -d` brings up nimtable at `:3018`, olake (admin via exec), lancedb-viewer at `:8081`
8. `curl http://localhost:8181/v1/config` returns Lakekeeper catalog config
9. `curl http://localhost:3018/` returns Nimtable HTML
10. `curl http://localhost:8081/` returns LanceDB Viewer HTML
11. `openspec archive extend-lakehouse-with-nimtable-olake-lancedb --yes` after merge
