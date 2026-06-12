#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# Run the 3 NEW frontend apps in development mode (bun dev) as background
# processes. Use this when the containerized services are not yet ready
# but you want the new apps (tuatha-ui, croilar-web, croilar-portal) to be
# accessible at their dev ports.
#
# Usage:
#   ./infrastructure/stacks/engineering/frontend/scripts/dev-start.sh start
#   ./infrastructure/stacks/engineering/frontend/scripts/dev-start.sh stop
#   ./infrastructure/stacks/engineering/frontend/scripts/dev-start.sh status
#   ./infrastructure/stacks/engineering/frontend/scripts/dev-start.sh logs
# ----------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

TUATHA_LOG=/tmp/tuatha-ui.log
CROILAR_WEB_LOG=/tmp/croilar-web.log
CROILAR_PORTAL_LOG=/tmp/croilar-portal.log

start() {
  echo "==> Starting tuatha-ui on :3004"
  cd "$ROOT/tuatha/ui"
  nohup bun dev > "$TUATHA_LOG" 2>&1 &
  echo $! > /tmp/tuatha-ui.pid

  echo "==> Starting croilar-web on :3003"
  cd "$ROOT/croilar/apps/web"
  nohup bun dev --port 3003 > "$CROILAR_WEB_LOG" 2>&1 &
  echo $! > /tmp/croilar-web.pid

  echo "==> Starting croilar-portal on :3002 (avoids 3000 conflict with oideachais-frontend)"
  cd "$ROOT/croilar/apps/portal"
  nohup bun dev --port 3002 > "$CROILAR_PORTAL_LOG" 2>&1 &
  echo $! > /tmp/croilar-portal.pid

  sleep 12

  echo ""
  echo "==> Health checks:"
  for entry in "tuatha-ui:3004" "croilar-web:3003" "croilar-portal:3002"; do
    name="${entry%%:*}"
    port="${entry##*:}"
    url="http://localhost:$port/"
    printf "  %s (%s): " "$name" "$url"
    code=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 5 "$url" || echo "FAIL")
    echo "HTTP $code"
  done
}

stop() {
  echo "==> Stopping dev servers"
  for pidfile in /tmp/tuatha-ui.pid /tmp/croilar-web.pid /tmp/croilar-portal.pid; do
    if [ -f "$pidfile" ]; then
      pid=$(cat "$pidfile")
      kill "$pid" 2>/dev/null || true
      rm -f "$pidfile"
    fi
  done
  pkill -f "vite dev" 2>/dev/null || true
  sleep 1
  echo "Done."
}

status() {
  for entry in "tuatha-ui:3004" "croilar-web:3003" "croilar-portal:3002"; do
    name="${entry%%:*}"
    port="${entry##*:}"
    url="http://localhost:$port/"
    code=$(curl -sf -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "DOWN")
    printf "  %-20s :%s — HTTP %s\n" "$name" "$port" "$code"
  done
}

logs() {
  case "${1:-all}" in
    tuatha) tail -50 "$TUATHA_LOG" ;;
    web) tail -50 "$CROILAR_WEB_LOG" ;;
    portal) tail -50 "$CROILAR_PORTAL_LOG" ;;
    all|*)
      echo "=== tuatha-ui ==="
      tail -20 "$TUATHA_LOG"
      echo "=== croilar-web ==="
      tail -20 "$CROILAR_WEB_LOG"
      echo "=== croilar-portal ==="
      tail -20 "$CROILAR_PORTAL_LOG"
      ;;
  esac
}

case "${1:-status}" in
  start) start ;;
  stop) stop ;;
  status) status ;;
  logs) logs "${2:-all}" ;;
  *) echo "Usage: $0 {start|stop|status|logs [tuatha|web|portal]}" ;;
esac
