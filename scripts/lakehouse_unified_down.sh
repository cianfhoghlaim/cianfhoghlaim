#!/usr/bin/env bash
# =============================================================================
# LAKEHOUSE UNIFIED - Canonical Teardown Shell Entry Point
# =============================================================================
# Per the 2026-08-15-lakehouse-unified-data-plane-v1 change. Tears down the
# entire data plane (16 services) with one command.
#
# Usage:
#   mise run lakehouse:down                    # docker compose down + remove volumes
#   ./scripts/lakehouse_unified_down.sh         # same
#   ./scripts/lakehouse_unified_down.sh --keep-volumes  # keep named volumes
#
# Exit codes:
#   0 = teardown succeeded
#   1 = docker compose failed
# =============================================================================
set -euo pipefail

# ---------------------------------------------------------------------------
# Parse args
# ---------------------------------------------------------------------------
KEEP_VOLUMES=false
for arg in "$@"; do
  case "$arg" in
    --keep-volumes) KEEP_VOLUMES=true ;;
    --help|-h)
      sed -n '3,15p' "$0"
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
# Pre-flight: docker daemon
# ---------------------------------------------------------------------------
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: docker daemon not reachable."
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 1: docker compose down
# ---------------------------------------------------------------------------
echo "=== Lakehouse unified teardown (16 services) ==="
echo ">>> docker compose -f compose.yaml -f sidecar.yaml down"
docker compose \
  -f compose.yaml \
  -f sidecar.yaml \
  down

if [[ $? -ne 0 ]]; then
  echo "ERROR: docker compose down failed."
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 2: optionally remove volumes
# ---------------------------------------------------------------------------
if [[ "${KEEP_VOLUMES}" == "true" ]]; then
  echo ""
  echo "✓ teardown complete (--keep-volumes — named volumes preserved)"
  exit 0
fi

echo ""
echo ">>> removing lakehouse-falkordb-data + lakehouse-memgraph-lib/log + lakehouse-postgres"
echo "  (use --keep-volumes to preserve named volumes)"
docker volume rm \
  lakehouse-falkordb-data \
  lakehouse-memgraph-lib \
  lakehouse-memgraph-log \
  lakehouse-postgres 2>/dev/null || true

echo ""
echo "✓ Lakehouse unified teardown complete"