-- =============================================================================
-- LAKEHOUSE DATABASE INITIALIZATION
-- =============================================================================
-- Creates additional databases for DuckLake catalogs per project
-- Run automatically by PostgreSQL on first container start
-- =============================================================================

-- Create DuckLake catalog databases for each project
CREATE DATABASE ducklake_oideachais;
CREATE DATABASE ducklake_crypteolas;
CREATE DATABASE ducklake_aleyum;  -- legacy: sruth/aleyum, superseded by croilar
CREATE DATABASE ducklake_croilar;
CREATE DATABASE ducklake_tuath;
CREATE DATABASE ducklake_meaisinfhoghlaim;  -- added in extend-lakehouse-with-nimtable-olake-lancedb
CREATE DATABASE dagster_local;

-- Create Langfuse database for observability
CREATE DATABASE langfuse;

-- Create Olake CDC engine state database (added in extend-lakehouse-with-nimtable-olake-lancedb)
CREATE DATABASE olake_state;

-- Create Nimtable Iceberg catalog UI metadata database (added in extend-lakehouse-with-nimtable-olake-lancedb)
CREATE DATABASE nimtable;

-- Grant permissions to lakekeeper user
GRANT ALL PRIVILEGES ON DATABASE ducklake_oideachais TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_crypteolas TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_aleyum TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_croilar TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_tuath TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_meaisinfhoghlaim TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE dagster_local TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE langfuse TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE olake_state TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE nimtable TO lakekeeper;
