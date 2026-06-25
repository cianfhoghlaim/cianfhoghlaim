# Tasks: extend-lakehouse-with-nimtable-olake-lancedb

## Phase 1 — Extend `lakehouse/init-db.sql` with meaisinfhoghlaim + olake_state + nimtable DBs

- [ ] Read the current `infrastructure/stacks/lakehouse/init-db.sql` to confirm exact line layout
- [ ] Append the `ducklake_meaisinfhoghlaim` `CREATE DATABASE` + `GRANT` block
- [ ] Append the `olake_state` `CREATE DATABASE` + `GRANT` block
- [ ] Append the `nimtable` `CREATE DATABASE` + `GRANT` block
- [ ] Verify all 3 new DBs use `OWNER lakehouse` (matches the existing 5 DBs at lines 9-13)
- [ ] Verify the SQL is idempotent on `docker compose up` (Postgres only runs init scripts on first boot — acceptable)

## Phase 2 — Extend `lakehouse/compose.yaml` with 3 new services + 2 named volumes

- [ ] Read the current `infrastructure/stacks/lakehouse/compose.yaml` end-to-end
- [ ] Add 2 new named volumes to the existing `volumes:` block: `olake_state` (driver: local), `nimtable_data` (driver: local)
- [ ] Append `nimtable` service: image `nimtable/nimtable:0.1.6`, port `3018:3000`, JDBC env vars, depends_on `postgres` (healthy), `lakekeeper`, `locket`, network `lakehouse`, resource limits `cpus: '1'`, `memory: 512M`
- [ ] Append `olake` service: image `ghcr.io/olake-io/olake:0.1.5`, no published port, JDBC env vars, volume mounts for config.json/catalog.json/writer.json, named volume `olake_state`, depends_on `postgres` (healthy), `locket`, network `lakehouse`, resource limits `cpus: '1'`, `memory: 512M`
- [ ] Append `lancedb-viewer` service: image `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3`, port `8081:8080`, env `LANCEDB_URI=rest://lakehouse-lance-namespace:8182`, depends_on `lance-sidecar` (healthy), `locket`, network `lakehouse`, resource limits `cpus: '0.5'`, `memory: 256M`
- [ ] Add healthchecks for all 3 new services
- [ ] Add security hardening to all 3 new services: `user: 65532:65532` (where supported), `read_only: true` (where supported), `cap_drop: [ALL]`, `no-new-privileges: true`, `security_opt: [no-new-privileges:true]`

## Phase 3 — Create `lakehouse/olake/` config directory + 4 files

- [ ] Create directory `infrastructure/stacks/lakehouse/olake/`
- [ ] Write `infrastructure/stacks/lakehouse/olake/config.json` — Olake source connector config (Postgres sample: host, port, database, username, sslmode)
- [ ] Write `infrastructure/stacks/lakehouse/olake/catalog.json` — Iceberg REST catalog pointing at Lakekeeper: `{"type":"rest","uri":"http://lakekeeper:8181","warehouse":"s3://iceberg/","s3.endpoint":"http://garage:3900","s3.access-key-id":"${GARAGE_ACCESS_KEY}","s3.secret-access-key":"${GARAGE_SECRET_KEY}","s3.region":"garage"}`
- [ ] Write `infrastructure/stacks/lakehouse/olake/writer.json` — Iceberg writer: `{"type":"iceberg","partitioner":"{\"type\":\"identity\",\"keys\":[\"id\"]}","flush_interval_ms":5000,"batch_size":10000}`
- [ ] Write `infrastructure/stacks/lakehouse/olake/.env.example` — `OLAKE_SOURCE_TYPE=postgres`, `OLAKE_SOURCE_HOST=postgres`, `OLAKE_SOURCE_PORT=5432`, `OLAKE_SOURCE_DATABASE=staging_pg`, etc.

## Phase 4 — Update `lakehouse/secrets.env` with 6 new Locket URI refs

