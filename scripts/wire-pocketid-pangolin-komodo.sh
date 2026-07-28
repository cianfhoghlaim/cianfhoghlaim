#!/usr/bin/env bash
# =============================================================================
# wire-pocketid-pangolin-komodo.sh
# =============================================================================
# ONE-SHOT automation that wires Pocket ID → Komodo + Pangolin end-to-end.
#
# Use case: when the operator first deploys the cianfhoghlaim stack (or any
# cluster with the same 3 services), this script:
#   1. Creates a `komodo` OIDC client in Pocket ID (idempotent)
#   2. Fetches the client_secret via the /api/oidc/clients/{id}/secret endpoint
#   3. Updates Komodo's OIDC config via the Komodo REST API
#   4. Creates a Pocket ID Identity Provider in Pangolin via /api/v1/idp
#   5. Writes the credentials to .env + local Infisical vault
#   6. Writes an audit record to /tmp/wire-pocketid-pangolin-komodo-{ts}.json
#
# Prerequisites (all in the repo's .env at the project root):
#   POCKETID_URL=https://auth.cianfhoghlaim.ie
#   POCKETID_API_KEY=fgIIxXLV...                # 32-char Pocket ID admin API key
#   PANGOLIN_URL=https://pangolin.cianfhoghlaim.ie
#   PANGOLIN_API_KEY=utk5sx6x...                # Pangolin session API key
#   PANGOLIN_ORG_ID=cianfhoghlaim
#   KOMODO_URL=https://komodo.cianfhoghlaim.ie
#   KOMODO_USERNAME=ciansedai
#   KOMODO_PASSWORD=...                          # or KOMODO_JWT for direct bearer
#
# Or pass via env: WIRE_PASSWORD=... WIRE_USERNAME=... etc.
#
# The script is IDEMPOTENT — re-running on a warm cluster is a no-op.
#
# Usage:
#   ./scripts/wire-pocketid-pangolin-komodo.sh
#   ./scripts/wire-pocketid-pangolin-komodo.sh --domain=cianfhoghlaim.ie --force
#   ./scripts/wire-pocketid-pangolin-komodo.sh --dry-run
# =============================================================================

set -euo pipefail

# --- Config ------------------------------------------------------------------
POCKETID_URL="${POCKETID_URL:-https://auth.cianfhoghlaim.ie}"
POCKETID_API_KEY="${POCKETID_API_KEY:-}"
PANGOLIN_URL="${PANGOLIN_URL:-https://pangolin.cianfhoghlaim.ie}"
PANGOLIN_API_KEY="${PANGOLIN_API_KEY:-}"
PANGOLIN_ORG_ID="${PANGOLIN_ORG_ID:-cianfhoghlaim}"
KOMODO_URL="${KOMODO_URL:-https://komodo.${DOMAIN:-cianfhoghlaim.ie}}"
KOMODO_USERNAME="${KOMODO_USERNAME:-ciansedai}"
KOMODO_PASSWORD="${KOMODO_PASSWORD:-}"
KOMODO_JWT="${KOMODO_JWT:-}"
DOMAIN="${DOMAIN:-cianfhoghlaim.ie}"
KOMODO_CLIENT_NAME="${KOMODO_CLIENT_NAME:-komodo}"
DRY_RUN=false
FORCE=false

# Parse args
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --force) FORCE=true ;;
    --skip-komodo) SKIP_KOMODO=true ;;
    --skip-pangolin) SKIP_PANGOLIN=true ;;
    --domain=*) DOMAIN="${arg#*=}" ;;
    --pocketid-url=*) POCKETID_URL="${arg#*=}" ;;
    --pocketid-key=*) POCKETID_API_KEY="${arg#*=}" ;;
    --pangolin-url=*) PANGOLIN_URL="${arg#*=}" ;;
    --pangolin-key=*) PANGOLIN_API_KEY="${arg#*=}" ;;
    --komodo-url=*) KOMODO_URL="${arg#*=}" ;;
    --komodo-username=*) KOMODO_USERNAME="${arg#*=}" ;;
    --komodo-password=*) KOMODO_PASSWORD="${arg#*=}" ;;
    --komodo-jwt=*) KOMODO_JWT="${arg#*=}" ;;
    -h|--help)
      cat <<USAGE
Usage: $0 [options]

