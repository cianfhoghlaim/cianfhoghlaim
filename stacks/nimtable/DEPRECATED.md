# DEPRECATED — `infrastructure/stacks/nimtable/`

The standalone `nimtable/` Docker Compose stack has been superseded by the
**Nimtable Iceberg Catalog UI** service inside the canonical dev lakehouse
stack.

## Migration

| Old location | New location |
|:--|:--|
| `infrastructure/stacks/nimtable/compose.yaml` | `infrastructure/stacks/lakehouse/compose.yaml` (service `nimtable`) |
| `infrastructure/stacks/nimtable/sidecar.yaml` | `infrastructure/stacks/lakehouse/sidecar.yaml` (shared) |
| `infrastructure/stacks/nimtable/secrets.env` | `infrastructure/stacks/lakehouse/secrets.env` (2 new URI refs) |
| `infrastructure/stacks/nimtable/blueprint.yaml` | `infrastructure/stacks/lakehouse/blueprint.yaml` (resource `nimtable`) |

## Why deprecated

1. **Reuse `lakehouse-postgres`** — the standalone `nimtable/` ran its own
   private `nimtable-postgres` container for user/dashboard state, doubling
   Postgres footprint on `bunchloch`. The new service uses the shared
   Postgres with a dedicated `nimtable` database (created in
   `infrastructure/stacks/lakehouse/init-db.sql`).
2. **Single JDBC config surface** — the standalone stack used the
   non-standard `NIMTABLE_JDBC_URL` env var; the lakehouse service uses the
   canonical Spring Boot `SPRING_DATASOURCE_URL` (matches Nimtable's
   upstream docs).
3. **Pangolin route consolidation** — the standalone stack had its own
   Pangolin entry; the lakehouse blueprint now has a single entry per
   lakehouse service.
4. **Cross-sruth wiring** — Nimtable inside the lakehouse can browse every
   Iceberg table ingested by every srutha + Olake without per-stack
   rewiring.

## Why not deleted

The `compose.yaml` is kept on disk so any automated test that imports from
`infrastructure/stacks/nimtable/compose.yaml` (or relies on the path
existing) does not break. **Do not start the standalone stack** — running
both copies will create two Spring Boot contexts writing to different
Postgres DBs, producing inconsistent dashboard state. After one release
cycle, this directory may be deleted in a follow-up change.

## Tracking

- Openspec change: `extend-lakehouse-with-nimtable-olake-lancedb`
- Spec: `openspec/changes/extend-lakehouse-with-nimtable-olake-lancedb/proposal.md`
