# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: The lakehouse stack MUST have a single source of truth for the database list

The lakehouse stack SHALL declare its 14 databases in a canonical file at `bonneagar/stacks/lakehouse/db_manifest.yaml`. The `init-db.sql` file SHALL reference this manifest in its header comment (any drift between manifest and init-db.sql MUST be caught by `scripts/lakehouse-stack-doctor.sh`).

The 14 databases are grouped by purpose:
- **ducklake** (6): `ducklake_cianfhoghlaim`, `ducklake_crypteolas`, `ducklake_aleyum`, `ducklake_croilar`, `ducklake_tuath`, `ducklake_meaisinfhoghlaim`
- **dagster** (1): `dagster_local`
- **lakehouse_internal** (2): `olake_state`, `nimtable`
- **downstream** (3): `langfuse`, `mlflow`, `litellm`
- **graph_db** (1): `cognee_cianfhoghlaim`
- **olake_source** (1): `olake_source`

Future changes that add or rename a database MUST update both `db_manifest.yaml` AND `init-db.sql` in the same PR. The `lakehouse-stack-doctor.sh` script SHALL fail any PR that has drift between these two files.

#### Scenario: Operator adds a new database

- **WHEN** the operator adds `CREATE DATABASE my_new_db;` to `init-db.sql`
- **THEN** `db_manifest.yaml` MUST also be updated with the new DB under the appropriate group
- **AND** `scripts/lakehouse-stack-doctor.sh` MUST pass after both updates
- **AND** the PR review SHALL flag any drift between the two files

#### Scenario: dlt destinations read the same source of truth

- **WHEN** a future PR wires `dlt_sources/common/destinations_cianfhoghlaim.py` to read `db_manifest.yaml`
- **THEN** the 14 database names are loaded from the manifest (not hardcoded in Python)
- **AND** the DLT destination factory uses the canonical names

### Requirement: The lakehouse stack MUST expose a typed Pydantic Settings class

The lakehouse stack SHALL provide a `LakehouseSettings(BaseSettings)` class at `bonneagar/stacks/lakehouse/config.py` that loads + validates all 53+ env vars in one place. The class SHALL aggregate sub-settings classes for each service:
- `GarageSettings`
- `LakekeeperSettings`
- `PostgresSettings`
- `CogneeSettings`
- `GraphitiSettings`
- `FalkorDBSettings`
- `MemgraphSettings`
- `LanceNamespaceSettings`
- `ObservabilitySettings` (Langfuse + MLflow + Logfire)

The Python settings class is the **Python-side counterpart** of the `compose.yaml` env vars. Future operators can use it for typed access in scripts + notebooks (e.g., `from lakehouse.config import settings; settings.garage.access_key_id`).

#### Scenario: A marimo notebook reads the lakehouse config

- **WHEN** a marimo notebook imports `from lakehouse.config import settings`
- **THEN** it gets typed access to all 53+ env vars
- **AND** Pydantic validates that required fields are set
- **AND** the notebook fails early if a required secret is missing

#### Scenario: A CI lint catches missing required config

- **WHEN** the operator removes `POSTGRES_PASSWORD` from `.env.local`
- **THEN** `from lakehouse.config import settings` fails with `ValidationError: POSTGRES_PASSWORD field required`
- **AND** any script that imports `lakehouse.config` fails with a clear error message

### Requirement: The `.infisical.env` MUST be split into lakehouse-specific sub-files

The 1194-line `.infisical.env` SHALL be split into lakehouse-specific sub-files for operator clarity. The lakehouse-relevant keys SHALL move to:

- `.infisical.env.lakehouse` (~62 lines): `GARAGE_*`, `POSTGRES_PASSWORD`, `CLICKHOUSE_PASSWORD`, `REDIS_PASSWORD`, `LAKEKEEPER_ENCRYPTION_KEY`, `OLAKE_*`, `LANCEDB_*`, `MOTHERDUCK_*`, `PLANETSCALE_*`, `DUCKLAKE_*`, `R2_*`
- `.infisical.env.cognee` (~10 lines): `COGNEE_LLM_*`, `COGNEE_EMBEDDING_*`, `COGNEE_POSTGRES_PASSWORD`, `GALILEO_API_KEY`
- `.infisical.env.falkordb` (~3 lines): `FALKORDB_PASSWORD`, `VECTOR_MODULE_URL`, `CLUSTER_MODE`
- `.infisical.env.memgraph` (~4 lines): `MEMGRAPH_USER`, `MEMGRAPH_PASSWORD`, `MEMGRAPH_LICENSE_FILE_PATH`, `MEMGRAPH_LOG_LEVEL`
- `.infisical.env.lancedb` (~3 lines): `LANCEDB_API_KEY`, `LANCEDB_NAMESPACE_TOKEN`, `LANCEDB_REGION`
- `.infisical.env.observability` (~15 lines): `LOGFIRE_TOKEN`, `LANGFUSE_*`, `MLFLOW_*`

The root `.infisical.env` SHALL keep the non-lakehouse sections (Komodo, Forgejo, PocketID, Pangolin, Spotify, etc.) and add a header comment pointing to the sub-files.

**`scripts/init-vault.ts` SHALL continue to read the root `.infisical.env`** (the sub-files are documentation only for now — a future PR will update init-vault.ts to merge sub-files).

#### Scenario: Operator finds a lakehouse env var

- **GIVEN** the operator wants to update `LANCEDB_API_KEY`
- **WHEN** they grep the repo for `LANCEDB_API_KEY`
- **THEN** they find it in `.infisical.env.lancedb` (NOT scattered across `.infisical.env`)
- **AND** the root `.infisical.env` header comment points to the sub-files

#### Scenario: Operator finds a non-lakehouse env var

- **GIVEN** the operator wants to update `KOMODO_API_KEY`
- **WHEN** they grep the repo for `KOMODO_API_KEY`
- **THEN** they find it in the root `.infisical.env` (Komodo section, NOT in a sub-file)
- **AND** the comment in the Komodo section says "Komodo-specific — NOT lakehouse"

## MODIFIED Requirements

### Requirement: A `lakehouse:stack-doctor` mise task SHALL lint the unified stack

The `mise run lakehouse:stack-doctor` task SHALL run the new `scripts/lakehouse-stack-doctor.sh` script which validates:

- **17 services** in `compose.yaml` (was 16; +1 otel-collector added in PR #2)
- **14 databases** in `init-db.sql` (matches `db_manifest.yaml`)
- **10 private-resources** in `blueprint.yaml`
- **5 routes** in `pangolin.yaml`
- **53+ `infisical://dev-baile/<svc>/<key>` URIs** in `secrets.env`
- **100% of image tags pinned** to semver (with documented exceptions for `nimtable/nimtable:latest` + `lakehouse-lance-namespace:latest`)
- **No hardcoded absolute paths** in `sidecar.yaml` (must use `${INFISICAL_SECRET_FILE}`)
- **All healthchecks use the canonical template** (10s interval, 5s timeout, 3-5 retries, 10-30s start_period)

The script exits 0 on success, exits 1 on failure with actionable error messages.

#### Scenario: PR adds a new service to lakehouse

- **GIVEN** the operator adds an 18th service to `compose.yaml`
- **WHEN** `mise run lakehouse:stack-doctor` runs
- **THEN** the script reports "Found 18 services in compose.yaml, expected 17 — add the new service to the stack-doctor's expected count"
- **AND** the script exits 1

#### Scenario: PR adds a hardcoded absolute path

- **GIVEN** the operator adds `file: /Users/.../secret` to a lakehouse YAML file
- **WHEN** `mise run lakehouse:stack-doctor` runs
- **THEN** the script reports "Found hardcoded absolute path at line X — replace with `${INFISICAL_SECRET_FILE}`"
- **AND** the script exits 1

## REMOVED Requirements

(None — no requirement removed in this change. The 5 deprecated stacks remain as read-only shadow stacks per user preference.)