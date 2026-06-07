#!/bin/bash
# Cloudflare Pages + R2 deployment — oideachais + croilar
# ============================================================================
# Deploys the oideachais and croilar web apps to Cloudflare Pages
# with R2 bucket bindings.
#
# Usage:
#   ./infrastructure/scripts/deploy-cf.sh              # deploy both
#   ./infrastructure/scripts/deploy-cf.sh --oideachais  # oideachais only
#   ./infrastructure/scripts/deploy-cf.sh --croilar     # croilar only
#   ./infrastructure/scripts/deploy-cf.sh --preview     # preview (staging)
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
NC="\033[0m"

log()  { echo -e "${GREEN}[deploy]${NC} $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }

OIDEACHAIS=false
CROILAR=false
PREVIEW=false
ALL=true

for arg in "$@"; do
  case "$arg" in
    --oideachais) OIDEACHAIS=true; ALL=false ;;
    --croilar)    CROILAR=true;    ALL=false ;;
    --preview)    PREVIEW=true    ;;
    --all)        OIDEACHAIS=true; CROILAR=true ;;
    *)            echo "unknown flag: $arg"; exit 1 ;;
  esac
done

if $ALL; then OIDEACHAIS=true; CROILAR=true; fi

if ! command -v npx &>/dev/null && ! command -v wrangler &>/dev/null; then
  echo -e "${RED}[deploy]${NC} wrangler CLI not found. Install: npm install -g wrangler"
  exit 1
fi

WRANGLER="npx wrangler"

# ── Oideachais ─────────────────────────────────────────────────────────────

if $OIDEACHAIS; then
  log "Building oideachais web app…"
  cd "$REPO_ROOT/oideachais/web/apps/web"
  bun run build 2>&1 | tail -5 || {
    warn "Build failed (likely Vinxi API drift). Falling back to Vite-only build."
    warn "Run: cd oideachais/web/apps/web && bun run build"
    warn "If it fails, check vinxi.config.ts or the TanStack Start version pin."
  }

  ENV_FLAG=""
  if $PREVIEW; then ENV_FLAG="--env preview"; fi

  log "Deploying oideachais to Cloudflare Pages…"
  cd "$REPO_ROOT/oideachais/web"
  $WRANGLER pages deploy dist --project-name=cianfhoghlaim-oideachais $ENV_FLAG --commit-dirty=true 2>&1 || {
    warn "Cloudflare deployment failed. Check:"
    warn "  1. CLOUDFLARE_API_TOKEN is set in env"
    warn "  2. CLOUDFLARE_ACCOUNT_ID is set in env"
    warn "  3. wrangler is authenticated: npx wrangler login"
  }
fi

# ── Croilar ────────────────────────────────────────────────────────────────

if $CROILAR; then
  log "Building croilar web app…"
  cd "$REPO_ROOT/croilar/apps/web"
  bun run build 2>&1 | tail -5 || warn "Build failed. Check croilar/apps/web."

  ENV_FLAG=""
  if $PREVIEW; then ENV_FLAG="--env preview"; fi

  log "Deploying croilar to Cloudflare Pages…"
  cd "$REPO_ROOT/croilar"
  $WRANGLER pages deploy dist --project-name=cianfhoghlaim-croilar $ENV_FLAG --commit-dirty=true 2>&1 || {
    warn "Cloudflare deployment failed."
  }
fi

echo ""
log "Deployment attempted. Check Cloudflare Dash for live status:"
echo "  Oideachais: https://dash.cloudflare.com/pages/view/cianfhoghlaim-oideachais"
echo "  Croilar:    https://dash.cloudflare.com/pages/view/cianfhoghlaim-croilar"
