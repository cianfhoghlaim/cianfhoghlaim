# planetscale-postgres-data-strategy Specification

## Purpose
The PlanetScale Postgres data strategy surface covers the 9-step strategy for migrating from the current lakehouse (DuckLake + MotherDuck) to a PlanetScale Postgres backend. It defines 9 invariants: the migration phases (1: shadow writes, 2: dual-read, 3: cutover, 4: cleanup), the data integrity checks (per phase), the rollback strategy (per phase), the cost projections, the schema mapping (DuckDB types → PlanetScale types), the connection pool config, the per-jurisdiction sub-shard layout, the observability layer (planetexplorer + PlanetScale API), and the deprecation timeline for DuckLake.

## Requirements
### Requirement: Data substrate decision tree (R1)

The system SHALL pick a data substrate for each stack via the following
algorithm:

```
pick_data_substrate(stack):
    if stack.requires_extension_not_in_planetscale_pg_matrix:
        return "local-postgres"
    if stack.is_serverless_read_mostly:
        return "cloudflare-d1-sqlite"
    return "planetscale-postgres"   # default
```

The PlanetScale PostgreSQL extension matrix is enumerated in R6 and
mirrored in the ADR.

#### Scenario: New stack is added

- **GIVEN** a developer adds a new stack to `bonneagar/stacks/<stack>/`
- **WHEN** they wire the DB connection
- **THEN** they apply the decision tree
- **AND** they document the substrate choice in the per-stack Markdown
  file (per R7)

### Requirement: PlanetScale PostgreSQL as primary substrate (R2)

The system SHALL use PlanetScale PostgreSQL as the **primary**
managed remote DB substrate for the platform.

PlanetScale PostgreSQL SHALL satisfy all of:

- TLS-encrypted connections (`?sslmode=verify-full`)
- Per-branch database isolation
- PITR (point-in-time recovery) backups
- PgBouncer pooling for serverless apps (port 6543)
- Direct connections for long-running apps (port 5432)

#### Scenario: A migration-target stack connects

- **GIVEN** the operator has approved the Phase B change for `<stack>`
- **WHEN** the `<stack>` compose.yaml is updated
- **THEN** the connection URL uses `?sslmode=verify-full`
- **AND** the credentials are injected via Locket from Infisical path
  `dev-baile/<stack>/database_url`

### Requirement: Cloudflare D1 SQLite as secondary substrate (R3)

The system SHALL use **Cloudflare D1 SQLite** as the secondary
substrate for:

- Per-subject Convex deployments (small footprint, serverless)
- Mobile-sync backends
- Other read-mostly serverless use-cases

#### Scenario: A Convex deployment provisions its DB

- **GIVEN** a new `conic-<subject>` Convex deployment is provisioned
- **WHEN** the connection URL is configured
- **THEN** the DB is a Cloudflare D1 SQLite (per-request billing,
  edge-replicated)

### Requirement: Local Postgres as tertiary substrate (R4)

The system SHALL use a local Postgres container as the tertiary
substrate **only when** the stack requires an extension NOT in the
PlanetScale PG matrix (R6).

Examples of stacks requiring local Postgres:

- **Komodo** (FerretDB v2 + `documentdb` extension — explicitly
  out-of-scope here per the Komodo deferral, see R8)

#### Scenario: A stack needs a missing extension

- **GIVEN** stack `<stack>` needs `<extension>`
- **WHEN** the operator verifies that `<extension>` is NOT in R6
- **THEN** the stack SHALL use a local Postgres container
- **AND** the stack SHALL be added to the local-Postgres exception list
  in R7

### Requirement: PlanetScale MySQL sunset (R5)

The system SHALL **sunset** the existing PlanetScale MySQL usage
during Phase C. Specifically:

- The 6 Bytebase-managed schemas (`vikunja`, `n8n`, `calcom`/`cal-diy`,
  `paperless`, `glance`, `changedetection`) SHALL migrate to
  PlanetScale PostgreSQL.
- The DuckLake tables (currently on PlanetScale MySQL) SHALL migrate
  to PlanetScale PostgreSQL.

After Phase C completes, the platform SHALL **not** use PlanetScale
MySQL for any new substrate decisions.

#### Scenario: Phase C archives

- **GIVEN** the Phase C change has archived
- **WHEN** the bytebase-config.yaml is checked
- **THEN** the `production` environment SHALL point at PlanetScale PG
- **AND** the MySQL connection SHALL be absent from the config

### Requirement: Connection conventions (R6)

The system SHALL follow the PlanetScale PG connection conventions:

| Convention | Value | Rationale |
|---|---|---|
| TLS | `?sslmode=verify-full` | PlanetScale enforces TLS |
| Serverless pooling | port `6543` (PgBouncer) | Convex, D1-write, short-lived workers |
| Long-running | port `5432` (direct) | Lakekeeper, Dagster, cognee |
| Connection URL format | `postgresql://<user>:<password>@<host>.pg.psdb.cloud/<db>?sslmode=verify-full` | the canonical PlanetScale PG URL |
| Credentials source | Locket from Infisical path `dev-baile/<stack>/database_url` | the canonical secret pattern |
| Extension verification | operator confirms extension in PlanetScale's [published docs](https://planetscale.com/docs/postgres/extensions) BEFORE adding the stack to R7 | the extension matrix changes |
| PlanetScale PG supported extension matrix (verified 2026-07-19) | `pgvector`, `pg_cron`, `pg_partman`, `postgis`, `pg_duckdb`, TimescaleDB, `pg_trgm`, `cube`, `earthdistance`, `hstore`, `ltree`, `pg_strict`, `pginsights`, + most other native | see https://planetscale.com/docs/postgres/extensions |
| PlanetScale PG NOT supported | `documentdb` (the FerretDB v2 hard requirement — see R8) | confirmed absent from published docs |

