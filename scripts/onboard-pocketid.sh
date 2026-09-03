#!/usr/bin/env bash
# onboard-pocketid.sh — Guided wizard for non-technical Pocket ID onboarding.
# See the full doc in the worktree.

set -euo pipefail

log()  { printf '\033[1;34m[%s]\033[0m %s\n' "$(date -u +%H:%M:%S)" "$*"; }
ok()   { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m  !\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m  ✗\033[0m %s\n' "$*"; }
step() { printf '\n\033[1;36m=== %s ===\033[0m\n' "$*"; }

NON_INTERACTIVE=false
SKIP_KOMODO=false
SKIP_WIRE=false
WITH_INFISICAL=false
POCKETID_API_KEY=""
PANGOLIN_API_KEY=""
POCKETID_URL="https://auth.cianfhoghlaim.ie"
PANGOLIN_URL="https://pangolin.cianfhoghlaim.ie"
PANGOLIN_ORG_ID="cianfhoghlaim"
DOMAIN="cianfhoghlaim.ie"
ENV_FILE="$(git rev-parse --show-toplevel)/.env"
WIRE_SCRIPT="$(git rev-parse --show-toplevel)/scripts/wire-pocketid-pangolin-komodo.sh"

usage() {
  cat <<USAGE
Usage: $0 [options]

Options:
  --non-interactive        Use values from .env (for CI / non-TTY)
  --pocketid-api-key=KEY  Pocket ID admin API key
  --pangolin-api-key=KEY  Pangolin API key
  --skip-komodo           Skip the Komodo step
  --skip-wire             Don't run the wire script (just write to .env)
  --with-infisical        Also persist to local Infisical
  --domain=DOMAIN         Domain (default: cianfhoghlaim.ie)
  -h, --help              Show this help
USAGE
  exit 0
}

for arg in "$@"; do
  case "$arg" in
    --non-interactive) NON_INTERACTIVE=true ;;
    --skip-komodo) SKIP_KOMODO=true ;;
    --skip-wire) SKIP_WIRE=true ;;
    --with-infisical) WITH_INFISICAL=true ;;
    --pocketid-api-key=*) POCKETID_API_KEY="${arg#*=}" ;;
    --pangolin-api-key=*) PANGOLIN_API_KEY="${arg#*=}" ;;
    --domain=*) DOMAIN="${arg#*=}" ;;
    -h|--help) usage ;;
    *) err "unknown arg: $arg; use --help for usage"; exit 2 ;;
  esac
done

echo
log "Pocket ID + Komodo + Pangolin Onboarding Wizard"
log "============================================"
log "  This wizard helps non-technical operators wire"
log "  the cianfhoghlaim stack to Pocket ID as the OIDC"
log "  identity provider for Komodo (orchestrator) +"
log "  Pangolin (proxy) + all Pangolin-protected services."

# Step 1: Collect credentials
step "Step 1: Collect credentials"

prompt() {
  local var="$1" label="$2" default="$3" secure="${4:-false}"
  local current="${!var:-}"
  if [ -n "$current" ]; then default="$current"; fi
  if [ "$NON_INTERACTIVE" = true ]; then eval "$var=\"$default\""; return; fi
  local value=""
  while [ -z "$value" ]; do
    if [ "$secure" = "true" ]; then
      read -r -s -p "  $label [$(echo $default | head -c 4)***]: " value; echo
    else
      read -r -p "  $label [$default]: " value
    fi
    [ -z "$value" ] && value="$default"
  done
  eval "$var=\"$value\""
}

if [ "$NON_INTERACTIVE" != true ]; then
  cat <<'PROMPT'
  You need 3 credentials. Where to get each:
    1. POCKETID_API_KEY: https://auth.cianfhoghlaim.ie → Settings → API Keys
    2. PANGOLIN_API_KEY: https://pangolin.cianfhoghlaim.ie → Settings → API Keys
    3. KOMODO_PASSWORD: your Komodo admin password (or use --skip-komodo)

PROMPT
fi

prompt POCKETID_API_KEY "Pocket ID admin API key" "" true
prompt POCKETID_URL "Pocket ID URL" "$POCKETID_URL"
prompt PANGOLIN_URL "Pangolin URL" "$PANGOLIN_URL"
prompt PANGOLIN_API_KEY "Pangolin API key" "" true
prompt PANGOLIN_ORG_ID "Pangolin org_id" "$PANGOLIN_ORG_ID"
prompt DOMAIN "Domain" "$DOMAIN"

# Step 2: Validate credentials
step "Step 2: Validate credentials"

if [ -n "$POCKETID_API_KEY" ]; then
  if curl -ksS -H "X-API-Key: $POCKETID_API_KEY" "$POCKETID_URL/api/admin/me" 2>/dev/null | grep -q "admin"; then
    ok "Pocket ID: API key valid (admin scope)"
  else
    err "Pocket ID: API key invalid or unreachable"
  fi
fi

if [ -n "$PANGOLIN_API_KEY" ]; then
  if curl -ksS -H "Authorization: Bearer $PANGOLIN_API_KEY" "$PANGOLIN_URL/api/v1/orgs" 2>/dev/null | grep -q "success"; then
    ok "Pangolin: API key valid"
  else
    err "Pangolin: API key invalid or unreachable"
  fi
fi

# Step 3: Write to .env
step "Step 3: Write credentials to $ENV_FILE"

upsert_env() {
  local key="$1" value="$2"
  [ -z "$value" ] && return
  if grep -q "^$key=" "$ENV_FILE" 2>/dev/null; then
    sed -i.bak "s|^$key=.*|$key=\"$value\"|" "$ENV_FILE" 2>/dev/null
  else
    echo "$key=\"$value\"" >> "$ENV_FILE"
  fi
}

touch "$ENV_FILE"
upsert_env POCKETID_URL "$POCKETID_URL"
upsert_env POCKETID_API_KEY "$POCKETID_API_KEY"
upsert_env PANGOLIN_URL "$PANGOLIN_URL"
upsert_env PANGOLIN_API_KEY "$PANGOLIN_API_KEY"
upsert_env PANGOLIN_ORG_ID "$PANGOLIN_ORG_ID"
upsert_env DOMAIN "$DOMAIN"
ok "Updated $ENV_FILE"

# Step 4: Optional Infisical write
if [ "$WITH_INFISICAL" = true ]; then
  step "Step 4: Write to local Infisical"
  warn "Infisical write not implemented in this build — use the wire-pocketid-pangolin-komodo.sh"
fi

# Step 5: Optional wire run
if [ "$SKIP_WIRE" != true ]; then
  step "Step 5: Run the wire script (dry-run first)"
  if [ -f "$WIRE_SCRIPT" ]; then
    local ARGS="--skip-komodo --dry-run --domain=$DOMAIN"
    log "Running: $WIRE_SCRIPT $ARGS"
    bash "$WIRE_SCRIPT" $ARGS 2>&1 | tail -10

    if [ "$NON_INTERACTIVE" != true ]; then
      read -r -p "  Run for real (not dry-run)? [y/N]: " CONFIRM
      if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
        log "Running for real..."
        bash "$WIRE_SCRIPT" --domain="$DOMAIN" 2>&1 | tail -10
      fi
    fi
  fi
fi

# Done
step "Done!"
log "Next steps:"
log "  1. Visit https://komodo.$DOMAIN (if Komodo is up)"
log "  2. Click 'Login with Pocket ID' - should work end-to-end"
log "  3. Re-run this wizard any time: $0"
