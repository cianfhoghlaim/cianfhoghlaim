-- init-db.sql — schema bootstrap for croilar-postgres
-- Runs once on first container start (Alpine Postgres docker-entrypoint-initdb.d)

-- BetterAuth schema (managed by Drizzle migrations at deploy time)
-- Tables: user, session, account, verification, etc.
CREATE SCHEMA IF NOT EXISTS better_auth;
GRANT ALL ON SCHEMA better_auth TO croilar;

-- Convex metadata schema (managed by Convex backend at startup)
-- Tables: _convex_*
CREATE SCHEMA IF NOT EXISTS convex;
GRANT ALL ON SCHEMA convex TO croilar;

-- DuckLake catalog schema (managed by dlt_utils/destinations.py)
-- Tables: lakekeeper catalog tables
CREATE SCHEMA IF NOT EXISTS ducklake_catalog;
GRANT ALL ON SCHEMA ducklake_catalog TO croilar;
