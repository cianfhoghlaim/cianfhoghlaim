-- =============================================================================
-- LAKEHOUSE DATABASE INITIALIZATION
-- =============================================================================
-- Creates databases for the centralised data plane (after the
-- `centralise-data-plane` 7-stack rewrite, 2026-07):
--
--   • 6 DuckLake catalog databases (per project)
--   • dagster_local                         (dagster)
--   • lakekeeper, nimtable, olake_state     (lakehouse-internal metadata)
--   • langfuse                              (consumed by langfuse stack)
--   • mlflow                                (consumed by mlflow stack)
--   • litellm                               (consumed by litellm stack)
--
-- The langfuse / mlflow / litellm databases are consumed by downstream
-- stacks that previously ran their own per-stack PostgreSQL container.
-- They now share this single lakehouse-postgres container. The existing
-- `lakekeeper` superuser is granted per-service database access — we
-- intentionally use ONE shared user (rather than per-service users) to
-- avoid the Docker-Postgres init-script env-var-substitution gotcha.
--
-- Run automatically by PostgreSQL on first container start.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- DuckLake catalog databases (per project)
-- ---------------------------------------------------------------------------
CREATE DATABASE ducklake_oideachais;
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
-- Grant permissions on every database to the lakekeeper superuser.
-- All 12 databases share the single superuser (POSTGRES_USER in compose.yaml).
-- Per-service passwords are layered on top by the LANGFUSE_DB_PASSWORD /
-- MLFLOW_DB_PASSWORD / LITELLM_DB_PASSWORD env vars when each downstream
-- stack connects. Using ONE superuser keeps the auth model simple.
-- ---------------------------------------------------------------------------
GRANT ALL PRIVILEGES ON DATABASE ducklake_oideachais     TO lakekeeper;
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
