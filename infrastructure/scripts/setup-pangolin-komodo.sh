#!/usr/bin/env bash
# =============================================================================
# setup-pangolin-komodo.sh — End-to-end bootstrap of the Cianfhoghlaim
# convergence architecture: Pulumi → Infisical → Pangolin → Komodo → Newt
# =============================================================================
# Idempotent. Safe to re-run. Reads secrets from the local .env (which is
# hydrated by `mise` directory hooks from .infisical.env).
#
# Usage:
#   ./setup-pangolin-komodo.sh oci          # Phase 1: Pulumi bootstrap OCI
#   ./setup-pangolin-komodo.sh cloudflare   # Phase 1b: Pulumi bootstrap Cloudflare
#   ./setup-pangolin-komodo.sh vault        # Phase 2: Infisical vault sync
#   ./setup-pangolin-komodo.sh pangolin     # Phase 3: Bring up Pangolin on arm1-oci
#   ./setup-pangolin-komodo.sh komodo-core  # Phase 4: Bring up Komodo Core on mbp
#   ./setup-pangolin-komodo.sh komodo-periphery-mbp     # Phase 5
#   ./setup-pangolin-komodo.sh komodo-periphery-oci     # Phase 6
#   ./setup-pangolin-komodo.sh newt-mbp     # Phase 7: Bring up Pangolin Newt on mbp
#   ./setup-pangolin-komodo.sh stacks       # Phase 8: Deploy stacks via komodo_client SDK
#   ./setup-pangolin-komodo.sh resources    # Phase 9: Create Pangolin resources via API
#   ./setup-pangolin-komodo.sh all          # Run phases 1-9 in order
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

OCI_HOST="oci.arm1"
OCI_IP="140.238.96.148"
OCI_USER="ubuntu"
PANGOLIN_STACK_DIR="/opt/pangolin"
KOMODO_STACK_DIR="$HOME/.config/komodo"
NEWT_STACK_DIR="$HOME/.config/pangolin-newt"

# ANSI colors
RED=$'\e[31m'
GREEN=$'\e[32m'
YELLOW=$'\e[33m'
BLUE=$'\e[34m'
RESET=$'\e[0m'

log()   { echo "${BLUE}[setup]${RESET} $*"; }
ok()    { echo "${GREEN}[setup] ✓${RESET} $*"; }
warn()  { echo "${YELLOW}[setup] !${RESET} $*"; }
err()   { echo "${RED}[setup] ✗${RESET} $*" >&2; exit 1; }

# ----- Preflight -----
preflight() {
  log "preflight checks"
  command -v docker >/dev/null || err "docker not installed"
  command -v pulumi >/dev/null || err "pulumi not installed"
  command -v ssh    >/dev/null || err "ssh not installed"
  command -v rsync  >/dev/null || err "rsync not installed"
  [ -f "$REPO_ROOT/.env" ] || err ".env not found at repo root"
  ok "preflight passed"
}

# ----- Phase 1: Pulumi OCI -----
phase_oci() {
  log "Phase 1: Pulumi OCI bootstrap"
  cd infrastructure/pulumi/oci
  pulumi up --yes
  ok "Pulumi OCI stack up-to-date"
  cd "$REPO_ROOT"
}

# ----- Phase 1b: Pulumi Cloudflare -----
phase_cloudflare() {
  log "Phase 1b: Pulumi Cloudflare bootstrap"
  cd infrastructure/pulumi/cloudflare
  if ! pulumi config get cloudflare:apiToken >/dev/null 2>&1; then
    warn "cloudflare:apiToken not set; skipping (set with: pulumi config set --secret cloudflare:apiToken cfat_xxx)"
    return 0
  fi
  pulumi up --yes
  ok "Pulumi Cloudflare stack up-to-date"
  cd "$REPO_ROOT"
}

# ----- Phase 2: Infisical vault sync -----
phase_vault() {
  log "Phase 2: Infisical vault sync"
  bun run scripts/init-vault.ts
  ok "Infisical vault synced from .env"
}

# ----- Phase 3: Bring up Pangolin on arm1-oci -----
phase_pangolin() {
  log "Phase 3: Pangolin stack on arm1-oci"
  local local_stack="infrastructure/stacks/infrastructure/pangolin"
  [ -d "$local_stack" ] || err "local pangolin stack not found at $local_stack"

  log "  → syncing $local_stack → $OCI_HOST:$PANGOLIN_STACK_DIR"
  rsync -avz --delete \
    -e "ssh" \
    "$local_stack/" \
    "$OCI_USER@$OCI_HOST:$PANGOLIN_STACK_DIR/"

  log "  → bringing up docker compose"
  ssh "$OCI_HOST" "cd $PANGOLIN_STACK_DIR && docker compose up -d"
  ssh "$OCI_HOST" "cd $PANGOLIN_STACK_DIR && sleep 10 && docker compose ps"

  log "  → testing public endpoint"
  if curl -fsSI "https://pangolin.cianfhoghlaim.ie" >/dev/null 2>&1; then
    ok "pangolin.cianfhoghlaim.ie is healthy"
  else
    warn "pangolin.cianfhoghlaim.ie not responding; check docker logs on $OCI_HOST"
  fi
}

