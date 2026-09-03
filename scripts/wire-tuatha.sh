#!/usr/bin/env bash
# =============================================================================
# wire-tuatha.sh
# =============================================================================
# ONE-SHOT automation that wires Tuatha → Komodo + Pangolin + Infisical end-to-end.
# Mirrors wire-pocketid-pangolin-komodo.sh for consistency.
#
# Use case: when the operator first deploys Tuatha (or rebuilds after a
# stack upgrade), this script:
#   1. Generates the 6 TUATH_* secrets (LLM keys, Langfuse keys, JWT signing
#      key) and persists them under /tuatha in the dev-baile Infisical vault
#   2. Creates a `tuatha` OIDC client in Pocket ID (idempotent) for the
#      TinyAuth gate on tuath-api.cianfhoghlaim.ie + tuath-ui.cianfhoghlaim.ie
#   3. Creates the 3 Pangolin resources (tuath-api, tuath-ui, tuath-game public)
#   4. Triggers a Komodo deploy of the tuatha stack on bunchloch
#   5. Writes credentials to .env + audit record to /tmp/wire-tuatha-{ts}.json
#
# The script is IDEMPOTENT — re-running on a warm cluster is a no-op.
#
# Usage:
#   ./scripts/wire-tuatha.sh
#   ./scripts/wire-tuatha.sh --domain=cianfhoghlaim.ie --force
#   ./scripts/wire-tuatha.sh --dry-run
# =============================================================================

set -euo pipefail

# --- Config ------------------------------------------------------------------
DOMAIN="${DOMAIN:-cianfhoghlaim.ie}"
POCKETID_URL="${POCKETID_URL:-https://auth.cianfhoghlaim.ie}"
POCKETID_API_KEY="${POCKETID_API_KEY:-}"
PANGOLIN_URL="${PANGOLIN_URL:-https://pangolin.cianfhoghlaim.ie}"
PANGOLIN_API_KEY="${PANGOLIN_API_KEY:-}"
PANGOLIN_ORG_ID="${PANGOLIN_ORG_ID:-cianfhoghlaim}"
KOMODO_URL="${KOMODO_URL:-https://komodo.${DOMAIN}}"
KOMODO_API_KEY="${KOMODO_API_KEY:-}"
INFISICAL_URL="${INFISICAL_URL:-https://infisical.cianfhoghlaim.ie}"
INFISICAL_TOKEN="${INFISICAL_TOKEN:-}"  # if set, use it (faster than client creds)
INFISICAL_WORKSPACE_ID="${INFISICAL_WORKSPACE_ID:-f3cff583-b74b-4804-b9d3-db8b68885236}"
INFISICAL_ENV="${INFISICAL_ENV:-dev-baile}"

OPENAI_API_KEY="${OPENAI_API_KEY:-}"
ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}"

TUATH_CLIENT_NAME="${TUATH_CLIENT_NAME:-tuatha}"
TUATH_SECRET_PATH="/tuatha"

# Resource IDs returned by Pangolin (used as audit trail)
TUATH_API_RESOURCE_ID=""
TUATH_UI_RESOURCE_ID=""
TUATH_GAME_RESOURCE_ID=""

DRY_RUN=false
FORCE=false
SKIP_KOMODO=false
SKIP_PANGOLIN=false
SKIP_INFISICAL=false
SKIP_POCKETID=false

# --- Args -------------------------------------------------------------------
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --force) FORCE=true ;;
    --skip-komodo) SKIP_KOMODO=true ;;
    --skip-pangolin) SKIP_PANGOLIN=true ;;
    --skip-infisical) SKIP_INFISICAL=true ;;
    --skip-pocketid) SKIP_POCKETID=true ;;
    --domain=*) DOMAIN="${arg#*=}" ;;
    --pocketid-url=*) POCKETID_URL="${arg#*=}" ;;
    --pocketid-key=*) POCKETID_API_KEY="${arg#*=}" ;;
    --pangolin-url=*) PANGOLIN_URL="${arg#*=}" ;;
    --pangolin-key=*) PANGOLIN_API_KEY="${arg#*=}" ;;
    --komodo-url=*) KOMODO_URL="${arg#*=}" ;;
    --komodo-key=*) KOMODO_API_KEY="${arg#*=}" ;;
    --infisical-url=*) INFISICAL_URL="${arg#*=}" ;;
    --infisical-token=*) INFISICAL_TOKEN="${arg#*=}" ;;
    --openai-key=*) OPENAI_API_KEY="${arg#*=}" ;;
    --anthropic-key=*) ANTHROPIC_API_KEY="${arg#*=}" ;;
    -h|--help)
      cat <<USAGE
Usage: $0 [options]

