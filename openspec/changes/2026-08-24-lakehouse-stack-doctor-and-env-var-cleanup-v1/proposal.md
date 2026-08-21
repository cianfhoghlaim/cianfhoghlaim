# 2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1

## Why

PR #3 of the **4-PR lakehouse hardening series**. Addresses cross-cutting technical debt that remains after PR #1 (config hardening) + PR #2 (production config + Lance sidecar rewrite).

The lakehouse stack has grown to 17 services + 14 databases + 53+ Infisical URIs + 10 private-resources. The same data (database names, env vars) is duplicated across `init-db.sql`, `compose.yaml`, `destinations_cianfhoghlaim.py` (in `dlt_sources/`), and `.infisical.env` — every drift is a potential outage. This change establishes **single sources of truth** + **custom validation gates**.

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| Lance Namespace sidecar | Full rewrite using official libs (DONE in PR #2) |
| Ship strategy | **This is PR #3 of 4** — ship separately |
| Observability stack | Langfuse + MLflow + Logfire (DONE in PR #2) |
| Deprecated stacks | Keep as read-only shadow stacks |

## Dependencies

`Blocked by: 2026-08-22-lakehouse-config-and-env-var-hardening-v1` (same compose.yaml + init-db.sql files)
`Blocked by: 2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1` (same compose.yaml + init-db.sql files)
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. Single source of truth for DB list (1 NEW file + 1 MODIFIED)
**File**: `bonneagar/stacks/lakehouse/db_manifest.yaml` (NEW)
**File**: `bonneagar/stacks/lakehouse/init-db.sql` (MODIFIED — header comment references db_manifest.yaml)

The new `db_manifest.yaml` lists all 14 databases in one canonical place. `dlt_sources/common/destinations_cianfhoghlaim.py` reads from it via Python's `yaml.safe_load()` (this becomes a future PR — for now, init-db.sql + the Python file both reference db_manifest.yaml in their docstrings).

```yaml
# db_manifest.yaml
databases:
  ducklake:
    - ducklake_cianfhoghlaim
    - ducklake_crypteolas
    - ducklake_aleyum
    - ducklake_croilar
    - ducklake_tuath
    - ducklake_meaisinfhoghlaim
  dagster:
    - dagster_local
  lakehouse_internal:
    - olake_state
    - nimtable
  downstream:
    - langfuse
    - mlflow
    - litellm
  graph_db:
    - cognee_cianfhoghlaim
  olake_source:
    - olake_source
```

### 2. Pydantic Settings class (1 NEW file)
**File**: `bonneagar/stacks/lakehouse/config.py` (NEW)

A `LakehouseSettings(BaseSettings)` class that loads + validates all 53+ env vars in one place:
```python
from pydantic_settings import BaseSettings

class GarageSettings(BaseSettings):
    rpc_secret: str
    admin_token: str
    access_key_id: str
    secret_access_key: str

class LakekeeperSettings(BaseSettings):
    encryption_key: str
    base_uri: str = "http://lakekeeper.cianfhoghlaim.ie"
    ssl_mode: str = "prefer"
    pg_host_r: str = "postgres"
    pg_host_w: str = "postgres"
    metrics_port: int = 9100
    # ... etc

class LakehouseSettings(BaseSettings):
    garage: GarageSettings
    lakekeeper: LakekeeperSettings
    postgres: PostgresSettings
    # ...
```

This is the Python-side counterpart of `compose.yaml`'s env vars. Future operators can `from lakehouse.config import lakehouse_settings` to get typed access to all config.

### 3. Split `.infisical.env` into lakehouse sub-files (6 NEW files + 1 MODIFIED)
**Files**: 
- `.infisical.env` (MODIFIED — keep non-lakehouse sections + add header referencing sub-files)
- `.infisical.env.lakehouse` (NEW — ~62 lines: garage + postgres + clickhouse + redis + lakekeeper + olake + lance + motherduck + planetscale)
- `.infisical.env.cognee` (NEW — ~10 lines: COGNEE_LLM_API_KEY, COGNEE_EMBEDDING_API_KEY, COGNEE_POSTGRES_PASSWORD, GALILEO_API_KEY)
- `.infisical.env.falkordb` (NEW — ~3 lines)
- `.infisical.env.memgraph` (NEW — ~4 lines)
- `.infisical.env.lancedb` (NEW — ~3 lines)
- `.infisical.env.observability` (NEW — ~15 lines: LOGFIRE_TOKEN, LANGFUSE_PUBLIC_KEY/SECRET, MLFLOW_TRACKING_URI, etc.)

The root `.infisical.env` keeps non-lakehouse sections (Komodo, Forgejo, PocketID, etc.) and adds a header comment pointing to the sub-files. **`scripts/init-vault.ts` continues to read the root .infisical.env** (the sub-files are documentation only for now — a future PR will update init-vault.ts to merge sub-files).

### 4. `lakehouse` profile in stack-doctor (1 NEW file + 1 MODIFIED)
**File**: `scripts/lakehouse-stack-doctor.sh` (NEW)
**File**: `mise.toml` (MODIFIED — add `lakehouse:stack-doctor` task)

New script that lints the unified lakehouse stack specifically:
- 17 services in compose.yaml
- 14 databases in init-db.sql
- 10 private-resources in blueprint.yaml
- 5 routes in pangolin.yaml
- 53+ `infisical://dev-baile/<svc>/<key>` URIs in secrets.env
- 100% of image tags pinned to semver (exceptions documented)
- All healthchecks use the canonical template
- No hardcoded absolute paths in sidecar.yaml

### 5. garage-init bash → Python (1 NEW file + 1 MODIFIED)
**File**: `bonneagar/stacks/lakehouse/garage_init.py` (NEW — replaces the bash script inside the compose.yaml entrypoint)
**File**: `bonneagar/stacks/lakehouse/compose.yaml` (MODIFIED — change the garage-init service to mount the Python script)

The 50-line bash script in `garage-init` service (in compose.yaml) is replaced with a Python script using boto3. Easier to test + maintain + integrate with Locket.

### 6. Validate read-only shadow stacks (1 file NEW)
**File**: `scripts/validate-deprecated-stacks.sh` (NEW)

Script that verifies the 5 deprecated stacks (`cognee/`, `graphiti/`, `falkordb/`, `memgraph/`, `lancedb/`) are:
1. Valid Docker Compose (parse + `docker compose config --quiet` succeeds)
2. Have the deprecation banner at the top
3. Have a README that documents the move to lakehouse
4. Are NOT in any Komodo deployment TOML

### 7. Quality gates (4 tasks)
- `openspec validate --strict` PASS
- `docker compose config --quiet` (lakehouse + 5 deprecated) PASS
- `mise run lint:skills` / `lint:drift-docs` / `lint:registry` PASS
- `scripts/lakehouse-stack-doctor.sh` PASS

## Out of scope (deferred to PR #4)

- **Pydantic Settings integration with init-vault.ts** (the config.py is the Python-side; init-vault.ts writes secrets.env on the Compose side)
- **Update dlt_sources/common/destinations_cianfhoghlaim.py** to read db_manifest.yaml (PR #4 or later)
- **Update init-vault.ts** to merge sub-files when populating Infisical (future PR)
- **Delete the 5 deprecated stacks** (per user preference: kept as read-only shadow stacks)

## Cross-references

- Spec delta: `openspec/changes/2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1/specs/infrastructure-stacks/spec.md`
- Tasks: `openspec/changes/2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1/tasks.md`
- Related change: `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/` (PR #1 — prerequisite)
- Related change: `openspec/changes/2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1/` (PR #2 — prerequisite)
- Related archive: `openspec/changes/archive/2026-08-14-2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1/` (the original preflight script)