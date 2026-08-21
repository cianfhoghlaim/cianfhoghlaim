# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Lance Namespace sidecar MUST use the official `lance-namespace-impls[iceberg]` library

The `lakehouse/lance-sidecar/main.py` SHALL use the official `lance-namespace` + `lance-namespace-urllib3-client` + `lance-namespace-impls[iceberg]` libraries from `lance-format/lance-namespace-impls` to talk to the Lakekeeper Iceberg REST Catalog. The hand-rolled `RestClient` class + 567 LOC of custom Iceberg REST code SHALL be removed.

The `requirements.txt` SHALL include:
- `lance-namespace>=0.11.1`
- `lance-namespace-urllib3-client>=0.11.1`
- `lance-namespace-impls[iceberg]>=0.4.1`
- `pylance>=7.0.0`
- `pyarrow>=15.0.0`

The sidecar SHALL continue to expose the same REST API surface (the `/namespaces`, `/tables` endpoints with the `table_type=lance` property hack) for backward compatibility with the consumers (cognee, graphiti, lancedb-viewer, 47 CocoIndex Apps).

#### Scenario: Lance table registration uses the official iceberg adapter

- **GIVEN** the unified lakehouse stack is up + lakehouse-postgres is healthy
- **WHEN** the operator runs `curl -X POST http://localhost:8182/v1/namespaces/edu.lc/tables -d '{"name": "math_syllabus", ...}'`
- **THEN** the sidecar registers the Lance table in Lakekeeper via the upstream `IcebergNamespace.declare_table()` method
- **AND** the table has `table_type=lance` property in its Iceberg metadata

#### Scenario: Sidecar boots without hand-rolled Iceberg code

- **GIVEN** `lance-namespace-impls[iceberg]>=0.4.1` is installed via `requirements.txt`
- **WHEN** the sidecar container starts
- **THEN** `python -c "from lance_namespace_impls.iceberg import IcebergNamespace; IcebergNamespace(endpoint='http://lakekeeper:8181')"` succeeds
- **AND** the FastAPI app exposes the same REST endpoints as before

### Requirement: Lakekeeper MUST be configured with production-grade env vars

The lakekeeper service in `compose.yaml` SHALL include the following 10+ env vars from the official Lakekeeper configuration docs:

- `LAKEKEEPER__PG_HOST_R` / `LAKEKEEPER__PG_HOST_W` (read replica routing — both default to `postgres`)
- `LAKEKEEPER__METRICS__PORT=9100`
- `LAKEKEEPER__PAGINATION_SIZE_DEFAULT=1024`
- `LAKEKEEPER__PAGINATION_SIZE_MAX=2048`
- `LAKEKEEPER__USE_X_FORWARDED_HEADERS=true` (for Pangolin reverse proxy)
- `LAKEKEEPER__CACHE__STC__ENABLED=true` (short-term credentials cache)
- `LAKEKEEPER__CACHE__WAREHOUSE__ENABLED=true` (warehouse metadata cache)
- `LAKEKEEPER__CACHE__WAREHOUSE__CAPACITY=1000`

The `secrets.env` SHALL add Infisical URI references for the new env vars (operator can override per environment).

Production-only env vars (`LAKEKEEPER__OPENID_PROVIDER_URI`, `LAKEKEEPER__OPENFGA__ENDPOINT`, `LAKEKEEPER__INSTANCE_ADMINS`) SHALL be documented but NOT set by default. Operators opt in by setting them in their Infisical vault.

#### Scenario: Lakekeeper exposes Prometheus metrics

- **WHEN** the lakehouse stack is up
- **THEN** `curl http://localhost:9100/metrics` returns Prometheus metrics (e.g. `lakekeeper_cache_size`, `lakekeeper_cache_hits_total`)
- **AND** the metrics port is documented in `.env.example` + `README.md`

#### Scenario: Pangolin reverse proxy passes through X-Forwarded-* headers

- **WHEN** Lakekeeper receives a request from Pangolin with `X-Forwarded-Host` / `X-Forwarded-Proto` / `X-Forwarded-Port` headers
- **THEN** Lakekeeper uses those headers for the `/config` endpoint URLs (not the `Host` header)
- **AND** the `LAKEKEEPER__BASE_URI` env var is correctly populated from the headers

#### Scenario: Read replica routing (when configured)

- **WHEN** the operator sets `LAKEKEEPER__PG_HOST_R` to a read replica DB host
- **THEN** read-only Lakekeeper endpoints (e.g. `GET /v1/tables`) use the read replica
- **AND** write endpoints (e.g. `POST /v1/tables`) use the write DB (`LAKEKEEPER__PG_HOST_W`)
- **AND** operators MUST be aware of replication lag for read-after-write consistency

### Requirement: Cognee MUST use the new Dataset Database Handlers config pattern

