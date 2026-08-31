#!/usr/bin/env bash
# =============================================================================
# start.sh — one-shot bring-up for the mylar3 + qbittorrent-gluetun stacks
# =============================================================================#
# USAGE
#   ./start.sh                              # both stacks, dev mode
#   ./start.sh mylar3                       # only mylar3
#   ./start.sh qbittorrent-gluetun          # only qbittorrent-gluetun
#   PRODUCTION=1 ./start.sh                 # Locket sidecar (Infisical secrets)
#
# PREREQUISITES
#   - .env.local exists (copy from .env.example in each stack directory)
#   - For production: PANGOLIN_API_KEY exported + WireGuard creds in Infisical
#
# NETWORK
#   Both stacks join the canonical `cianfhoghlaim` Docker network so
#   Mylar3 can reach qBittorrent at qbittorrent-gluetun:8080 (DNS-based).
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACKS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PRODUCTION="${PRODUCTION:-}"
TARGET="${1:-all}"

start_stack() {
  local name="$1"
  local dir="$STACKS_DIR/$name"
  local compose_args=(--env-file .env.local -f compose.yaml)
  local label="[DEV]"

  if [[ -n "$PRODUCTION" ]]; then
    compose_args=(-f compose.yaml -f sidecar.yaml)
    label="[PROD]"
  fi

  echo ""
  echo "==> $label Starting stack: $name"
  echo "    dir: $dir"
  echo "    args: docker compose ${compose_args[*]} up -d"

  if [[ ! -f "$dir/.env.local" && -z "$PRODUCTION" ]]; then
    echo "    [WARN] $dir/.env.local not found — copying from .env.example"
    cp "$dir/.env.example" "$dir/.env.local"
  fi

  (cd "$dir" && docker compose "${compose_args[@]}" up -d)
}

case "$TARGET" in
  all)
    start_stack "mylar3"
    start_stack "qbittorrent-gluetun"
    ;;
  mylar3)
    start_stack "mylar3"
    ;;
  qbittorrent-gluetun|qbit)
    start_stack "qbittorrent-gluetun"
    ;;
  *)
    echo "usage: $0 [mylar3|qbittorrent-gluetun|all]   (env: PRODUCTION=1)" >&2
    exit 1
    ;;
esac

echo ""
echo "==> Done. Container status:"
docker ps --filter "name=mylar3" --filter "name=qbittorrent" --filter "name=gluetun" \
  --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "==> Next steps:"
echo "    1. Apply the Pangolin blueprints (one-time):"
echo "         export PANGOLIN_API_KEY='<apiKeyId>.<apiKeySecret>'"
echo "         $STACKS_DIR/../pangolin/apply-blueprint.sh $STACKS_DIR/mylar3/blueprint.yaml"
echo "         $STACKS_DIR/../pangolin/apply-blueprint.sh $STACKS_DIR/qbittorrent-gluetun/blueprint.yaml"
echo ""
echo "    2. Reach the services from a Pangolin-connected device:"
echo "         https://mylar3.cianfhoghlaim.ie"
echo "         https://qbittorrent.cianfhoghlaim.ie"
echo ""
echo "    3. Wire Mylar3 → qBittorrent:"
echo "         Open https://mylar3.cianfhoghlaim.ie"
echo "         Settings → Download Clients → Add → qBittorrent"
echo "         Host: qbittorrent-gluetun"
echo "         Port: 8080"
echo "         User: admin"
echo "         Pass: from Infisical dev-baile/qbittorrent-gluetun/webui_password"
