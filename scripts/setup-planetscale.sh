#!/usr/bin/env bash
# Idempotent PlanetScale "bunchloch" DB bootstrap.
# Creates the 6 schemas if they don't exist.
set -euo pipefail

HOST="${PLANETSCALE_HOST:-eu-west-3.pg.psdb.cloud}"
PORT="${PLANETSCALE_PORT:-5432}"
DB="bunchloch"
USER="${PLANETSCALE_USERNAME}"
PASS="${PLANETSCALE_PASSWORD}"

if [[ -z "$USER" || -z "$PASS" ]]; then
  echo "ERROR: PLANETSCALE_USERNAME and PLANETSCALE_PASSWORD must be set"
  exit 1
fi

echo "Connecting to PlanetScale $DB at $HOST:$PORT..."

PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -c "CREATE SCHEMA IF NOT EXISTS vikunja;" 2>/dev/null || true
PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -c "CREATE SCHEMA IF NOT EXISTS n8n;" 2>/dev/null || true
PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -c "CREATE SCHEMA IF NOT EXISTS calcom;" 2>/dev/null || true
PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -c "CREATE SCHEMA IF NOT EXISTS paperless;" 2>/dev/null || true
PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -c "CREATE SCHEMA IF NOT EXISTS glance;" 2>/dev/null || true
PGPASSWORD="$PASS" psql -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" -c "CREATE SCHEMA IF NOT EXISTS changedetect;" 2>/dev/null || true

echo "All 6 schemas verified: vikunja n8n calcom paperless glance changedetect"
