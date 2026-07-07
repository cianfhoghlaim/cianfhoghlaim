#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# Master deploy script for the full Cianfhoghlaim frontend platform.
#
# Boots all required backend services (postgres, convex, hono-api, litellm)
# and the 5 frontend workspaces via docker compose.
#
# Usage:
#   ./infrastructure/stacks/frontend/scripts/deploy.sh up
#   ./infrastructure/stacks/frontend/scripts/deploy.sh down
#   ./infrastructure/stacks/frontend/scripts/deploy.sh logs
#   ./infrastructure/stacks/frontend/scripts/deploy.sh status
# ----------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

# Stack compose paths in dependency order
POSTGRES="$ROOT/infrastructure/stacks/croilar-postgres/compose.yaml"
CONVEX="$ROOT/infrastructure/stacks/convex/compose.yaml"
LITELLM="$ROOT/infrastructure/stacks/litellm/compose.yaml"
HONO_API="$ROOT/infrastructure/stacks/croilar-hono-api/compose.yaml"
FRONTEND="$ROOT/infrastructure/stacks/frontend/compose.yaml"
FRONTEND_DEV="$ROOT/infrastructure/stacks/frontend/compose.dev.yaml"

CMD="${1:-status}"

case "$CMD" in
  up)
    echo "==> Bringing up backends: postgres → convex → litellm → hono-api"
    BUILD_CONTEXT="$ROOT" \
    docker compose \
      -f "$POSTGRES" \
      -f "$CONVEX" \
      -f "$LITELLM" \
      -f "$HONO_API" \
      -p cianfhoghlaim-backend \
      up -d --build

    echo "==> Bringing up frontend (with dev overrides if available)"
    DOCKER_COMPOSE_FILES="-f $FRONTEND"
    [[ -f "$FRONTEND_DEV" ]] && DOCKER_COMPOSE_FILES="$DOCKER_COMPOSE_FILES -f $FRONTEND_DEV"

    # shellcheck disable=SC2086
    docker compose $DOCKER_COMPOSE_FILES \
      -p cianfhoghlaim-frontend \
      up -d --build

    echo "==> Frontend deployed. Waiting 30s for health checks…"
    sleep 30

    PORTS=(3001 8787 3004 3003 3000)
    SERVICES=(oideachais-web oideachais-api tuatha-ui croilar-web croilar-portal)
    FAILED=0
    for i in "${!SERVICES[@]}"; do
      svc="${SERVICES[$i]}"
      port="${PORTS[$i]}"
      url="http://localhost:$port/"
      printf "  %s (%s): " "$svc" "$url"
      if curl -sf --max-time 5 "$url" >/dev/null 2>&1; then
        echo "OK"
      else
        echo "FAIL"
        FAILED=$((FAILED + 1))
      fi
    done

    if [[ $FAILED -gt 0 ]]; then
      echo "==> $FAILED service(s) failed health check. Inspect logs."
      docker compose $DOCKER_COMPOSE_FILES -p cianfhoghlaim-frontend logs --tail=100
      exit 1
    fi

    echo "==> All 5 services healthy."
    echo ""
    echo "Local URLs:"
    echo "  oideachais-web:    http://localhost:3001"
    echo "  oideachais-api:    http://localhost:8787"
    echo "  tuatha-ui:         http://localhost:3004"
    echo "  croilar-web:       http://localhost:3003"
    echo "  croilar-portal:    http://localhost:3000"
    echo ""
    echo "Production URLs (Pangolin routes):"
    echo "  https://oideachais.cianfhoghlaim.ie"
    echo "  https://tuath.cianfhoghlaim.ie"
    echo "  https://croilar.cianfhoghlaim.ie"
    echo "  https://portal.cianfhoghlaim.ie"
    ;;

  down)
    echo "==> Tearing down frontend"
    docker compose -f "$FRONTEND" -p cianfhoghlaim-frontend down --remove-orphans || true
    echo "==> Tearing down backends"
    docker compose \
      -f "$POSTGRES" \
      -f "$CONVEX" \
      -f "$LITELLM" \
      -f "$HONO_API" \
      -p cianfhoghlaim-backend \
      down --remove-orphans || true
    ;;

  logs)
    docker compose -f "$FRONTEND" -p cianfhoghlaim-frontend logs -f
    ;;

  status)
    docker compose -f "$FRONTEND" -p cianfhoghlaim-frontend ps 2>&1 || true
    echo "---"
    docker compose -f "$POSTGRES" -f "$CONVEX" -f "$LITELLM" -f "$HONO_API" -p cianfhoghlaim-backend ps 2>&1 || true
    ;;

  *)
    echo "Usage: $0 {up|down|logs|status}"
    exit 1
    ;;
esac
