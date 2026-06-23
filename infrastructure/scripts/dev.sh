#!/bin/bash
# oideachais dev deployment — one-command bring-up
# ============================================================================
# Starts the oideachais platform in dev mode:
#   1. Dependency check (Docker, bun, uv, mise)
#   2. Docker Compose stack (if Docker is running)
#   3. Vite dev server (TanStack Start, port 3001)
#   4. Dagster webserver (port 3335, if Python deps installed)
#
# Usage:
#   ./infrastructure/scripts/dev.sh              # bring everything up
#   ./infrastructure/scripts/dev.sh --web-only    # just the Vite dev server
#   ./infrastructure/scripts/dev.sh --docker-only # just Docker Compose
#   ./infrastructure/scripts/dev.sh --status      # check what's running
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# ── Colours ────────────────────────────────────────────────────────────────

GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
NC="\033[0m"

log()  { echo -e "${GREEN}[dev]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
err()  { echo -e "${RED}[err]${NC} $*"; }

# ── Flags ──────────────────────────────────────────────────────────────────

WEB_ONLY=false
DOCKER_ONLY=false
STATUS=false

for arg in "$@"; do
  case "$arg" in
    --web-only)   WEB_ONLY=true   ;;
    --docker-only) DOCKER_ONLY=true ;;
    --status)     STATUS=true     ;;
    *)             echo "unknown flag: $arg"; exit 1 ;;
  esac
done

# ── Status check ───────────────────────────────────────────────────────────

if $STATUS; then
  log "Checking oideachais dev status…"
  echo ""

  # Docker
  if docker info &>/dev/null; then
    echo "  Docker:   running"
    docker ps --filter "name=cianchoghlaim-oideachais" --format "  ├─ {{.Names}}: {{.Status}}" 2>/dev/null || echo "  └─ (no oideachais containers)"
  else
    echo "  Docker:   not running (OrbStack/Docker Desktop not started)"
  fi

  # Vite
  if pgrep -f "vite dev.*oideachais" &>/dev/null; then
    echo "  Vite:     running (port 3001)"
  else
    echo "  Vite:     not running"
  fi

  # Dagster
  if pgrep -f "dagster.*oideachais" &>/dev/null; then
    echo "  Dagster:  running (port 3335)"
  else
    echo "  Dagster:  not running"
  fi

  exit 0
fi

# ── Pre-flight ─────────────────────────────────────────────────────────────

log "Pre-flight checks…"

if ! command -v bun &>/dev/null; then
  err "bun is not installed. Run: brew install bun"
  exit 1
fi

if ! $DOCKER_ONLY; then
  cd "$REPO_ROOT/oideachais/web"
  if [ ! -d "node_modules" ]; then
    log "Installing web dependencies…"
    bun install
  fi
fi

# ── Docker Compose ─────────────────────────────────────────────────────────

if ! $WEB_ONLY; then
  COMPOSE_FILE="$REPO_ROOT/infrastructure/stacks/oideachais/compose.yaml"

  if docker info &>/dev/null; then
    log "Docker is running. Starting oideachais Docker Compose stack…"
    cd "$REPO_ROOT/infrastructure/stacks/oideachais"

    # Dev mode: use compose.dev.yaml (local .env, no Locket sidecar)
    docker compose -f compose.yaml -f compose.dev.yaml up -d 2>&1 | tail -10

    log "Waiting for containers to be healthy…"
    sleep 5
    docker compose ps 2>/dev/null || true

    echo ""
    log "Oideachais stack started."
    echo "  → Frontend:  http://localhost:3000"
    echo "  → API:       http://localhost:8000"
    echo "  → Dagster:   http://localhost:3335"
  else
    warn "Docker is not running (OrbStack/Docker Desktop not started)."
    warn "Skipping Docker Compose. Start Docker and re-run to bring up containers."
    warn "Or use:  ./infrastructure/scripts/dev.sh --web-only"
  fi
fi

# ── Vite Dev Server ────────────────────────────────────────────────────────

if ! $DOCKER_ONLY; then
  echo ""
  log "Starting Vite dev server (TanStack Start, port 3001)…"
  cd "$REPO_ROOT/oideachais/web/apps/web"
  log "Dev server at http://localhost:3001"
  log "Leaving Cert pages at http://localhost:3001/leaving-cert/mathematics"
  echo ""

  # Run in foreground so the user sees the dev server output
  exec bun run dev
fi
