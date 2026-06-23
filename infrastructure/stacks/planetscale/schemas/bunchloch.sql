-- PlanetScale "bunchloch" — single Postgres DB, 6 schemas for the team-workflow stacks.
-- $5/mo Scaler Plan, eu-west-3, 500 MB. Bytebase manages migrations.
-- Each schema is isolated: search_path per connection string.

CREATE SCHEMA IF NOT EXISTS vikunja;
CREATE SCHEMA IF NOT EXISTS n8n;
CREATE SCHEMA IF NOT EXISTS calcom;
CREATE SCHEMA IF NOT EXISTS paperless;
CREATE SCHEMA IF NOT EXISTS glance;
CREATE SCHEMA IF NOT EXISTS changedetect;

-- Bytebase audit tracking table (written by bytebase upon first connection)
CREATE TABLE IF NOT EXISTS public._bytebase_migrations (
    version     INT PRIMARY KEY,
    schema_name TEXT NOT NULL,
    applied_at  TIMESTAMP DEFAULT NOW(),
    checksum    TEXT
);
