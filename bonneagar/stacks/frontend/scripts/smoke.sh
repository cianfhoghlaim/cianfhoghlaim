#!/usr/bin/env bash
# ----------------------------------------------------------------------------
# Smoke test — boot all 5 frontend services via docker compose and verify
# each responds on its expected port.
#
# Usage:  ./infrastructure/stacks/frontend/scripts/smoke.sh
# Exits 0 on success, non-zero on any failure.
# ----------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$STACK_DIR"

PORTS=(3001 8787 3004 3003 3000)
SERVICES=(oideachais-web oideachais-api tuatha-ui croilar-web croilar-portal)

echo "==> Building and starting frontend stack (dev mode)…"
docker compose -f compose.yaml -f compose.dev.yaml up -d --build

echo "==> Waiting 30s for services to become healthy…"
sleep 30

FAILED=0
for i in "${!SERVICES[@]}"; do
  svc="${SERVICES[$i]}"
  port="${PORTS[$i]}"
  url="http://localhost:$port/"

  printf "==> %s (%s): " "$svc" "$url"
  if curl -sf --max-time 10 "$url" >/dev/null 2>&1; then
    echo "OK"
  else
    echo "FAIL"
    FAILED=$((FAILED + 1))
  fi
done

echo ""
echo "==> Health endpoints (detailed):"
curl -sf http://localhost:8787/ && echo ""  # oideachais-api
echo ""

if [[ $FAILED -gt 0 ]]; then
  echo "==> $FAILED service(s) failed health check"
  docker compose -f compose.yaml -f compose.dev.yaml logs --tail=50
  docker compose -f compose.yaml -f compose.dev.yaml down
  exit 1
fi

echo "==> All 5 services responded. Tearing down…"
docker compose -f compose.yaml -f compose.dev.yaml down

echo "==> Smoke test passed."