The cognee service SHALL drop the legacy `USE_UNIFIED_PROVIDER=pghybrid` environment variable. Cognee config SHALL use the new Dataset Database Handlers pattern:
- `DB_PROVIDER: postgres`
- `VECTOR_DB_PROVIDER: pgvector`
- `GRAPH_DATABASE_PROVIDER: postgres` (or `kuzu` if a future change adds the AGE extension)
- `LANCEDB_PROVIDER: lancedb` (uses the Lance Namespace adapter for vector storage)

The pghybrid behaviour (`USE_UNIFIED_PROVIDER=pghybrid`) SHALL be removed because Cognee 1.2.x deprecated it in favour of the explicit provider model.

#### Scenario: Cognee boots with the modernized config

- **WHEN** the lakehouse stack is up + lance-namespace is healthy + postgres is healthy
- **THEN** the cognee service starts successfully with `DB_PROVIDER=postgres` + `VECTOR_DB_PROVIDER=pgvector`
- **AND** `curl -sf http://localhost:8000/health` returns `{"status":"ready"}`
- **AND** no `USE_UNIFIED_PROVIDER` warnings appear in the cognee logs

#### Scenario: Cognee uses Lance Namespace as its vector backend

- **WHEN** the operator runs `cognee.cognify(datasets=[...])`
- **THEN** Cognee writes embedding vectors to Lance Namespace at `rest://lakehouse-lance-namespace:8182` (via the new `LANCEDB_PROVIDER=lancedb`)
- **AND** queries can search via the same Lance backend (no postgres pgvector fallback)

### Requirement: FalkorDB MUST use canonical `REDIS_ARGS` + `FALKORDB_ARGS` env vars

The falkordb service SHALL replace its inline `command:` args with the canonical env vars per the official FalkorDB Docker docs:
- `command: ["falkordb"]` (simplified — all args via env vars)
- `REDIS_ARGS: "--requirepass ${FALKORDB_PASSWORD} --appendonly yes --appendfsync everysec --maxmemory 2gb --maxmemory-policy allkeys-lru"`
- `FALKORDB_ARGS: "THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000 TIMEOUT_DEFAULT 30000 QUERY_MEM_CAPACITY 104857600"`
- `BROWSER: "1"`

The `--loadmodule /etc/falkordb/vector.so` flag for vector search capability SHALL also be passed (via `command:` or an additional env var).

#### Scenario: FalkorDB persists data across container restarts

- **GIVEN** the lakehouse stack is up with AOF persistence enabled (`--appendonly yes --appendfsync everysec`)
- **WHEN** the operator runs `docker compose restart falkordb`
- **THEN** FalkorDB recovers the graph from the AOF file at `/data`
- **AND** the Graphiti bi-temporal KG state is preserved

#### Scenario: FalkorDB has production memory limits

- **WHEN** the lakehouse stack is up
- **THEN** FalkorDB's memory usage is capped at 2GB (via `--maxmemory 2gb --maxmemory-policy allkeys-lru`)
- **AND** the cache evicts old keys when the limit is reached
- **AND** the BIEP workload doesn't OOM the host

#### Scenario: Vector.so module loaded for hybrid queries

- **GIVEN** the falkordb service command includes `--loadmodule /etc/falkordb/vector.so`
- **WHEN** Graphiti issues a hybrid query (vector + graph)
- **THEN** the `db.idx.vector.queryNodes` procedure is available
- **AND** the query returns both vector-similar + graph-traversal results

## MODIFIED Requirements

### Requirement: Cognee MUST use a dedicated `cognee` PostgreSQL user (not the shared `lakekeeper` superuser)

The `init-db.sql` SHALL create a dedicated `cognee` user with permissions ONLY on the `cognee_cianfhoghlaim` database (not the other 13 databases). The cognee service SHALL connect with `COGNEE_POSTGRES_USER=cognee` + `COGNEE_POSTGRES_PASSWORD` (resolved via Locket).

The shared `lakekeeper` superuser is reserved for admin tasks (Lakekeeper migrations + DLT destinations). Per-service users (cognee, langfuse, mlflow, litellm) get isolated permissions on their own databases — security best-practice per the Lakekeeper configuration docs.

#### Scenario: Cognee connects with isolated user

- **GIVEN** the lakehouse stack is up + lakehouse-postgres is healthy
- **WHEN** the cognee service starts
- **THEN** it connects to `postgres:5432/cognee_cianfhoghlaim` as user `cognee`
- **AND** it CANNOT read/write to the other 13 databases (ducklake_*, dagster_local, olake_state, nimtable, langfuse, mlflow, litellm, olake_source)

#### Scenario: Operator grants additional permissions to cognee

- **WHEN** the operator runs `docker exec lakehouse-postgres psql -U lakekeeper -c "GRANT pg_read_server_files TO cognee;"`
- **THEN** cognee gains the additional privilege (the `lakekeeper` superuser still has all privileges)
- **AND** other per-service users (langfuse, mlflow, litellm) are NOT affected (least-privilege)

## REMOVED Requirements

(None — no requirement removed in this change. Future PRs may deprecate the 5 standalone graph DB stacks.)