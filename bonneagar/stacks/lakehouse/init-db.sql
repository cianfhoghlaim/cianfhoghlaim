-- =============================================================================
-- LAKEHOUSE DATABASE INITIALIZATION
-- =============================================================================
-- Creates databases for the centralised data plane (after the
-- `centralise-data-plane` 7-stack rewrite, 2026-07 + the
-- `2026-08-15-lakehouse-unified-data-plane-v1` change):
--
--   • 6 DuckLake catalog databases (per project)
--   • dagster_local                         (dagster)
--   • lakekeeper, nimtable, olake_state     (lakehouse-internal metadata)
--   • langfuse                              (consumed by langfuse stack)
--   • mlflow                                (consumed by mlflow stack)
--   • litellm                               (consumed by litellm stack)
--   • cognee_cianfhoghlaim                  (cognee knowledge graph + vectors)
--
-- The langfuse / mlflow / litellm databases are consumed by downstream
-- stacks that previously ran their own per-stack PostgreSQL container.
-- They now share this single lakehouse-postgres container. The existing
-- `lakekeeper` superuser is granted per-service database access — we
-- intentionally use ONE shared user (rather than per-service users) to
-- avoid the Docker-Postgres init-script env-var-substitution gotcha.
--
-- ADDED 2026-08-15: `cognee_cianfhoghlaim` for the cognee knowledge graph
-- builder (the 5 graph DB backends are now part of the unified lakehouse
-- stack). Cognee uses USE_UNIFIED_PROVIDER=pghybrid — postgres serves
-- BOTH the vector store (pgvector) AND the graph store. The dedicated
-- `cognee-postgres` container in the (now-deprecated) cognee/ stack is
-- GONE — replaced by the shared lakehouse-postgres.
--
-- Run automatically by PostgreSQL on first container start.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- DuckLake catalog databases (per project)
-- ---------------------------------------------------------------------------
CREATE DATABASE ducklake_cianfhoghlaim;
CREATE DATABASE ducklake_crypteolas;
CREATE DATABASE ducklake_aleyum;  -- legacy: sruth/aleyum, superseded by croilar
CREATE DATABASE ducklake_croilar;
CREATE DATABASE ducklake_tuath;
CREATE DATABASE ducklake_meaisinfhoghlaim;  -- added in extend-lakehouse-with-nimtable-olake-lancedb

-- ---------------------------------------------------------------------------
-- Dagster metadata (per-subject pipelines)
-- ---------------------------------------------------------------------------
CREATE DATABASE dagster_local;

-- ---------------------------------------------------------------------------
-- Lakehouse-internal metadata
-- ---------------------------------------------------------------------------
CREATE DATABASE olake_state;     -- Olake CDC checkpoints (extend-lakehouse-with-nimtable-olake-lancedb)
CREATE DATABASE nimtable;        -- Nimtable dashboard state (extend-lakehouse-with-nimtable-olake-lancedb)

-- ---------------------------------------------------------------------------
-- Downstream consumer databases (added by centralise-data-plane rewrite)
-- ---------------------------------------------------------------------------
CREATE DATABASE langfuse;        -- langfuse stack metadata (was: standalone postgres)
CREATE DATABASE mlflow;          -- mlflow stack backend store (was: standalone postgres)
CREATE DATABASE litellm;         -- litellm stack model registry (was: standalone postgres)

-- ---------------------------------------------------------------------------
-- Graph DB backend database (added 2026-08-15-lakehouse-unified-data-plane-v1)
-- ---------------------------------------------------------------------------
-- Cognee uses pgvector (built into Postgres 16+) for vector storage AND the
-- Postgres graph extension for graph storage (USE_UNIFIED_PROVIDER=pghybrid).
-- The dedicated cognee-postgres container in the deprecated cognee/ stack
-- is gone — replaced by this shared database on lakehouse-postgres.
CREATE DATABASE cognee_cianfhoghlaim;  -- cognee KG + pgvector (was: dedicated cognee-postgres)

-- ---------------------------------------------------------------------------
-- Olake CDC source DB (added 2026-08-22-lakehouse-config-and-env-var-hardening-v1)
-- ---------------------------------------------------------------------------
-- Olake CDC jobs connect to this DB to capture changes for the
-- olake → iceberk → lance pipeline. Was the placeholder `staging_pg`
-- (never existed in the lakehouse-postgres).
CREATE DATABASE olake_source;  -- olake CDC source DB (was: staging_pg placeholder)

-- ---------------------------------------------------------------------------
-- Required Postgres extensions (added 2026-08-22-lakehouse-config-and-env-var-hardening-v1)
-- ---------------------------------------------------------------------------
-- The pgvector/pgvector:pg17 image includes postgresql-contrib + pgvector.
-- These 6 extensions MUST be created BEFORE Lakekeeper migrations run.
-- uuid-ossp, pgcrypto, pg_trgm, bbtree_gin, btree_gist — required by Lakekeeper.
-- vector — required by Cognee pgvector backend.
-- IF NOT EXISTS makes the script idempotent for existing volumes.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ---------------------------------------------------------------------------
-- Grant permissions on every database to the lakekeeper superuser.
-- All 14 databases share the single superuser (POSTGRES_USER in compose.yaml).
-- Per-service passwords are layered on top by the LANGFUSE_DB_PASSWORD /
-- MLFLOW_DB_PASSWORD / LITELLM_DB_PASSWORD / COGNEE_POSTGRES_PASSWORD env
-- vars when each downstream service connects. Using ONE superuser keeps
-- the auth model simple.
-- ---------------------------------------------------------------------------
GRANT ALL PRIVILEGES ON DATABASE ducklake_cianfhoghlaim     TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_crypteolas     TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_aleyum         TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_croilar        TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_tuath          TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_meaisinfhoghlaim TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE dagster_local           TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE olake_state             TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE nimtable                TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE langfuse                TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE mlflow                  TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE litellm                 TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE cognee_cianfhoghlaim    TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE olake_source            TO lakekeeper;
