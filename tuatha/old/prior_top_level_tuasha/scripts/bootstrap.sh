#!/usr/bin/env bash
# =============================================================================
# tuatha/scripts/bootstrap.sh
# =============================================================================
# One-command local dev setup for the Tuatha educational MMO stack.
#
# Steps:
#   1. Set USE_LOCAL_SCRAPES=true + USE_DUCKLAKE=false (no API credits, no lake)
#   2. Build the api/ui/game containers via the IaC stack
#   3. Boot SpacetimeDB + Dragonfly + Dagster + Langfuse (subset of tuatha/)
#   4. Seed the SpacetimeDB credential_events + player_assets tables with
#      bundled fixtures from stedding/dev/sruth/tuath/fixtures/
#   5. Run both dlt sources against a local DuckDB at ./tuatha.duckdb
#   6. Print the explore URLs
#
# Usage:
#   ./tuatha/scripts/bootstrap.sh
#   ./tuatha/scripts/bootstrap.sh --skip-docker-build
# =============================================================================

set -euo pipefail

WORKTREE="$(git rev-parse --show-toplevel)"
export USE_LOCAL_SCRAPES=true
export USE_DUCKLAKE=false
export DUCKDB_PATH="$WORKTREE/tuatha.duckdb"

SKIP_DOCKER_BUILD=false
SKIP_DLT=false
for arg in "$@"; do
  case "$arg" in
    --skip-docker-build) SKIP_DOCKER_BUILD=true ;;
    --skip-dlt) SKIP_DLT=true ;;
    -h|--help)
      cat <<USAGE
Usage: $0 [options]

Options:
  --skip-docker-build       Skip the docker compose build step (use existing images)
  --skip-dlt                Skip the dlt source run (just bring up the stack)
USAGE
      exit 0 ;;
    *) echo "unknown arg: $arg" >&2 ;;
  esac
done

log()  { printf '\033[1;34m[%s]\033[0m %s\n' "$(date -u +%H:%M:%S)" "$*"; }
ok()   { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m  !\033[0m %s\n' "$*"; }

log "Tuatha bootstrap → local dev"
log "================================"
log "  USE_LOCAL_SCRAPES=$USE_LOCAL_SCRAPES"
log "  USE_DUCKLAKE=$USE_DUCKLAKE"
log "  DUCKDB_PATH=$DUCKDB_PATH"

cd "$WORKTREE"

# Step 1: Docker compose (api + ui + game + spacetimedb + dragonfly + langfuse)
if [ "$SKIP_DOCKER_BUILD" != true ]; then
  log "Step 1: Build + boot the Tuatha Docker compose stack"
  if command -v docker >/dev/null 2>&1; then
    docker compose -f bonneagar/stacks/tuatha/compose.yaml \
                   -f bonneagar/stacks/tuatha/compose.dev.yaml \
                   up -d --build 2>&1 | tail -10 || true
    ok "Docker stack up (api → 8002, ui → 3010, game → 8080, langfuse → 3013)"
  else
    warn "docker not on PATH — assuming services are already up"
  fi
else
  warn "Step 1: SKIPPED (--skip-docker-build)"
fi

# Step 2: Seed SpacetimeDB with bundled fixtures (skipped if SpacetimeDB not running)
log "Step 2: Seed SpacetimeDB credentials_events + player_assets fixtures"
FIXTURE_DIR="$WORKTREE/stedding/dev/sruth/tuath/fixtures"
if [ -d "$FIXTURE_DIR" ] && command -v spacetime >/dev/null 2>&1; then
  (cd "$WORKTREE/stedding/dev/sruth/tuath" && \
     spacetime publish --module-path . tuatha-dev --clear-database 2>&1 | tail -5) || \
     warn "SpacetimeDB publish failed (continuing with dlt-only path)"
  ok "SpacetimeDB seeded"
else
  warn "Step 2: SKIPPED (no $FIXTURE_DIR or spacetime CLI)"
fi

# Step 3: Run both dlt sources against the local DuckDB
if [ "$SKIP_DLT" != true ]; then
  log "Step 3: Run both dlt sources into $DUCKDB_PATH"
  python3 -m tuatha.dlt.run_all 2>&1 | tail -10
  ok "dlt sources loaded (player_assets + credential_events)"
else
  warn "Step 3: SKIPPED (--skip-dlt)"
fi

# Step 4: Print the explore URLs
log "============================================"
log "Tuatha is live:"
log "  - Babylon.js game:  http://localhost:8080"
log "  - TanStack UI:      http://localhost:3010"
log "  - FastAPI healthz:  http://localhost:8002/healthz"
log "  - SpacetimeDB CLI:  spacetime logs tuatha-dev"
log "  - Langfuse UI:      http://localhost:3013"
log "  - Local DuckDB:     $DUCKDB_PATH"
log ""
log "Explore the local DuckDB:"
log "  duckdb $DUCKDB_PATH -c \"SHOW TABLES; SELECT COUNT(*) FROM cianfhoghlaim.tuatha.player_assets;\""
log ""
log "Tear down: ./tuatha/scripts/bootstrap.sh --skip-docker-build --skip-dlt  (no-op)"
log "            docker compose -f bonneagar/stacks/tuatha/compose.yaml down"
