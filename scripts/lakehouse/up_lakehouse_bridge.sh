#!/usr/bin/env bash
# scripts/lakehouse/up_lakehouse_bridge.sh
# Brings up the 12 currently-down lakehouse services in dependency order:
# 1. postgres (foundation — already up at lakehouse-postgres:5433)
# 2. garage + garage-init (S3-compatible storage)
# 3. redis (cache + queue)
# 4. lakekeeper-migrate (one-shot migration)
# 5. lakekeeper (Iceberg REST catalog)
# 6. lance-namespace (Lance sidecar)
# 7. nimtable (UI for Iceberg)
# 8. cognee + graphiti + falkordb + memgraph + memgraph-lab (graph DB backends)
# 9. olake (CDC)
# 10. otel-collector (telemetry)
#
# Per Plan 5 of the 2026-10 convergence saga.
# Uses the canonical mise workflow under the hood but with the explicit ordering.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="${REPO_ROOT}/bonnegar/stacks/lakehouse/compose.yaml"

if ! command -v docker &> /dev/null; then
    echo "  ✗ docker not found"
    exit 1
fi

if ! docker ps --format "{{.Names}}" 2>/dev/null | grep -q .; then
    echo "  ✗ docker daemon not reachable (tried OrbStack socket)"
    echo "  → Check OrbStack is running: ls /Users/cianmacandeisigh/.orbstack/run/"
    exit 1
fi

echo "  Starting the 12 down lakehouse services in dependency order..."

# 2. garage + garage-init (S3)
echo "  → garage + garage-init"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up -d garage garage-init

# 3. redis (cache + queue)
echo "  → redis"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up -d redis

# 4. lakekeeper-migrate (one-shot migration)
echo "  → lakekeeper-migrate (one-shot)"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up lakekeeper-migrate

# 5. lakekeeper
echo "  → lakekeeper"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up -d lakekeeper

# 6. lance-namespace
echo "  → lance-namespace"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up -d lance-namespace

# 7. nimtable
echo "  → nimtable"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up -d nimtable

# 8. graph DB backends
echo "  → cognee + graphiti + falkordb + memgraph + memgraph-lab"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up -d cognee graphiti falkordb memgraph memgraph-lab

# 9. olake (CDC)
echo "  → olake"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up -d olake

# 10. otel-collector
echo "  → otel-collector"
docker compose --env-file "${REPO_ROOT}/.env" -f "${COMPOSE_FILE}" up -d otel-collector

echo ""
echo "  ✓ All 12 services up. Run scripts/lakehouse/init_lakehouse_postgres.sh next."