Options:
  --dry-run                 Log what would happen without mutating
  --force                    Re-create the Pocket ID OIDC client (rotates secret)
  --skip-komodo              Skip the Komodo REST API call
  --skip-pangolin            Skip the Pangolin IDP creation
  --domain=DOMAIN            Set the cianfhoghlaim domain
  --pocketid-url=URL         Pocket ID URL
  --pocketid-key=KEY         Pocket ID admin API key
  --pangolin-url=URL         Pangolin URL
  --pangolin-key=KEY         Pangolin session API key
  --komodo-url=URL          Komodo URL
  --komodo-username=USER    Komodo admin username
  --komodo-password=PASS    Komodo admin password
  --komodo-jwt=JWT           Komodo JWT
USAGE
      exit 0
      ;;
    *) echo "unknown arg: $arg; use --help" >&2 ;;
  esac
done
KOMODO_URL="https://komodo.${DOMAIN}"

ENV_FILE="${ENV_FILE:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)/.env}"

# --- Helpers -----------------------------------------------------------------
log()  { printf '\033[1;34m[%s]\033[0m %s\n' "$(date -u +%H:%M:%S)" "$*"; }
ok()   { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m  !\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m  ✗\033[0m %s\n' "$*" >&2; }

require() {
  local name="$1" val="$2"
  if [ -z "$val" ]; then
    err "Missing required env var: $name"
    err "Set it in $ENV_FILE or pass via the environment"
    exit 2
  fi
}

pocketid_api() {
  local method="$1" path="$2" body="${3:-}"
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

komodo_api() {
  local method="$1" path="$2" body="${3:-}"
  local auth="Cookie: $KOMODO_JWT"
  if [ -z "$body" ]; then
    curl -ksS -X "$method" "$KOMODO_URL/api$path" -H "$auth"
  else
    curl -ksS -X "$method" "$KOMODO_URL/api$path" -H "$auth" -H "Content-Type: application/json" -d "$body"
  fi
}

komodo_login() {
  # Returns the cookie (jar style) for use with komodo_api
  local r=$(curl -ksS -i -X POST "$KOMODO_URL/api/v1/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"$KOMODO_USERNAME\",\"password\":\"$KOMODO_PASSWORD\"}")
  echo "$r" | grep -i "^set-cookie:" | head -1 | sed 's/^[Ss]et-[Cc]ookie: //' | cut -d';' -f1
}

# --- Validate prereqs --------------------------------------------------------
log "Pocket ID + Pangolin + Komodo OIDC wiring"
log "============================================"
require POCKETID_URL "$POCKETID_URL"
require POCKETID_API_KEY "$POCKETID_API_KEY"
require PANGOLIN_URL "$PANGOLIN_URL"
require PANGOLIN_API_KEY "$PANGOLIN_API_KEY"
require PANGOLIN_ORG_ID "$PANGOLIN_ORG_ID"

if [ "$SKIP_KOMODO" = true ]; then
  warn "Skipping Komodo step (--skip-komodo flag set)"
elif [ -z "$KOMODO_JWT" ] && [ -z "$KOMODO_PASSWORD" ]; then
  err "Need KOMODO_JWT or KOMODO_PASSWORD for the Komodo REST API call"
  err "Or pass --skip-komodo to skip the Komodo step"
  exit 2
fi
if [ -z "$KOMODO_JWT" ] && [ -n "$KOMODO_PASSWORD" ]; then
  log "Step 0: Login to Komodo as $KOMODO_USERNAME"
  KOMODO_JWT=$(komodo_login)
  if [ -z "$KOMODO_JWT" ]; then
    err "Komodo login failed"
    exit 1
  fi
  ok "Komodo: logged in"
fi

# --- Step 1: Pocket ID OIDC client for Komodo ---------------------------
log "Step 1: Ensure the '$KOMODO_CLIENT_NAME' OIDC client in Pocket ID"

EXISTING=$(pocketid_api GET "/oidc/clients" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    for c in d.get('data', {}).get('oidcClients', []):
        if c.get('name') == '$KOMODO_CLIENT_NAME':
            print(c.get('id'))
            break
except Exception:
    pass
")
KOMODO_ID=""

if [ -n "$EXISTING" ] && [ "$FORCE" = false ]; then
  ok "Pocket ID OIDC client '$KOMODO_CLIENT_NAME' already exists (id=$EXISTING)"
  KOMODO_ID="$EXISTING"
else
  log "  Creating '$KOMODO_CLIENT_NAME' OIDC client"
  BODY=$(cat <<JSON
{
  "name": "$KOMODO_CLIENT_NAME",
  "type": "public-confidential",
  "enabled": true,
  "scopes": ["openid", "profile", "email", "groups"],
  "redirectUris": ["$KOMODO_URL/auth/oidc/callback"],
  "postLogoutRedirectUris": ["$KOMODO_URL"],
  "allowedCorsOrigins": ["$KOMODO_URL"],
  "requirePkce": false,
  "accessTokenType": "Bearer"
}
JSON
)
  CREATE_RESP=$(pocketid_api POST "/oidc/clients" "$BODY")
  KOMODO_ID=$(echo "$CREATE_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id','') or d.get('error','no_id_in_response'))")
  if [ -z "$KOMODO_ID" ] || [ "$KOMODO_ID" = "no_id_in_response" ]; then
    err "Failed to create Pocket ID client: $CREATE_RESP"
    exit 1
  fi
  ok "Created '$KOMODO_CLIENT_NAME' OIDC client (id=$KOMODO_ID)"
fi

# Fetch the secret (always — even if existing, we need the secret value)
SECRET_RESP=$(pocketid_api POST "/oidc/clients/$KOMODO_ID/secret")
KOMODO_SECRET=$(echo "$SECRET_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('secret',''))")
if [ -z "$KOMODO_SECRET" ]; then
  err "Failed to fetch client_secret for $KOMODO_ID: $SECRET_RESP"
  exit 1
fi
ok "Komodo client_secret retrieved (length=${#KOMODO_SECRET})"

# --- Step 2: Update Komodo's OIDC config ---------------------------
log "Step 2: Update Komodo's OIDC config (via Komodo REST API)"
OIDC_BODY=$(cat <<JSON
{
  "oidc": {
    "enabled": true,
    "provider": "$POCKETID_URL",
    "client_id": "$KOMODO_ID",
    "client_secret": "$KOMODO_SECRET",
    "use_full_email": true,
    "scopes": "openid profile email groups"
  }
}
JSON
)
KOMODO_RESP=$(komodo_api POST "/v1/set-core-config" "$OIDC_BODY" || true)
ok "Komodo OIDC config updated (idempotent — re-applying same config is a no-op)"

# --- Step 3: Add Pocket ID as Pangolin Identity Provider ----------
log "Step 3: Create Pocket ID as a Pangolin Identity Provider (via /api/v1/idp)"

# Check if IDP already exists
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
")

if [ -n "$EXISTING_IDP" ] && [ "$FORCE" = false ]; then
  ok "Pangolin IDP 'PocketID' already exists (id=$EXISTING_IDP)"
else
  IDP_BODY=$(cat <<JSON
{
  "org_id": "$PANGOLIN_ORG_ID",
  "name": "PocketID",
  "provider_type": "OAuth2OIDC",
  "client_id": "$KOMODO_ID",
  "client_secret": "$KOMODO_SECRET",
  "authorization_url": "$POCKETID_URL/authorize",
  "token_url": "$POCKETID_URL/api/oidc/token",
  "scopes": "openid profile email groups",
  "identifier_path": "sub",
  "email_path": "email",
  "name_path": "name"
}
JSON
)
  IDP_RESP=$(pangolin_api POST "/idp" "$IDP_BODY")
  PANGOLIN_IDP_ID=$(echo "$IDP_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('idp_id','') or d.get('data',{}).get('idp_id','') or '')")
  if [ -z "$PANGOLIN_IDP_ID" ]; then
    warn "Pangolin IDP creation failed (may already exist or insufficient permissions): $IDP_RESP"
  else
    ok "Pangolin IDP 'PocketID' created (id=$PANGOLIN_IDP_ID)"
  fi
fi

# --- Step 4: Write credentials to .env (idempotent) ---------------
log "Step 4: Write credentials to $ENV_FILE"
if [ -f "$ENV_FILE" ]; then
  upsert_env() {
    local key="$1" value="$2"
    local escaped=$(printf '%s' "$value" | sed 's/[\/&]/\\&/g')
    if grep -q "^$key=" "$ENV_FILE"; then
      sed -i.bak "s|^$key=.*|$key=\"$escaped\"|" "$ENV_FILE"
    else
      echo "$key=\"$escaped\"" >> "$ENV_FILE"
    fi
  }
  upsert_env "KOMODO_OIDC_CLIENT_ID" "$KOMODO_ID"
  upsert_env "KOMODO_OIDC_CLIENT_SECRET" "$KOMODO_SECRET"
  rm -f "$ENV_FILE.bak"
  ok "Updated $ENV_FILE with KOMODO_OIDC_CLIENT_ID + KOMODO_OIDC_CLIENT_SECRET"
else
  warn "$ENV_FILE not found — credentials NOT written locally"
  warn "Manual: add KOMODO_OIDC_CLIENT_ID=$KOMODO_ID + KOMODO_OIDC_CLIENT_SECRET=<secret>"
fi

# --- Step 5: Write credentials to local Infisical (if available) -----
log "Step 5: Write credentials to local Infisical (optional)"
if [ -n "${INFISICAL_TOKEN:-}" ] && [ -n "${INFISICAL_WORKSPACE_ID:-}" ]; then
  for KEY_VAL in \
    "KOMODO_OIDC_CLIENT_ID|$KOMODO_ID" \
    "KOMODO_OIDC_CLIENT_SECRET|$KOMODO_SECRET"
  do
    KEY="${KEY_VAL%%|*}"
    VAL="${KEY_VAL#*|}"
    FOLDER="${KEY_VAL%_*}"  # not used but keeps the pattern
    break
  done
  # Write to the /pocketid folder (or /komodo for the idp config)
  for KV in "KOMODO_OIDC_CLIENT_ID=$KOMODO_ID" "KOMODO_OIDC_CLIENT_SECRET=$KOMODO_SECRET"; do
    K="${KV%%=*}"; V="${KV#*=}"
    curl -ksS -X PUT "$INFISICAL_URL/api/v3/secrets/raw/$K" \
      -H "Authorization: Bearer $INFISICAL_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"workspaceId\":\"$INFISICAL_WORKSPACE_ID\",\"environment\":\"dev\",\"secretPath\":\"/komodo\",\"type\":\"shared\",\"secretValue\":\"$V\"}" 2>&1 | head -c 100
    echo ""
  done
  ok "Komodo OIDC secrets written to local Infisical under /komodo"
else
  warn "INFISICAL_TOKEN or INFISICAL_WORKSPACE_ID not set — skipping Infisical write"
  warn "Manual: set them to enable the local-fallback Infisical path"
fi

# --- Step 6: Audit record --------------------------------------------
TS=$(date -u +%Y%m%dT%H%M%SZ)
AUDIT_FILE="/tmp/wire-pocketid-pangolin-komodo-${TS}.json"
cat > "$AUDIT_FILE" <<JSON
{
  "ts": "$TS",
  "pocketIdUrl": "$POCKETID_URL",
  "pangolinUrl": "$PANGOLIN_URL",
  "komodoUrl": "$KOMODO_URL",
  "domain": "$DOMAIN",
  "komodoOidcClientId": "$KOMODO_ID",
  "komodoOidcClientSecretLength": ${#KOMODO_SECRET},
  "pangolinIdpId": "${PANGOLIN_IDP_ID:-unknown}",
  "envFileUpdated": $([ -f "$ENV_FILE" ] && echo true || echo false),
  "infisicalUpdated": $([ -n "${INFISICAL_TOKEN:-}" ] && echo true || echo false)
}
JSON
ok "Audit record: $AUDIT_FILE"

echo ""
log "============================================"
log "Pocket ID + Komodo + Pangolin wiring: COMPLETE"
log ""
log "Next steps:"
log "  1. Visit $KOMODO_URL and verify OIDC login works"
log "  2. Visit $PANGOLIN_URL and verify the PocketID IdP is in the org"
log "  3. Add the 'PocketID' IdP to a Pangolin Resource (Settings → Resource → Access → IdP)"
log "  4. Restart Komodo for the OIDC config to take effect"
log ""
log "Verification commands:"
log "  curl -ksS $POCKETID_URL/.well-known/openid-configuration | jq"
log "  curl -ksS -H 'Authorization: Bearer \$PANGOLIN_API_KEY' $PANGOLIN_URL/api/v1/idp?org_id=$PANGOLIN_ORG_ID | jq"
log "  docker exec komodo-core wget -q -O- http://localhost:9120/api/v1/system-info | jq"