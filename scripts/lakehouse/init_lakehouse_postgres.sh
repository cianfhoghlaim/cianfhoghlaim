#!/usr/bin/env bash
# scripts/lakehouse/init_lakehouse_postgres.sh
# Runs the canonical init-db.sql against the lakehouse-postgres container.
# Per Plan 5 of the 2026-10 convergence saga.
#
# Usage:
#   ./scripts/lakehouse/init_lakehouse_postgres.sh
#
# Idempotent: uses CREATE ... IF NOT EXISTS for all extensions + databases.

set -euo pipefail

CONTAINER="${LAKEHOUSE_POSTGRES_CONTAINER:-lakehouse-postgres}"
POSTGRES_USER="${POSTGRES_USER:-lakekeeper}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-}"

if docker ps --format "{{.Names}}" | grep -q "^${CONTAINER}$"; then
    echo "  ✓ ${CONTAINER} is already running"
else
    echo "  ✗ ${CONTAINER} is not running. Start it first with:"
    echo "    mise run lakehouse:up"
    exit 1
fi

INIT_SQL="${INIT_SQL:-bonnegar/stacks/lakehouse/init-db.sql}"
if [ ! -f "$INIT_SQL" ]; then
    echo "  ✗ ${INIT_SQL} not found"
    exit 1
fi

echo "  Running init-db.sql against ${CONTAINER}..."
docker exec -i "${CONTAINER}" \
    env PGPASSWORD="${POSTGRES_PASSWORD}" \
    psql -U "${POSTGRES_USER}" -d postgres -f - < "${INIT_SQL}"

echo "  ✓ Lakehouse PostgreSQL initialized"
echo ""
echo "  Verify the 13 databases are present:"
docker exec -i "${CONTAINER}" \
    env PGPASSWORD="${POSTGRES_PASSWORD}" \
    psql -U "${POSTGRES_USER}" -d postgres -c "\l" | grep -E "ducklake_|^Name|---|^---" | head -20
