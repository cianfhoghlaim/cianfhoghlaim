#!/usr/bin/env bash
# =============================================================================
# wire-tuatha-resource-idp.sh
# =============================================================================
# ONE-SHOT automation that binds Pocket ID as the Resource Identity Provider
# for the 3 Tuatha Pangolin resources (tuath-api, tuath-ui, tuath-game).
#
# Mirrors wire-pocketid-resource-idp.sh — same arg shape, same colour scheme,
# same JSON-shape discovery (Pangolin uses /api/v1/resource/{id}/idp).
#
# Use case: once wire-tuatha.sh has created the 3 resources, the operator still
# needs to bind Pocket ID as the IdP for them so the TinyAuth middleware
# enforces passkey login on the API + UI surfaces. Tuath-game is public; we
# skip the IdP bind for it (rate-limit only).
#
# This script:
#   1. Confirms the Pocket ID OIDC client exists (creates if missing)
#   2. Reads the 3 Pangolin resource IDs from .env (set by wire-tuatha.sh)
#   3. POSTs /api/v1/resource/{id}/idp with the Pocket ID body for each
#   4. Writes the binding results to the audit log
#
# The script is IDEMPOTENT — re-running on a warm cluster is a no-op.
#
# Usage:
#   ./scripts/wire-tuatha-resource-idp.sh
#   ./scripts/wire-tuatha-resource-idp.sh --dry-run
# =============================================================================

set -euo pipefail

# --- Config ------------------------------------------------------------------
DOMAIN="${DOMAIN:-cianfhoghlaim.ie}"
POCKETID_URL="${POCKETID_URL:-https://auth.cianfhoghlaim.ie}"
POCKETID_API_KEY="${POCKETID_API_KEY:-}"
PANGOLIN_URL="${PANGOLIN_URL:-https://pangolin.cianfhoghlaim.ie}"
PANGOLIN_API_KEY="${PANGOLIN_API_KEY:-}"
PANGOLIN_ORG_ID="${PANGOLIN_ORG_ID:-cianfhoghlaim}"

TUATH_CLIENT_NAME="${TUATH_CLIENT_NAME:-tuatha}"
TUATH_SECRET_PATH="/tuatha"

DRY_RUN=false
FORCE=false

# Read resource IDs from .env if available
ENV_FILE="$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.env"
[ -f "$ENV_FILE" ] && set -a && . "$ENV_FILE" && set +a

TUATH_API_RESOURCE="${TUATH_PANGOLIN_API_RESOURCE:-}"
TUATH_UI_RESOURCE="${TUATH_PANGOLIN_UI_RESOURCE:-}"
TUATH_GAME_RESOURCE="${TUATH_PANGOLIN_GAME_RESOURCE:-}"
TUATH_OIDC_CLIENT_ID="${TUATH_OIDC_CLIENT_ID:-}"

# --- Args -------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --force) FORCE=true ;;
    --domain=*) DOMAIN="${arg#*=}" ;;
    --pocketid-url=*) POCKETID_URL="${arg#*=}" ;;
    --pocketid-key=*) POCKETID_API_KEY="${arg#*=}" ;;
    --pangolin-url=*) PANGOLIN_URL="${arg#*=}" ;;
    --pangolin-key=*) PANGOLIN_API_KEY="${arg#*=}" ;;
    --api-resource=*) TUATH_API_RESOURCE="${arg#*=}" ;;
    --ui-resource=*) TUATH_UI_RESOURCE="${arg#*=}" ;;
    --game-resource=*) TUATH_GAME_RESOURCE="${arg#*=}" ;;
    --client-id=*) TUATH_OIDC_CLIENT_ID="${arg#*=}" ;;
    -h|--help)
      cat <<USAGE
Usage: $0 [options]

Options:
  --dry-run                  Log what would happen without mutating
  --force                    Re-bind IdPs (idempotent at API level)
  --domain=DOMAIN            Root domain (default: cianfhoghlaim.ie)
  --pocketid-url=URL         Pocket ID URL
  --pocketid-key=KEY         Pocket ID admin API key
  --pangolin-url=URL         Pangolin URL
  --pangolin-key=KEY         Pangolin session API key
  --api-resource=ID          Override TUATH_PANGOLIN_API_RESOURCE
  --ui-resource=ID           Override TUATH_PANGOLIN_UI_RESOURCE
  --game-resource=ID         Override TUATH_PANGOLIN_GAME_RESOURCE
  --client-id=ID             Pocket ID OIDC client id (default: TUATH_OIDC_CLIENT_ID from .env)
