-- =============================================================================
-- LAKEHOUSE DATABASE INITIALIZATION
-- =============================================================================
-- Creates additional databases for DuckLake catalogs per project
-- Run automatically by PostgreSQL on first container start
-- =============================================================================

-- Create DuckLake catalog databases for each project
CREATE DATABASE ducklake_oideachais;
CREATE DATABASE ducklake_crypteolas;
CREATE DATABASE ducklake_aleyum;
CREATE DATABASE ducklake_tuath;
CREATE DATABASE dagster_local;

-- Create Langfuse database for observability
CREATE DATABASE langfuse;

-- Grant permissions to lakekeeper user
GRANT ALL PRIVILEGES ON DATABASE ducklake_oideachais TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_crypteolas TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_aleyum TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE ducklake_tuath TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE dagster_local TO lakekeeper;
GRANT ALL PRIVILEGES ON DATABASE langfuse TO lakekeeper;
