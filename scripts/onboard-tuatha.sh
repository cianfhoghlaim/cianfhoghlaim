#!/usr/bin/env bash
# =============================================================================
# onboard-tuatha.sh
# =============================================================================
# Guided wizard for non-technical Tuatha onboarding.
# Mirrors onboard-pocketid.sh — collect credentials + write to .env +
# optionally run wire-tuatha.sh. Same colour scheme, same arg shape.
#
# Use case: when a new operator first deploys the Tuatha stack (api/ui/game +
# SpacetimeDB + Langfuse + Locket-sidecar) on bunchloch, this wizard collects
# the 6 secrets and writes them to the project .env so the next phase
# (wire-tuatha.sh) can succeed without re-asking.
#
# Prerequisites in the repo's .env at project root (auto-loaded by mise):
#   POCKETID_URL=https://auth.cianfhoghlaim.ie        (for TinyAuth OIDC login)
#   POCKETID_API_KEY=...
#   PANGOLIN_URL=https://pangolin.cianfhoghlaim.ie
#   PANGOLIN_API_KEY=...
#   INFISICAL_URL=https://infisical.cianfhoghlaim.ie
#   INFISICAL_CLIENT_ID=...
#   INFISICAL_CLIENT_SECRET=...
#   KOMODO_URL=https://komodo.cianfhoghlaim.ie         (for the stack deploy)
#   KOMODO_API_KEY=...
#
# Usage:
#   ./scripts/onboard-tuatha.sh
#   ./scripts/onboard-tuatha.sh --non-interactive    (CI path; reads .env)
#   ./scripts/onboard-tuatha.sh --skip-wire          (just write .env)
# =============================================================================

set -euo pipefail

log()  { printf '\033[1;34m[%s]\033[0m %s\n' "$(date -u +%H:%M:%S)" "$*"; }
ok()   { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m  !\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m  ✗\033[0m %s\n' "$*"; }
step() { printf '\n\033[1;36m=== %s ===\033[0m\n' "$*"; }

NON_INTERACTIVE=false
SKIP_WIRE=false
WITH_INFISICAL=true
DOMAIN="cianfhoghlaim.ie"
ENV_FILE="$(git rev-parse --show-toplevel)/.env"
WIRE_SCRIPT="$(git rev-parse --show-toplevel)/scripts/wire-tuatha.sh"

usage() {
  cat <<USAGE
Usage: $0 [options]

Options:
  --non-interactive        Use values from .env (for CI / non-TTY)
  --skip-wire              Don't run the wire script (just write to .env)
  --no-infisical           Skip the Infisical-write step (write to .env only)
  --domain=DOMAIN          Root domain (default: cianfhoghlaim.ie)
  -h, --help               Show this help
USAGE
  exit 0
}

for arg in "$@"; do
  case "$arg" in
    --non-interactive) NON_INTERACTIVE=true ;;
    --skip-wire) SKIP_WIRE=true ;;
    --no-infisical) WITH_INFISICAL=false ;;
    --domain=*) DOMAIN="${arg#*=}" ;;
    -h|--help) usage ;;
    *) err "unknown arg: $arg; use --help for usage"; exit 2 ;;
  esac
done

echo
log "Tuatha + Pangolin + Komodo + Infisical Onboarding Wizard"
log "======================================================="
log "  This wizard helps non-technical operators wire"
log "  the Tuatha educational MMO stack to:"
log "    - Pocket ID     (OIDC identity for TinyAuth middleware)"
log "    - Pangolin      (proxy + 3 named public routes)"
log "    - Komodo        (orchestrator: deploy tuatha stack)"
log "    - Infisical     (secrets — TUATH_* keys under /tuatha folder)"
log "    - Locket sidecar (injects secrets into api/ui/game containers)"

# --- Step 1: Collect credentials -------------------------------------------
step "Step 1: Collect credentials"

prompt() {
  local var="$1" label="$2" default="$3" secure="${4:-false}"
  local current="${!var:-}"
  if [ -n "$current" ]; then default="$current"; fi
  if [ "$NON_INTERACTIVE" = true ]; then eval "$var=\"\$default\""; return; fi
  local value=""
  while [ -z "$value" ]; do
    if [ "$secure" = "true" ]; then
      read -r -s -p "  $label [$(echo "$default" | head -c 4)***]: " value; echo
    else
      read -r -p "  $label [$default]: " value
    fi
    [ -z "$value" ] && value="$default"
  done
  eval "$var=\"\$value\""
}

if [ "$NON_INTERACTIVE" != true ]; then
  cat <<'PROMPT'
  You need ~5 credentials. Where to get each:
    1. POCKETID_API_KEY:   https://auth.cianfhoghlaim.ie → Settings → API Keys
    2. PANGOLIN_API_KEY:   https://pangolin.cianfhoghlaim.ie → Settings → API Keys
    3. INFISICAL_CLIENT_ID / SECRET: deployed with the project Infisical stack
    4. KOMODO_API_KEY:     https://komodo.cianfhoghlaim.ie → Settings → API Keys
    5. OPENAI_API_KEY:     from your OpenAI account dashboard (for the NPC LLM)

PROMPT
fi