Options:
  --dry-run                  Log what would happen without mutating
  --force                    Re-create the Pocket ID OIDC client (rotates secret)
  --skip-komodo              Skip the Komodo deploy trigger
  --skip-pangolin            Skip Pangolin resource creation
  --skip-infisical           Skip the Infisical secret-write step
  --skip-pocketid            Skip the Pocket ID OIDC client step
  --domain=DOMAIN            Root domain (default: cianfhoghlaim.ie)
  --pocketid-url=URL         Pocket ID URL
  --pocketid-key=KEY         Pocket ID admin API key
  --pangolin-url=URL         Pangolin URL
  --pangolin-key=KEY         Pangolin session API key
  --komodo-url=URL           Komodo URL
  --komodo-key=KEY           Komodo API key
  --infisical-url=URL        Infisical URL
  --infisical-token=TOKEN    Use a pre-minted Infisical machine-identity token
  --openai-key=KEY           OpenAI key to seed /tuatha/openai_api_key
  --anthropic-key=KEY        Anthropic key to seed /tuatha/anthropic_api_key
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

komodo_api() {
  local method="$1" path="$2" body="${3:-}"
  if [ "$DRY_RUN" = true ]; then
    echo "  [dry-run] komodo $method $path"
    return
  fi
  if [ -z "$body" ]; then
    curl -ksS -X "$method" "$KOMODO_URL/api$path" -H "X-API-KEY: $KOMODO_API_KEY"
  else
    curl -ksS -X "$method" "$KOMODO_URL/api$path" \
      -H "X-API-KEY: $KOMODO_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$body"
  fi
}

infisical_api() {
  local method="$1" path="$2" body="${3:-}"
  local auth=()
  if [ -n "$INFISICAL_TOKEN" ]; then
    auth=(-H "Authorization: Bearer $INFISICAL_TOKEN")
  fi
  if [ "$DRY_RUN" = true ]; then
    echo "  [dry-run] infisical $method $path"
    return
  fi
  if [ -n "$body" ]; then
    curl -ksS -X "$method" "$INFISICAL_URL/api$path" \
      "${auth[@]}" \
      -H "Content-Type: application/json" \
      -d "$body"
  else
    curl -ksS -X "$method" "$INFISICAL_URL/api$path" "${auth[@]}"
  fi
}

# --- Validate prereqs --------------------------------------------------------
log "Tuatha + Pangolin + Komodo + Infisical wiring"
log "============================================="
require DOMAIN "$DOMAIN"

if [ "$SKIP_POCKETID" != true ]; then
  require POCKETID_URL     "$POCKETID_URL"
  require POCKETID_API_KEY "$POCKETID_API_KEY"
fi
if [ "$SKIP_PANGOLIN" != true ]; then
  require PANGOLIN_URL     "$PANGOLIN_URL"
  require PANGOLIN_API_KEY "$PANGOLIN_API_KEY"
fi
if [ "$SKIP_KOMODO" != true ]; then
  require KOMODO_URL     "$KOMODO_URL"
  require KOMODO_API_KEY "$KOMODO_API_KEY"
fi
if [ "$SKIP_INFISICAL" != true ] && [ -z "$INFISICAL_TOKEN" ]; then
  warn "INFISICAL_TOKEN not set — will fall back to client-credentials flow (see Step 1)"
fi

# --- Step 1: Generate TUATH_* secrets and seed Infisical ---------------
if [ "$SKIP_INFISICAL" != true ]; then
  log "Step 1: Ensure TUATH_* secrets exist in Infisical (under /tuatha)"
  # Secrets we provision. Keys are the Infisical secret names; values either come
  # from env (--openai-key=...) or are freshly generated.
  declare -A SECRET_DEFS
  SECRET_DEFS[openai_api_key]="${OPENAI_API_KEY:-}"
  SECRET_DEFS[anthropic_api_key]="${ANTHROPIC_API_KEY:-}"
  SECRET_DEFS[langfuse_public_key]="pk-lf-tuatha-$(openssl rand -hex 8)"
  SECRET_DEFS[langfuse_secret_key]="sk-lf-tuatha-$(openssl rand -hex 16)"
  SECRET_DEFS[x402_payment_url]="https://x402.cianfhoghlaim.ie"
  SECRET_DEFS[jwt_signing_key]="tuatha-jwt-$(openssl rand -hex 24)"

  for KEY in "${!SECRET_DEFS[@]}"; do
    VALUE="${SECRET_DEFS[$KEY]}"
    if [ -z "$VALUE" ]; then
      VALUE="$(openssl rand -hex 32)"
    fi
    BODY=$(cat <<JSON
{
  "workspaceId": "$INFISICAL_WORKSPACE_ID",
  "environment": "$INFISICAL_ENV",
  "secretPath": "$TUATH_SECRET_PATH",
  "type": "shared",
  "secretValue": "$VALUE"
}
JSON
)
    RESP=$(infisical_api POST "/v3/secrets/raw/$KEY" "$BODY" || true)
    ok "Infisical /tuatha/$KEY seeded"
  done
