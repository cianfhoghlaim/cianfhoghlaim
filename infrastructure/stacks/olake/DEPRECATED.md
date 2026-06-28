# DEPRECATED — `infrastructure/stacks/olake/`

The standalone `olake/` Docker Compose stack has been superseded by the
**Olake CDC engine** service inside the canonical dev lakehouse stack.

## Migration

| Old location | New location |
|:--|:--|
| `infrastructure/stacks/olake/compose.yaml` | `infrastructure/stacks/lakehouse/compose.yaml` (service `olake`) |
| `infrastructure/stacks/olake/sidecar.yaml` | `infrastructure/stacks/lakehouse/sidecar.yaml` (shared) |
| `infrastructure/stacks/olake/secrets.env` | `infrastructure/stacks/lakehouse/secrets.env` (3 new URI refs) |
| `infrastructure/stacks/olake/blueprint.yaml` | `infrastructure/stacks/lakehouse/blueprint.yaml` (resource `olake`) |
| *(none — Olake config was never wired up)* | `infrastructure/stacks/lakehouse/olake/{config,catalog,writer}.json` |

## Why deprecated

1. **Reuse `lakehouse-postgres`** — the standalone `olake/` mounted its own
   `olake-postgres` container, duplicating `lakehouse-postgres`. The new
   service uses the shared Postgres with a dedicated `olake_state` database
   (created in `infrastructure/stacks/lakehouse/init-db.sql`).
2. **Canonical Locket sidecar** — the standalone `olake/` had its own
   `sidecar.yaml` with a non-standard secret surface; the lakehouse sidecar
   is the single Infisical injection point for the whole lakehouse.
3. **Cross-sruth wiring** — placing Olake inside `lakehouse/` lets every
   active srutha use Olake-ingested Iceberg tables without bespoke config.

## Why not deleted

The `compose.yaml` is kept on disk so any automated test that imports from
`infrastructure/stacks/olake/compose.yaml` (or relies on the path existing)
does not break. **Do not start the standalone stack** — running both copies
will produce duplicate S3 writes to the same Iceberg tables. After one
release cycle, this directory may be deleted in a follow-up change.

## Tracking

- Openspec change: `extend-lakehouse-with-nimtable-olake-lancedb`
- Spec: `openspec/changes/extend-lakehouse-with-nimtable-olake-lancedb/proposal.md`
