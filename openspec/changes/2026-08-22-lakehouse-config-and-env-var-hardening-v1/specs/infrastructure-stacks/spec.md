# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Postgres image MUST include pgvector + postgresql-contrib extensions

The lakehouse stack at `bonneagar/stacks/lakehouse/compose.yaml` SHALL use the `pgvector/pgvector:pg17` Docker image (NOT `postgres:16-alpine` or `postgres:16`) for the `postgres` service. The `pgvector/pgvector:pg17` image includes:
- `pgvector` extension (required by Cognee for vector storage)
- `postgresql-contrib` package (provides `uuid-ossp`, `pgcrypto`, `pg_trgm`, `btree_gin`, `btree_gist`)

The `init-db.sql` SHALL install the 6 required extensions via `CREATE EXTENSION IF NOT EXISTS` statements that run BEFORE any `CREATE TABLE` or data load:
- `uuid-ossp` (required by Lakekeeper migrations)
- `pgcrypto` (required by Lakekeeper migrations)
- `pg_trgm` (required by Lakekeeper migrations)
- `btree_gin` (required by Lakekeeper migrations)
- `btree_gist` (required by Lakekeeper migrations)
- `vector` (required by Cognee pgvector backend)

The extensions SHALL be installed automatically by the postgres container on first boot (no manual operator action required).

#### Scenario: Lakekeeper bootstraps successfully on first boot

- **GIVEN** a fresh `docker compose -f compose.yaml -f sidecar.yaml up -d` (no existing volume)
- **WHEN** the postgres container's `init-db.sql` runs
- **THEN** the 6 extensions are created BEFORE the migrations
- **AND** the Lakekeeper migrate container (`lakekeeper-migrate`) successfully runs migrations without `extension "uuid-ossp" is not installed` errors
- **AND** `docker exec lakekeeper-postgres psql -U lakekeeper -d lakekeeper -c "\dx"` shows all 6 extensions

#### Scenario: Cognee connects to pgvector

- **WHEN** the cognee service starts (after lance-namespace + postgres are healthy)
- **THEN** `DB_PROVIDER: postgres` + `VECTOR_DB_PROVIDER: pgvector` resolve correctly
- **AND** `curl -sf http://localhost:8000/health` returns `{"status":"ready"}` within 60s

### Requirement: Olake CDC source DB MUST exist in shared lakehouse-postgres

The lakehouse stack SHALL provide an `olake_source` database on the shared `lakehouse-postgres` container so Olake CDC jobs can connect to a real source DB (NOT the placeholder `staging_pg`).

The `init-db.sql` SHALL create `olake_source` + grant permissions to the `lakekeeper` superuser. The Olake `SOURCE_DB_NAME` env var SHALL default to `olake_source` (NOT `staging_pg`).

#### Scenario: Operator runs Olake CDC job against the source DB

- **GIVEN** the lakehouse stack is up
- **WHEN** the operator runs `mise run olake:cdc --source=postgres` (or `docker exec lakehouse-olake olake ...`)
- **THEN** the Olake CLI connects to `postgres:5432/olake_source` (the default)
- **AND** the connection succeeds with `OLAKE_JDBC_PASSWORD` (shared `POSTGRES_PASSWORD` via Locket)
- **AND** the CDC job persists checkpoint state to the `olake_state` database (separate from `olake_source`)

#### Scenario: Olake source DB survives container restarts

- **WHEN** the lakehouse stack restarts (`docker compose restart`)
- **THEN** the `olake_source` database persists in the named volume `lakehouse-postgres`
- **AND** no data loss occurs

### Requirement: lakehouse sidecar MUST use a portable infisical_secret path

The lakehouse stack's `sidecar.yaml` SHALL NOT hardcode the developer-laptop path `/Users/cianmacandeisigh/dev/kings_college_galway/...` for the `infisical_secret` file mount. Instead, the path SHALL be parameterized via the `INFISICAL_SECRET_FILE` env var (default: `./infisical_secret`).

This makes the lakehouse stack deployable on:
- CI runners (any workspace path)
- Production Komodo deploys (no `/Users/...` paths exist)
- Other developer laptops (any local clone path)

#### Scenario: CI builds the lakehouse stack

- **GIVEN** the CI runner has `INFISICAL_SECRET_FILE=/tmp/ci-infisical-secret` set
- **WHEN** `docker compose -f compose.yaml -f sidecar.yaml config --quiet` runs in CI
- **THEN** the sidecar's `infisical_secret` mount resolves to `/tmp/ci-infisical-secret`
- **AND** the Locket sidecar starts without "file not found" errors

#### Scenario: Operator uses default relative path

- **GIVEN** no `INFISICAL_SECRET_FILE` env var is set
- **WHEN** the operator runs `docker compose -f compose.yaml -f sidecar.yaml up -d` from `bonneagar/stacks/lakehouse/`
- **THEN** the sidecar mounts `./infisical_secret` (the conventional local path)
- **AND** Locket resolves secrets as before

## MODIFIED Requirements

### Requirement: Storage Stacks (Lakehouse) — plaintext secret policy

The system SHALL NOT commit plaintext secrets (POSTGRES_PASSWORD, GARAGE_ACCESS_KEY_ID, CLICKHOUSE_PASSWORD, REDIS_PASSWORD, NIMTABLE_JDBC_PASSWORD, OLAKE_JDBC_PASSWORD, OLAKE_SOURCE_PG_PASSWORD, OLAKE_WRITER_S3_SECRET_KEY, LAKEKEEPER_ENCRYPTION_KEY, LANCEDB_VIEWER_ADMIN_TOKEN, etc.) to the git repository.

The lakehouse stack's `.env.dev` file SHALL be an **empty-value template** with the same keys + inline comments showing where each value comes from. Plaintext secret values SHALL live in `.env.local` (gitignored per `.gitignore:177`).

A CI workflow (`.github/workflows/lakehouse-secret-scan.yml`) SHALL run `gitleaks` against the lakehouse stack + critical `.py` files on every PR + push to main. On detection, the workflow SHALL fail. The allowlist SHALL include `.env.local`, `.env.example`, `.env.local.example`, and `.env.dev` (the empty-value template).

#### Scenario: New PR adds a plaintext secret to a tracked file

- **GIVEN** the developer adds `POSTGRES_PASSWORD=abc123def456` to `dlt_sources/common/destinations_cianfhoghlaim.py`
- **WHEN** the PR is opened
- **THEN** the `lakehouse-secret-scan` CI workflow fails
- **AND** the developer MUST either remove the plaintext (use `${POSTGRES_PASSWORD}` env var instead) OR move it to `.env.local` + add `infisical://dev-baile/...` ref + update the `.env.example`

#### Scenario: Operator populates `.env.local` for local dev

- **GIVEN** the operator has access to the `dev-baile` Infisical vault
- **WHEN** they run `mise run secrets:init` (or `cp .env.dev .env.local && infisical export > .env.local`)
- **THEN** `.env.local` contains the real plaintext secrets for local development
- **AND** `.env.local` is in `.gitignore` so it never gets committed
- **AND** CI secret-scan ignores `.env.local` (allowlisted)

## REMOVED Requirements

(None — no requirement removed in this change. Future PRs may deprecate the 5 standalone graph DB stacks.)