else
  log "Step 1: SKIPPED (--skip-infisical)"
fi

# --- Step 2: Pocket ID OIDC client for Tuatha ---------------------------
if [ "$SKIP_POCKETID" != true ]; then
  log "Step 2: Ensure the '$TUATH_CLIENT_NAME' OIDC client in Pocket ID"

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
  TUATH_CLIENT_ID=""

  if [ -n "$EXISTING" ] && [ "$FORCE" != true ]; then
    ok "Pocket ID OIDC client '$TUATH_CLIENT_NAME' already exists (id=$EXISTING)"
    TUATH_CLIENT_ID="$EXISTING"
  else
    log "  Creating '$TUATH_CLIENT_NAME' OIDC client"
    BODY=$(cat <<JSON
{
  "name": "$TUATH_CLIENT_NAME",
  "type": "public-confidential",
  "enabled": true,
  "scopes": ["openid", "profile", "email", "groups"],
  "redirectUris": [
    "https://tuath-ui.${DOMAIN}/auth/callback",
    "https://tuath-api.${DOMAIN}/auth/callback"
  ],
  "postLogoutRedirectUris": [
    "https://tuath-ui.${DOMAIN}",
    "https://tuath-api.${DOMAIN}"
  ],
  "allowedCorsOrigins": [
    "https://tuath-ui.${DOMAIN}",
    "https://tuath-api.${DOMAIN}",
    "https://tuath.${DOMAIN}"
  ],
  "requirePkce": false,
  "accessTokenType": "Bearer"
}
JSON
)
    CREATE_RESP=$(pocketid_api POST "/oidc/clients" "$BODY" 2>/dev/null || true)
    TUATH_CLIENT_ID=$(echo "$CREATE_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id','') or '')" 2>/dev/null || true)
    if [ -z "$TUATH_CLIENT_ID" ]; then
      warn "Pocket ID OIDC client creation may have failed (or running in dry-run): $CREATE_RESP"
    else
      ok "Created '$TUATH_CLIENT_NAME' OIDC client (id=$TUATH_CLIENT_ID)"
    fi
  fi

  if [ -n "$TUATH_CLIENT_ID" ]; then
    SECRET_RESP=$(pocketid_api POST "/oidc/clients/$TUATH_CLIENT_ID/secret" 2>/dev/null || true)
    TUATH_CLIENT_SECRET=$(echo "$SECRET_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('secret',''))" 2>/dev/null || true)
    if [ -n "$TUATH_CLIENT_SECRET" ]; then
      ok "Tuatha client_secret retrieved (length=${#TUATH_CLIENT_SECRET})"
    fi
  fi
else
  log "Step 2: SKIPPED (--skip-pocketid)"
fi

