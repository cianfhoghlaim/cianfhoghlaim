## ADDED Requirements

### Requirement: Local Infisical Vault on bunchloch

The system SHALL deploy a local Infisical vault at
`bonneagar/stacks/infisical/` on the `bunchloch` host, exposing its UI on
host port 8081, with the canonical 5 mandated env vars
(`ENCRYPTION_KEY`, `AUTH_SECRET`, `DB_CONNECTION_URI`, `REDIS_URL`,
`SITE_URL`) plus `HOST=0.0.0.0`. The vault SHALL hold a project named
`dev-baile` with a machine identity granting Locket-sidecar access.

#### Scenario: Fresh cold-boot brings up the vault

- **GIVEN** bunchloch is fresh (zero infisical containers running)
- **AND** the operator has 25 GB free disk + 12 GB RAM headroom
- **AND** the operator has executed `docker network create bunchloch-infra`
- **WHEN** the operator runs
  `cd bonneagar/stacks/infisical && docker compose -f compose.yaml up -d`
- **THEN** 3 containers come up: `infisical-backend` (port 8081),
  `infisical-db` (postgres:16-alpine, internal port 5432),
  `infisical-redis` (redis:7.4-alpine, internal port 6379)
- **AND** the backend's `/api/status` returns HTTP 200

#### Scenario: All images are semver-pinned

- **WHEN** `bun run validate-stacks` runs against `bonneagar/stacks/infisical/`
- **THEN** zero `:latest` tags appear in any compose file in the stack
- **AND** `infisical/infisical:v0.161.12`, `postgres:16-alpine`,
  `redis:7.4-alpine` are the only image tags present

#### Scenario: The external network is bunchloch-scoped

- **WHEN** `docker-compose.yaml` is read
- **THEN** the only `external: true` network declared SHALL be named
  `bunchloch-infra` (NOT `infrastructure`, which is the arm1-oci production
  network)
- **AND** the network SHALL be created by the runbook with
  `docker network create bunchloch-infra` before the first compose up

### Requirement: Bundled Vault Seeding Bootstrap

The system SHALL provide a `bonneagar/scripts/seed-infisical-vault.sh`
script that writes the 7 seed secret paths to the `dev-baile/dev`
environment on first vault bring-up, covering every URI referenced by the
5 consumer stacks' `secrets.env` files.

#### Scenario: Seed script populates the 7 paths

- **GIVEN** the operator is authenticated to the local Infisical via
  `infisical login`
- **AND** the project `dev-baile` exists with a captured `PROJECT_ID`,
  `CLIENT_ID`, `CLIENT_SECRET`
- **WHEN** the operator runs `bun run scripts/seed-infisical-vault.sh`
- **THEN** `infisical secrets list` shows 7 paths populated:
  `infisical/{encryption_key,auth_secret,postgres_password,db_uri,redis_url,site_url,client_secret}`,
  `lakehouse/{postgres_password,rpc_secret,admin_token,access_key_id,secret_access_key,encryption_key,jdbc_password,dashboard_secret,source_pg_password,writer_s3_secret_key,lancedb_viewer_admin_token}`,
  `lakehouse-garage/{access_key_id,secret_access_key}`,
  `lakehouse-clickhouse/{user,password,db}`,
  `lakehouse-redis/{password}`,
  `litellm/{master_key,salt_key,database_url,postgres_user,postgres_password,postgres_db,api_keys}`, and
  `mlflow/{postgres_user,postgres_password,aws_default_region,default_artifact_root,aws_default_region}`