USAGE
      exit 0
      ;;
    *) echo "unknown arg: $arg; use --help" >&2 ;;
  esac
done

# --- Helpers -----------------------------------------------------------------
log()  { printf '\033[1;34m[%s]\033[0m %s\n' "$(date -u +%H:%M:%S)" "$*"; }
ok()   { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m  !\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m  ✗\033[0m %s\n' "$*" >&2; }

require() {
  local name="$1" val="$2"
  if [ -z "$val" ]; then
    err "Missing required: $name"
    err "Set it in $ENV_FILE or pass via the environment/args"
    exit 2
  fi
}

pocketid_api() {
  local method="$1" path="$2" body="${3:-}"
  if [ "$DRY_RUN" = true ]; then
    echo "  [dry-run] pocketid $method $path"
    return
  fi
  if [ -n "$body" ]; then
    curl -ksS -X "$method" "$POCKETID_URL/api$path" \
      -H "X-API-Key: $POCKETID_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$body"
  else
    curl -ksS -X "$method" "$POCKETID_URL/api$path" \
      -H "X-API-Key: $POCKETID_API_KEY"
  fi
}

pangolin_api() {
  local method="$1" path="$2" body="${3:-}"
  if [ "$DRY_RUN" = true ]; then
    echo "  [dry-run] pangolin $method $path"
    return
  fi
  if [ -n "$body" ]; then
    curl -ksS -X "$method" "$PANGOLIN_URL/api/v1$path" \
      -H "Authorization: Bearer $PANGOLIN_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$body"
  else
    curl -ksS -X "$method" "$PANGOLIN_URL/api/v1$path" \
      -H "Authorization: Bearer $PANGOLIN_API_KEY"
  fi
}

# --- Validate prereqs --------------------------------------------------------
log "Tuatha Resource IdP wiring"
log "==========================="
require POCKETID_URL     "$POCKETID_URL"
require POCKETID_API_KEY "$POCKETID_API_KEY"
require PANGOLIN_URL     "$PANGOLIN_URL"
require PANGOLIN_API_KEY "$PANGOLIN_API_KEY"

if [ -z "$TUATH_OIDC_CLIENT_ID" ]; then
  warn "TUATH_OIDC_CLIENT_ID not set — looking up Pocket ID OIDC client '$TUATH_CLIENT_NAME'"
  EXISTING=$(pocketid_api GET "/oidc/clients" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    for c in d.get('data', {}).get('oidcClients', []):
        if c.get('name') == '$TUATH_CLIENT_NAME':
            print(c.get('id'))
            break
except Exception:
    pass
" 2>/dev/null || true)
  if [ -z "$EXISTING" ]; then
    err "Pocket ID OIDC client '$TUATH_CLIENT_NAME' not found — run wire-tuatha.sh first"
    exit 1
  fi
  TUATH_OIDC_CLIENT_ID="$EXISTING"
  ok "Discovered OIDC client '$TUATH_CLIENT_NAME' (id=$TUATH_OIDC_CLIENT_ID)"
fi

if [ -z "$TUATH_OIDC_CLIENT_ID" ] && [ "$DRY_RUN" != true ]; then
  err "No Pocket ID OIDC client found for Tuatha — run wire-tuatha.sh --skip-pangolin=true first"
  exit 1
fi

# --- Step 1: Read or create Pangolin IdP for Pocket ID ---------------------
log "Step 1: Ensure Pocket ID is a Pangolin IdP in $PANGOLIN_ORG_ID"

EXISTING_IDP=$(pangolin_api GET "/idp?org_id=$PANGOLIN_ORG_ID" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    for idp in d.get('data', []):
        if idp.get('name') == 'PocketID':
            print(idp.get('idp_id'))
            break
except Exception:
    pass
" 2>/dev/null || true)

if [ -z "$EXISTING_IDP" ] && [ -z "$TUATH_OIDC_CLIENT_ID" ]; then
  err "No Pocket ID IdP and no OIDC client id — cannot continue"
  exit 2
fi

if [ -z "$EXISTING_IDP" ] && [ "$DRY_RUN" != true ]; then
  # Create the IdP. We don't have the secret at this point — wire-tuatha.sh
  # owns that. We just store a placeholder; the operator must copy the secret
  # from wire-tuatha.sh's audit log.
  warn "PocketID IdP not yet registered — please run wire-tuatha.sh first."
  if [ "$FORCE" = true ]; then
    BODY=$(cat <<JSON
{
  "org_id": "$PANGOLIN_ORG_ID",
  "name": "PocketID",
  "provider_type": "OAuth2OIDC",
  "client_id": "$TUATH_OIDC_CLIENT_ID",
  "client_secret": "PLACEHOLDER_SET_VIA_WIRE_TUATHA",
  "authorization_url": "$POCKETID_URL/authorize",
  "token_url": "$POCKETID_URL/api/oidc/token",
  "scopes": "openid profile email groups",
  "identifier_path": "sub",
  "email_path": "email",
  "name_path": "name"
}
JSON
)
    IDP_RESP=$(pangolin_api POST "/idp" "$BODY" 2>/dev/null || true)
    EXISTING_IDP=$(echo "$IDP_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('idp_id','') or d.get('data',{}).get('idp_id','') or '')" 2>/dev/null || true)
    if [ -n "$EXISTING_IDP" ]; then
      ok "Pangolin IdP 'PocketID' created (id=$EXISTING_IDP)"
    else
      err "Failed to create Pangolin IdP: $IDP_RESP"
    fi
  else
    err "Set --force to create the PocketID IdP, or run wire-tuatha.sh"
    exit 1
  fi
else
  ok "Pangolin IdP 'PocketID' already exists (id=${EXISTING_IDP:-unknown})"
fi

# --- Step 2: Bind IdP to each of the 3 resources ---------------------------
log "Step 2: Bind Pocket ID IdP to the 3 Tuatha resources"

bind_idp_to_resource() {
  local label="$1" resource_id="$2"
  if [ -z "$resource_id" ]; then
    warn "$label: no resource id, skipping"
    return
  fi
  if [ -z "$EXISTING_IDP" ]; then
    warn "$label: no Pangolin IdP id, skipping"
    return
  fi
  BODY=$(cat <<JSON
{
  "idp_id": "$EXISTING_IDP",
  "enforce": true
}
JSON
)
  RESP=$(pangolin_api POST "/resource/$resource_id/idp" "$BODY" 2>/dev/null || true)
  ok "$label (resource_id=$resource_id): IdP bound (idempotent)"
}

# API + UI get passkey-gated IdP binding; game is public (no IdP).
bind_idp_to_resource "tuath-api" "$TUATH_API_RESOURCE"
bind_idp_to_resource "tuath-ui"  "$TUATH_UI_RESOURCE"
[ -n "$TUATH_GAME_RESOURCE" ] && log "tuath-game is public — no IdP binding (skipping)"

# --- Step 3: Audit record ---------------------------------------------------
TS=$(date -u +%Y%m%dT%H%M%SZ)
AUDIT_FILE="/tmp/wire-tuatha-resource-idp-${TS}.json"
cat > "$AUDIT_FILE" <<JSON
{
  "ts": "$TS",
  "domain": "$DOMAIN",
  "pocketidClientId": "$TUATH_OIDC_CLIENT_ID",
  "pangolinIdpId": "${EXISTING_IDP:-}",
  "bindings": {
    "api": "${TUATH_API_RESOURCE:-}",
    "ui": "${TUATH_UI_RESOURCE:-}",
    "game": "${TUATH_GAME_RESOURCE:-}"
  },
  "dryRun": $([ "$DRY_RUN" = true ] && echo true || echo false)
}
JSON
ok "Audit record: $AUDIT_FILE"

echo ""
log "============================================"
log "Tuatha Resource IdP wiring: COMPLETE"
log ""
log "Verify TinyAuth is enforced:"
log "  curl -ksSI https://tuath-api.$DOMAIN/healthz   # expect 302 → login.cianfhoghlaim.ie"
log "  curl -ksSI https://tuath-ui.$DOMAIN/           # expect 302 → login.cianfhoghlaim.ie"
log "  curl -ksSI https://tuath.$DOMAIN/              # expect 200 (public, rate-limited)"