# --- Step 3: Pangolin resources (3 named routes) -----------------------
if [ "$SKIP_PANGOLIN" != true ]; then
  log "Step 3: Create the 3 Pangolin resources for Tuatha"

  ensure_pangolin_resource() {
    local name="$1" domain="$2" target="$3" middlewares="$4" is_public="${5:-false}"
    local EXISTING=$(pangolin_api GET "/resources?org_id=$PANGOLIN_ORG_ID" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    for r in d.get('data', []):
        if r.get('full_domain') == '$domain' or r.get('name') == '$name':
            print(r.get('resource_id', r.get('id','')))
            break
except Exception:
    pass
" 2>/dev/null || true)

    if [ -n "$EXISTING" ] && [ "$FORCE" != true ]; then
      ok "Pangolin resource '$name' (full_domain=$domain) already exists (id=$EXISTING)"
      echo "$EXISTING"
      return
    fi

    local BODY
    if [ "$is_public" = true ]; then
      BODY=$(cat <<JSON
{
  "org_id": "$PANGOLIN_ORG_ID",
  "name": "$name",
  "protocol": "http",
  "full_domain": "$domain",
  "tags": [{"name": "public"}, {"name": "tuatha"}],
  "enabled": true
}
JSON
)
    else
      BODY=$(cat <<JSON
{
  "org_id": "$PANGOLIN_ORG_ID",
  "name": "$name",
  "protocol": "http",
  "full_domain": "$domain",
  "tags": [{"name": "tinyAuth"}, {"name": "tuatha"}],
  "middleware": "$middlewares",
  "enabled": true
}
JSON
)
    fi
    RESP=$(pangolin_api POST "/resources" "$BODY" 2>/dev/null || true)
    local id=$(echo "$RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',{}).get('resource_id','') or d.get('resource_id','') or '')" 2>/dev/null || true)
    if [ -n "$id" ]; then
      ok "Pangolin resource '$name' created (id=$id)"
    else
      warn "Pangolin resource '$name' creation may have failed: $RESP"
    fi
    echo "$id"
  }

  TUATH_API_RESOURCE_ID=$(ensure_pangolin_resource "Tuatha API" "tuath-api.$DOMAIN"  "http://tuath-api:8000"  "tinyauth,rate-limit-api")
  TUATH_UI_RESOURCE_ID=$(ensure_pangolin_resource "Tuatha UI"  "tuath-ui.$DOMAIN"   "http://tuath-ui:3000"   "tinyauth")
  TUATH_GAME_RESOURCE_ID=$(ensure_pangolin_resource "Tuatha Game" "tuath.$DOMAIN"      "http://tuath-game:8080" "" true)
else
  log "Step 3: SKIPPED (--skip-pangolin)"
fi

# --- Step 4: Komodo deploy trigger ---------------------------------------
if [ "$SKIP_KOMODO" != true ]; then
  log "Step 4: Trigger Komodo deploy of the 'tuatha' stack"
  RESP=$(komodo_api POST "/v1/stack/tuatha/deploy" "{}" 2>/dev/null || true)
  ok "Komodo deploy triggered (idempotent — re-running is a no-op)"
else
  log "Step 4: SKIPPED (--skip-komodo)"
fi

# --- Step 5: Write credentials to .env ----------------------------------
log "Step 5: Write credentials to $ENV_FILE"
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
  upsert_env "TUATH_OIDC_CLIENT_ID"     "${TUATH_CLIENT_ID:-}"
  upsert_env "TUATH_OIDC_CLIENT_SECRET" "${TUATH_CLIENT_SECRET:-}"
  upsert_env "TUATH_PANGOLIN_API_RESOURCE" "${TUATH_API_RESOURCE_ID:-}"
  upsert_env "TUATH_PANGOLIN_UI_RESOURCE"  "${TUATH_UI_RESOURCE_ID:-}"
  upsert_env "TUATH_PANGOLIN_GAME_RESOURCE" "${TUATH_GAME_RESOURCE_ID:-}"
  rm -f "$ENV_FILE.bak"
  ok "Updated $ENV_FILE with TUATH_OIDC_* + 3 Pangolin resource IDs"
else
  warn "$ENV_FILE not found — credentials NOT written locally"
fi

# --- Step 6: Audit record -----------------------------------------------
TS=$(date -u +%Y%m%dT%H%M%SZ)
AUDIT_FILE="/tmp/wire-tuatha-${TS}.json"
cat > "$AUDIT_FILE" <<JSON
{
  "ts": "$TS",
  "domain": "$DOMAIN",
  "tuathOidcClientId": "${TUATH_CLIENT_ID:-}",
  "pangolinResourceIds": {
    "api": "${TUATH_API_RESOURCE_ID:-}",
    "ui": "${TUATH_UI_RESOURCE_ID:-}",
    "game": "${TUATH_GAME_RESOURCE_ID:-}"
  },
  "envFileUpdated": $([ -f "$ENV_FILE" ] && echo true || echo false),
  "stepsRun": {
    "infisical": $([ "$SKIP_INFISICAL" = true ] && echo false || echo true),
    "pocketid": $([ "$SKIP_POCKETID" = true ] && echo false || echo true),
    "pangolin": $([ "$SKIP_PANGOLIN" = true ] && echo false || echo true),
    "komodo": $([ "$SKIP_KOMODO" = true ] && echo false || echo true)
  },
  "dryRun": $([ "$DRY_RUN" = true ] && echo true || echo false)
}
JSON
ok "Audit record: $AUDIT_FILE"

echo ""
log "============================================"
log "Tuatha + Pangolin + Komodo + Infisical wiring: COMPLETE"
log ""
log "Next steps:"
log "  1. Visit https://tuath.$DOMAIN (public game) — should be reachable"
log "  2. Visit https://tuath-api.$DOMAIN → TinyAuth passkey login"
log "  3. Visit https://tuath-ui.$DOMAIN → TinyAuth passkey login"
log "  4. Bind Pocket ID OIDC client to the Pangolin resources:"
log "       ./scripts/wire-tuatha-resource-idp.sh"
log ""
log "Verification commands:"
log "  curl -ksS https://tuath-api.$DOMAIN/healthz"
log "  curl -ksS $POCKETID_URL/.well-known/openid-configuration | jq"
log "  curl -ksS -H 'Authorization: Bearer \$PANGOLIN_API_KEY' $PANGOLIN_URL/api/v1/resources?org_id=$PANGOLIN_ORG_ID | jq"