- [ ] Read the current `infrastructure/stacks/lakehouse/secrets.env` to confirm URI pattern
- [ ] Append `nimtable_jdbc_password=infisical://dev-baile/lakehouse/nimtable/JDBC_PASSWORD`
- [ ] Append `nimtable_dashboard_secret=infisical://dev-baile/lakehouse/nimtable/DASHBOARD_SECRET`
- [ ] Append `olake_jdbc_password=infisical://dev-baile/lakehouse/olake/JDBC_PASSWORD`
- [ ] Append `olake_source_pg_password=infisical://dev-baile/lakehouse/olake/SOURCE_PG_PASSWORD`
- [ ] Append `lancedb_viewer_admin_token=infisical://dev-baile/lakehouse/lancedb-viewer/ADMIN_TOKEN`
- [ ] Append `olake_writer_s3_secret_key=infisical://dev-baile/lakehouse/olake/WRITER_S3_SECRET_KEY`
- [ ] Verify all 6 new URIs use `infisical://dev-baile/lakehouse/...` (not the older `op://` or `sops://` patterns)

## Phase 5 — Update `lakehouse/blueprint.yaml` with 3 new Pangolin private-resources

- [ ] Read the current `infrastructure/stacks/lakehouse/blueprint.yaml` to confirm the 6-label pattern
- [ ] Append `pangolin.private-resources.nimtable`: name `lakehouse-nimtable`, mode `standalone`, full-domain `nimtable.cianfhoghlaim.ie`, destination-port 3018, protocol `http`, roles `["bunchloch"]`
- [ ] Append `pangolin.private-resources.olake`: name `lakehouse-olake`, mode `standalone`, full-domain `olake.cianfhoghlaim.ie`, destination-port 8080, protocol `http`, roles `["bunchloch"]`
- [ ] Append `pangolin.private-resources.lancedb-viewer`: name `lakehouse-lancedb-viewer`, mode `standalone`, full-domain `lance-viewer.cianfhoghlaim.ie`, destination-port 8081, protocol `http`, roles `["bunchloch"]`
- [ ] Attach middlewares `["tinyauth", "secure-headers"]` to all 3 new resources (matches the convention from `.agents/skills/kcg-pangolin-stack/SKILL.md`)

## Phase 6 — Update `lakehouse/README.md` with service inventory + architecture diagram + Cross-Sruth Wiring

- [ ] Read the current `infrastructure/stacks/lakehouse/README.md` to confirm structure
- [ ] Add the 3 new services to the Service Inventory table (Port | Service | Image | Notes)
- [ ] Update the ASCII Architecture diagram to include `nimtable` (`:3018`), `olake` (ephemeral), `lancedb-viewer` (`:8081`)
- [ ] Add a "Cross-Sruth Wiring" section documenting:
  - The `LANCEDB_URI=rest://lakehouse-lance-namespace:8182` contract for every active srutha
  - The per-sruth `ducklake_{namespace}` DB contract (the 6 active DBs)
  - The canonical factory: `oideachais/dlt_utils/destinations.py:with_namespace()` (line 289)
  - A 4-row table mapping each srutha → DB name + LANCEDB_URI value
- [ ] Add a "Bringup" subsection showing the `docker compose up` order and the 4 URLs to verify

## Phase 7 — Fix `croilar-dagster/compose.yaml` + `croilar-marimo/compose.yaml` LANCEDB_URI + networks

- [ ] Read `infrastructure/stacks/croilar-dagster/compose.yaml` end-to-end
- [ ] Change `LANCEDB_URI=${LANCEDB_URI:-./lancedb_data_cv}` (line ~12) to `LANCEDB_URI=${LANCEDB_URI:-rest://lakehouse-lance-namespace:8182}`
- [ ] Add `lakehouse: external: true` to the `networks:` block in `croilar-dagster/compose.yaml` (if not present)
- [ ] Read `infrastructure/stacks/croilar-marimo/compose.yaml` end-to-end
- [ ] Change `LANCEDB_URI=${LANCEDB_URI:-./lancedb_data_cv}` (line ~11) to `LANCEDB_URI=${LANCEDB_URI:-rest://lakehouse-lance-namespace:8182}`
- [ ] Add `lakehouse: external: true` to the `networks:` block in `croilar-marimo/compose.yaml` (if not present)