#### Scenario: An operator adds a new stack to the R7 matrix

- **GIVEN** a developer adds `<new-stack>` to R7
- **WHEN** they mark PlanetScale PG as the substrate
- **THEN** they first verify `<new-stack>` requires no extensions
  outside the supported matrix
- **AND** they add the env var to the per-row entry

### Requirement: Per-stack decision matrix (R7)

The system SHALL document a per-stack decision matrix. Each row SHALL contain:

- The stack name
- The current DB substrate
- The target substrate (per R1)
- The compatibility verdict (✅ / ⚠ / ❌)
- The env var name to swap in Phase B
- Whether the swap is trivial or requires migration

The canonical matrix contains 28 rows (see the umbrella spec at
`openspec/specs/planetscale-postgres-data-strategy/spec.md` for the full table).

#### Scenario: A consumer reads R7

- **GIVEN** a developer opens `openspec/specs/planetscale-postgres-data-strategy/spec.md`
- **WHEN** they search for their stack
- **THEN** they see the current substrate + the target + the env var name
- **AND** they see whether Phase B or Phase C is the migration lane

### Requirement: Out of scope — Komodo deferral (R8)

The system SHALL defer **Komodo** (and its FerretDB v2 stack) to a
separate, future openspec change.

Per the explicit operator choice:

> *"Defer all Komodo work entirely"*

The rationale (per ADR `0005-planetscale-postgres-centralisation.md` § Consequences):

- FerretDB v2 requires the Postgres `documentdb` extension
- PlanetScale PostgreSQL **does NOT** support `documentdb`
- Until a Plan B is chosen (drop Komodo + use native MongoDB; OR ship a
  separate "Komodo Postgres" container with `documentdb`), Komodo
  retains its local FerretDB + `ghcr.io/ferretdb/postgres-documentdb:17` setup

The Komodo-deferred status SHALL be referenced from
`openspec/specs/bonneagar-komodo-gitops/spec.md` (via a MODIFIED delta
in this change).

#### Scenario: An agent searches for Komodo

- **GIVEN** the agent reads R8 of this spec
- **WHEN** they look for the Komodo substrate row
- **THEN** they see "deferred to a separate future change" with a link
  to `bonneagar-komodo-gitops/spec.md` (MODIFIED delta)

### Requirement: Per-stack hard-switch procedure (R9)

The system SHALL define a canonical per-stack hard-switch procedure for migrating a stack from a local Postgres container to PlanetScale PostgreSQL. The procedure applies to ⭐-easy stacks (rows 5–28 of R7) and consists of:

1. **Pre-check** — confirm the PlanetScale branch has the required database (via the operator or `verify_planetscale_databases.ts`)
2. **Infisical secret registration** — store the connection URL in `dev-baile/<stack>/database_url`
3. **env var swap** — change `DATABASE_URL` (or equivalent) from `postgres://...@<service-name>:5432/<db>` to `infisical://dev-baile/<stack>/database_url`
4. **Local container disposition** — either REMOVE (full hard switch) or KEEP (env-swap-only fallback), per the per-stack decision in the change proposal
5. **Locket reload** — restart the sidecar so the new secret is fetched
6. **Migration bootstrap** — for stacks that have an explicit `migrate` companion (e.g. Lakekeeper's `lakekeeper-migrate`), the companion container is REMOVED and migrations become idempotent on first start
7. **Verification** — `bun run iac:health --stack <stack>` returns green + the RAGAS gate (if applicable) passes

The procedure is per-stack, atomic, and reverts via `git revert` + PlanetScale PITR.

#### Scenario: Lakekeeper hard switches to PlanetScale PG

- **GIVEN** the operator has created `lakekeeper` on the PlanetScale branch
- **WHEN** Phase B.0 ships
- **THEN** `bonneagar/stacks/lakehouse/compose.yaml` SHALL remove the local `postgres` + `lakekeeper-migrate` services from the `lakekeeper` service block (Lakekeeper now lives inside the centralised `lakehouse` stack, not a standalone stack)
- **AND** the `lakekeeper` service env SHALL use `infisical://dev-baile/lakekeeper/database_url`
- **AND** migrations SHALL run idempotently on first start
- **AND** `bun run iac:health --stack lakekeeper` SHALL return green

#### Scenario: Dagster env-swaps only (local postgres retained)

- **GIVEN** the operator has created `dagster_state` on the PlanetScale branch
- **WHEN** Phase B.0 ships
- **THEN** `bonneagar/stacks/dagster/Dockerfile.dagster` SHALL add `DUCKLAKE_POSTGRES_HOST` pointing at `infisical://dev-baile/dagster/database_url`
- **AND** the local `dagster-postgres` container SHALL remain in compose.yaml (retired in Phase B.1)
- **AND** `bun run iac:health --stack dagster` SHALL return green

#### Scenario: Convex hard switches with no data export (clean start)

- **GIVEN** the operator has created `convex_production` on the PlanetScale branch
- **AND** the self-hosted Convex deployment has no production data (per the operator's confirmation)
- **WHEN** Phase B.0 ships
- **THEN** `bonneagar/stacks/convex/compose.yaml` SHALL remove the `convex-data` SQLite volume
- **AND** the `backend` service env SHALL use `infisical://dev-baile/convex/database_url`
- **AND** Convex SHALL auto-initialise the schema on first connect (its `init` step)

