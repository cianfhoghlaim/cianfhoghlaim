#!/usr/bin/env bash
# =============================================================================
# LAKEHOUSE UNIFIED - Canonical Bring-Up Shell Entry Point
# =============================================================================
# Per the 2026-08-15-lakehouse-unified-data-plane-v1 change. Brings up the
# entire data plane (16 services) with one command:
#   - 11 existing lakehouse data plane services
#   - 5 graph DB services (cognee + graphiti + falkordb + memgraph + memgraph-lab)
#
# Usage:
#   mise run lakehouse:up                    # full bring-up + preflight
#   ./scripts/lakehouse_unified_up.sh        # same
#   ./scripts/lakehouse_unified_up.sh --skip-preflight  # bring-up only
#   ./scripts/lakehouse_unified_up.sh --compose-only    # docker compose up only
#
# Exit codes:
#   0 = all services healthy + preflight passed
#   1 = docker compose failed
#   2 = preflight failed
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------
SKIP_PREFLIGHT=false
COMPOSE_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --skip-preflight) SKIP_PREFLIGHT=true ;;
    --compose-only) COMPOSE_ONLY=true ;;
    --help|-h)
      sed -n '3,20p' "$0"
      exit 0
      ;;
    *) echo "Unknown arg: $arg"; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Resolve repo root
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

# ---------------------------------------------------------------------------
# Pre-flight: env file
# ---------------------------------------------------------------------------
if [[ ! -f .env ]] && [[ -z "${INFISICAL_ENV:-}" ]]; then
  echo "WARNING: .env not found at ${REPO_ROOT}/.env"
  echo "  Run 'mise run secrets:init' first to hydrate .env from Infisical."
  echo "  Continuing — docker compose will fall back to defaults where possible."
fi

# ---------------------------------------------------------------------------
# Pre-flight: docker daemon
# ---------------------------------------------------------------------------
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: docker daemon not reachable. Start Docker Desktop first."
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 1: docker compose up
# ---------------------------------------------------------------------------
echo "=== Lakehouse unified bring-up (16 services) ==="
echo "  - 11 lakehouse data plane services (garage + postgres + clickhouse + redis + lakekeeper + lance-namespace + nimtable + olake + lancedb-viewer + garage-init + lakekeeper-migrate)"
echo "  - 5 graph DB services (cognee + graphiti + falkordb + memgraph + memgraph-lab)"
echo ""
echo ">>> docker compose -f compose.yaml -f sidecar.yaml up -d"
docker compose \
  -f compose.yaml \
  -f sidecar.yaml \
  up -d

if [[ $? -ne 0 ]]; then
  echo "ERROR: docker compose up failed."
  exit 1
fi

if [[ "${COMPOSE_ONLY}" == "true" ]]; then
  echo ""
  echo "✓ compose up complete (--compose-only — skipping preflight)"
  exit 0
fi

# ---------------------------------------------------------------------------
# Step 2: wait for healthchecks (max 90s)
# ---------------------------------------------------------------------------
echo ""
echo ">>> waiting 30s for healthchecks..."
sleep 30

# ---------------------------------------------------------------------------
# Step 3: preflight (unless --skip-preflight)
# ---------------------------------------------------------------------------
if [[ "${SKIP_PREFLIGHT}" == "true" ]]; then
  echo ""
  echo "✓ bring-up complete (--skip-preflight — skipping preflight)"
  echo "  Run 'mise run lakehouse:preflight' to verify."
  exit 0
fi

echo ""
echo ">>> mise run lakehouse:preflight"
if mise run lakehouse:preflight; then
  echo ""
  echo "✓ Lakehouse unified bring-up complete + preflight passed"
  echo "  16 services healthy + 13 databases present + 8 buckets present"
  exit 0
else
  echo ""
  echo "✗ Lakehouse preflight failed. Run 'mise run lakehouse:preflight' for details."
  exit 2
fi