prompt POCKETID_URL     "Pocket ID URL"                "https://auth.cianfhoghlaim.ie"
prompt POCKETID_API_KEY "Pocket ID admin API key"     "" true
prompt PANGOLIN_URL     "Pangolin URL"                "https://pangolin.cianfhoghlaim.ie"
prompt PANGOLIN_API_KEY "Pangolin API key"            "" true
prompt PANGOLIN_ORG_ID  "Pangolin org_id"             "cianfhoghlaim"
prompt KOMODO_URL       "Komodo URL"                  "https://komodo.$DOMAIN"
prompt KOMODO_API_KEY   "Komodo API key"              "" true
prompt INFISICAL_URL    "Infisical URL"               "https://infisical.cianfhoghlaim.ie"
prompt INFISICAL_CLIENT_ID "Infisical client ID"      "" true
prompt INFISICAL_CLIENT_SECRET "Infisical client secret" "" true
prompt OPENAI_API_KEY   "OpenAI API key (NPC LLM)"    "" true
prompt ANTHROPIC_API_KEY "Anthropic API key (optional)" "" true
prompt DOMAIN           "Root domain"                 "$DOMAIN"

# --- Step 2: Validate credentials -----------------------------------------
step "Step 2: Validate credentials (live API probes)"

validate() {
  local name="$1" url="$2" auth_header="$3" auth_value="$4"
  local probe=$(curl -ksS -m 5 -H "$auth_header: $auth_value" "$url" 2>/dev/null || true)
  if [ -n "$probe" ] && ! echo "$probe" | grep -qi "error\|fail\|unauthor"; then
    ok "$name: reachable"
  else
    warn "$name: NOT reachable (will retry at wire time)"
  fi
}

[ -n "$POCKETID_API_KEY" ] && validate "Pocket ID" "$POCKETID_URL/api/admin/me" "X-API-Key" "$POCKETID_API_KEY"
[ -n "$PANGOLIN_API_KEY" ] && validate "Pangolin" "$PANGOLIN_URL/api/v1/orgs" "Authorization" "Bearer $PANGOLIN_API_KEY"
[ -n "$KOMODO_API_KEY" ] && validate "Komodo" "$KOMODO_URL/api/v1/system-info" "X-API-KEY" "$KOMODO_API_KEY"

# --- Step 3: Write to .env ------------------------------------------------
step "Step 3: Write credentials to $ENV_FILE"

upsert_env() {
  local key="$1" value="$2"
  [ -z "$value" ] && return
  local escaped=$(printf '%s' "$value" | sed 's/[\/&]/\\&/g')
  if grep -q "^$key=" "$ENV_FILE" 2>/dev/null; then
    sed -i.bak "s|^$key=.*|$key=\"$escaped\"|" "$ENV_FILE" 2>/dev/null
  else
    echo "$key=\"$escaped\"" >> "$ENV_FILE"
  fi
}

touch "$ENV_FILE"
upsert_env POCKETID_URL                "$POCKETID_URL"
upsert_env POCKETID_API_KEY            "$POCKETID_API_KEY"
upsert_env PANGOLIN_URL                "$PANGOLIN_URL"
upsert_env PANGOLIN_API_KEY            "$PANGOLIN_API_KEY"
upsert_env PANGOLIN_ORG_ID             "$PANGOLIN_ORG_ID"
upsert_env KOMODO_URL                  "$KOMODO_URL"
upsert_env KOMODO_API_KEY              "$KOMODO_API_KEY"
upsert_env INFISICAL_URL               "$INFISICAL_URL"
upsert_env INFISICAL_CLIENT_ID         "$INFISICAL_CLIENT_ID"
upsert_env INFISICAL_CLIENT_SECRET     "$INFISICAL_CLIENT_SECRET"
upsert_env OPENAI_API_KEY              "$OPENAI_API_KEY"
upsert_env ANTHROPIC_API_KEY           "$ANTHROPIC_API_KEY"
upsert_env DOMAIN                      "$DOMAIN"
rm -f "$ENV_FILE.bak"
ok "Updated $ENV_FILE with 12 TUATH_* + control-plane keys"

# --- Step 4: Run wire (dry-run + optional confirm) -----------------------
if [ "$SKIP_WIRE" != true ]; then
  step "Step 4: Run the wire script (dry-run first)"
  if [ -f "$WIRE_SCRIPT" ]; then
    local ARGS="--dry-run --domain=$DOMAIN"
    log "Running: $WIRE_SCRIPT $ARGS"
    bash "$WIRE_SCRIPT" $ARGS 2>&1 | tail -10

    if [ "$NON_INTERACTIVE" != true ]; then
      read -r -p "  Run for real (not dry-run)? [y/N]: " CONFIRM
      if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
        log "Running for real..."
        bash "$WIRE_SCRIPT" --domain="$DOMAIN" 2>&1 | tail -10
      fi
    fi
  else
    warn "Wire script not found at $WIRE_SCRIPT — skipping"
  fi
fi

# --- Done ---------------------------------------------------------------
step "Done!"
log "Next steps:"
log "  1. Visit https://komodo.$DOMAIN and deploy the 'tuatha' stack"
log "  2. Visit https://tuath.cianfhoghlaim.ie (game) and https://tuath-api.cianfhoghlaim.ie (API)"
log "  3. Visit https://tuath-ui.cianfhoghlaim.ie (dashboard, TinyAuth passkey required)"
log "  4. Re-run this wizard any time: $0"
log ""
log "Rotate secrets on a 90-day cron (installs to /etc/cron.d):"
log "    ./scripts/rotate-tuatha-secrets.sh --install-cron"