# ----- Phase 4: Komodo Core on mbp -----
phase_komodo_core() {
  log "Phase 4: Komodo Core on mbp"
  local local_stack="infrastructure/stacks/infrastructure/komodo"
  mkdir -p "$KOMODO_STACK_DIR"
  rsync -avz --delete "$local_stack/" "$KOMODO_STACK_DIR/"

  if [ ! -f "$KOMODO_STACK_DIR/.env" ]; then
    log "  → generating .env with random secrets"
    cat > "$KOMODO_STACK_DIR/.env" <<EOF
KOMODO_DATABASE_USERNAME=komodo
KOMODO_DATABASE_PASSWORD=$(openssl rand -hex 24)
KOMODO_JWT_SECRET=$(openssl rand -hex 32)
KOMODO_PASSKEY=$(openssl rand -hex 32)
KOMODO_INIT_ADMIN_USERNAME=ciansedai
KOMODO_INIT_ADMIN_PASSWORD=$(openssl rand -hex 16)
KOMODO_HOST=https://komodo.cianfhoghlaim.ie
INFISICAL_CLIENT_ID=c56cbe28-88a4-4793-95a1-835d5164d8ad
INFISICAL_PROJECT_ID=f3cff583-b74b-4804-b9d3-db8b68885236
INFISICAL_SECRET_FILE=$KOMODO_STACK_DIR/infisical_secret
LOCKET_MODE=watch
EOF
    ok "  generated $KOMODO_STACK_DIR/.env"
  fi

  if [ ! -f "$KOMODO_STACK_DIR/infisical_secret" ]; then
    if [ -f "$REPO_ROOT/infisical_secret" ]; then
      cp "$REPO_ROOT/infisical_secret" "$KOMODO_STACK_DIR/infisical_secret"
      ok "  copied infisical_secret"
    else
      warn "  infisical_secret not found; locket will be unhealthy until placed"
    fi
  fi

  cd "$KOMODO_STACK_DIR"
  docker compose -f compose.yaml -f sidecar.yaml up -d
  docker compose ps
  cd "$REPO_ROOT"
  ok "Komodo Core is up on :9120"
}

# ----- Phase 5: Komodo Periphery (mbp) -----
phase_komodo_periphery_mbp() {
  log "Phase 5: Komodo Periphery (mbp)"
  cd "$KOMODO_STACK_DIR"
  docker compose -f compose.yaml -f sidecar.yaml -f periphery.yaml up -d
  docker compose ps
  cd "$REPO_ROOT"
  ok "Komodo Periphery (mbp) is up on :8120"
}

# ----- Phase 6: Komodo Periphery (arm1-oci) -----
phase_komodo_periphery_oci() {
  log "Phase 6: Komodo Periphery (arm1-oci)"
  ssh "$OCI_HOST" "mkdir -p /etc/komodo"
  rsync -avz --delete \
    "$KOMODO_STACK_DIR/" \
    "$OCI_USER@$OCI_HOST:/etc/komodo/"

  ssh "$OCI_HOST" "cd /etc/komodo && docker compose -f periphery.yaml -f sidecar.yaml up -d"
  ssh "$OCI_HOST" "cd /etc/komodo && docker compose ps"
  ok "Komodo Periphery (arm1-oci) is up on :8120"
}

# ----- Phase 7: Pangolin Newt (mbp) -----
phase_newt_mbp() {
  log "Phase 7: Pangolin Newt (mbp)"
  local local_dir="infrastructure/stacks/infrastructure/pangolin"
  mkdir -p "$NEWT_STACK_DIR"
  for f in newt.yaml newt.sidecar.yaml newt.secrets.env; do
    rsync -av "$local_dir/$f" "$NEWT_STACK_DIR/"
  done

  if [ ! -f "$NEWT_STACK_DIR/infisical_secret" ]; then
    if [ -f "$REPO_ROOT/infisical_secret" ]; then
      cp "$REPO_ROOT/infisical_secret" "$NEWT_STACK_DIR/infisical_secret"
    else
      warn "  infisical_secret not found; locket will be unhealthy"
    fi
  fi

  cd "$NEWT_STACK_DIR"
  docker compose -f newt.yaml -f newt.sidecar.yaml up -d
  docker compose ps
  cd "$REPO_ROOT"
  ok "Pangolin Newt (mbp) is up; check wg interface in container"
}

# ----- Phase 8: Deploy stacks via komodo_client SDK -----
phase_stacks() {
  log "Phase 8: Deploy stacks via komodo_client TypeScript SDK"
  bun run scripts/deploy-stacks.ts
  ok "stacks deployed via Komodo"
}

# ----- Phase 9: Create Pangolin resources via Integrations API -----
phase_resources() {
  log "Phase 9: Create Pangolin resources via Integrations API"
  bun run scripts/create-pangolin-resources.ts
  ok "Pangolin resources created"
}

# ----- Main -----
case "${1:-help}" in
  preflight)     preflight ;;
  oci)           phase_oci ;;
  cloudflare)    phase_cloudflare ;;
  vault)         phase_vault ;;
  pangolin)      phase_pangolin ;;
  komodo-core)   phase_komodo_core ;;
  komodo-periphery-mbp)  phase_komodo_periphery_mbp ;;
  komodo-periphery-oci)  phase_komodo_periphery_oci ;;
  newt-mbp)      phase_newt_mbp ;;
  stacks)        phase_stacks ;;
  resources)     phase_resources ;;
  all)           preflight
                 phase_oci
                 phase_cloudflare
                 phase_vault
                 phase_pangolin
                 phase_komodo_core
                 phase_komodo_periphery_mbp
                 phase_komodo_periphery_oci
                 phase_newt_mbp
                 phase_stacks
                 phase_resources
                 ;;
  *) cat <<EOF
Usage: $0 {preflight|oci|cloudflare|vault|pangolin|komodo-core|komodo-periphery-mbp|komodo-periphery-oci|newt-mbp|stacks|resources|all}
EOF
     exit 1 ;;
esac