## Phase 8 — Create DEPRECATED.md in `olake/` + `nimtable/` (redirect to lakehouse/)

- [ ] Write `infrastructure/stacks/olake/DEPRECATED.md` — 8-12 lines explaining that the standalone `olake/` stack is now superseded by `infrastructure/stacks/lakehouse/olake/` (the config dir inside the canonical lakehouse stack); cite the openspec change ID `extend-lakehouse-with-nimtable-olake-lancedb`; instruct contributors to delete the standalone `compose.yaml` after they confirm no automated test imports from it
- [ ] Write `infrastructure/stacks/nimtable/DEPRECATED.md` — 8-12 lines explaining that the standalone `nimtable/` stack is now superseded by the `nimtable` service inside `infrastructure/stacks/lakehouse/compose.yaml`; cite the openspec change ID; instruct contributors to delete the standalone `compose.yaml` after they confirm no automated test imports from it
- [ ] Do NOT delete the standalone `compose.yaml` files (per `openspec/AGENTS.md` "Backward compatibility" guidance); let humans delete them after one release cycle

## Phase 9 — Run `bun run validate-stacks` + `docker compose config`

- [ ] Run `bun run validate-stacks` and verify zero errors
- [ ] Run `docker compose -f infrastructure/stacks/lakehouse/compose.yaml config` and verify it parses
- [ ] Run `docker compose -f infrastructure/stacks/lakehouse/compose.yaml -f infrastructure/stacks/lakehouse/sidecar.yaml config` and verify it parses
- [ ] Run `docker compose -f infrastructure/stacks/croilar-dagster/compose.yaml config` and verify it parses
- [ ] Run `docker compose -f infrastructure/stacks/croilar-marimo/compose.yaml config` and verify it parses

## Phase 10 — Run quality gates + live audit

- [ ] Run `mise run lint:skills` and verify 108/108 skills pass
- [ ] Run `bash infrastructure/audit/scripts/inventory-bunchloch.sh` and verify the 3 new containers appear in the JSON snapshot (will require `docker compose up -d` first)
- [ ] Run `mise run turbo typecheck` and verify zero errors
- [ ] Run `mise run lint` and verify zero errors
- [ ] (Optional) `mise run py:typecheck` and verify zero errors

## Phase 11 — Commit + rebase + push + `openspec archive`

- [ ] `git status` to inspect the 12 modified/new files
- [ ] `git add infrastructure/stacks/lakehouse/ openspec/changes/extend-lakehouse-with-nimtable-olake-lancedb/ infrastructure/stacks/croilar-dagster/ infrastructure/stacks/croilar-marimo/ infrastructure/stacks/olake/DEPRECATED.md infrastructure/stacks/nimtable/DEPRECATED.md`
- [ ] `git commit -m "feat(lakehouse): wire nimtable + olake + lancedb-viewer into dev lakehouse

- Add 3 services to lakehouse/compose.yaml (nimtable :3018, olake ephemeral, lancedb-viewer :8081)
- Add ducklake_meaisinfhoghlaim + olake_state + nimtable DBs to init-db.sql
- Fix croilar-dagster + croilar-marimo LANCEDB_URI default to rest://lakehouse-lance-namespace:8182
- Add 6 Locket URI refs to lakehouse/secrets.env
- Add 3 Pangolin private-resources to lakehouse/blueprint.yaml
- Mark standalone olake/ + nimtable/ as deprecated
- Closes openspec change extend-lakehouse-with-nimtable-olake-lancedb"`
- [ ] `git pull --rebase`
- [ ] `git push`
- [ ] `openspec archive extend-lakehouse-with-nimtable-olake-lancedb --yes`
- [ ] `git status` to confirm "up to date with origin"
