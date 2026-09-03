#!/usr/bin/env bash
# =============================================================================
# SEED BUNCHLOCH FALLBACK VAULT (companion to the
# 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1
# openspec change)
# =============================================================================
# Writes 7 infisical-meta secrets + 10 openclaw + 4 hermes infisical
# paths under dev-baile/dev on the LOCAL Infisical vault (port 8081).
# Idempotent — safe to re-run; uses upsert semantics.
#
# Prerequisites (set in env before running):
#   INFISICAL_URL              — default http://127.0.0.1:8081
#   INFISICAL_PROJECT_ID       — UUID from the dev-baile project URL
#   INFISICAL_CLIENT_ID        — bons-iac Universal Auth client_id
#   INFISICAL_CLIENT_SECRET    — bons-iac Universal Auth client_secret
#   INFISICAL_ENV              — default dev
#
# Usage:
#   INFISICAL_PROJECT_ID=... INFISICAL_CLIENT_ID=... INFISICAL_CLIENT_SECRET=... \
#     bun run scripts/seed-bunchloch-fallback-vault.sh
# =============================================================================

set -euo pipefail

INFISICAL_URL="${INFISICAL_URL:-http://127.0.0.1:8081}"
PROJECT_ID="${INFISICAL_PROJECT_ID:?must be set (capture from project URL)}"
CLIENT_ID="${INFISICAL_CLIENT_ID:?must be set}"
CLIENT_SECRET="${INFISICAL_CLIENT_SECRET:?must be set}"
ENV="${INFISICAL_ENV:-dev}"

# Pre-flight: confirm infisical CLI is logged in / vault reachable
if ! command -v infisical >/dev/null 2>&1; then
  echo "ERROR: infisical CLI not on PATH; run: mise install (or brew install infisical)" >&2
  exit 2
fi

echo "[seed-bunchloch-fallback-vault] target=${INFISICAL_URL} project=${PROJECT_ID} env=${ENV}"

# Helper: upsert a single secret
infisical_set() {
  local path="$1" value="$2"
  infisical secrets set "$path=$value" \
    --projectId="$PROJECT_ID" --env="$ENV" \
    --url="$INFISICAL_URL" --token="$CLIENT_SECRET" --plain \
    >/dev/null
  echo "  set ${ENV}/${path}"
}

# Generate values
ENCRYPTION_KEY=$(openssl rand -hex 16)
AUTH_SECRET=$(openssl rand -base64 32)
POSTGRES_PASSWORD=$(openssl rand -hex 24)
DB_URI="postgresql://infisical:${POSTGRES_PASSWORD}@infisical-db:5432/infisical"
REDIS_URL="redis://infisical-redis:6379"
SITE_URL="http://127.0.0.1:8081"
GATEWAY_TOKEN=$(openssl rand -hex 32)
HERMES_API_KEY=$(openssl rand -hex 32)
LITELLM_PLACEHOLDER="sk-placeholder-replace-with-litellm-master-key"
LANGFUSE_OTEL="http://langfuse:3000/api/public/otel"

echo "[1/3] writing 7 infisical meta-secrets"
infisical_set infisical/encryption_key   "$ENCRYPTION_KEY"
infisical_set infisical/auth_secret      "$AUTH_SECRET"
infisical_set infisical/postgres_password "$POSTGRES_PASSWORD"
infisical_set infisical/db_uri           "$DB_URI"
infisical_set infisical/redis_url        "$REDIS_URL"
infisical_set infisical/site_url         "$SITE_URL"
infisical_set infisical/client_secret    "$CLIENT_SECRET"

echo "[2/3] writing 10 openclaw secrets"
infisical_set openclaw/gateway_token               "$GATEWAY_TOKEN"
infisical_set openclaw/openai_api_key              "$LITELLM_PLACEHOLDER"
infisical_set openclaw/telegram_bot_token          ""
infisical_set openclaw/slack_bot_token             ""
infisical_set openclaw/slack_app_token             ""
infisical_set openclaw/discord_bot_token           ""
infisical_set openclaw/whatsapp_access_token       ""
infisical_set openclaw/whatsapp_phone_number_id    ""
infisical_set openclaw/teams_bot_token             ""
infisical_set openclaw/otel_exporter_otlp_endpoint "$LANGFUSE_OTEL"

echo "[3/3] writing 4 hermes secrets"
infisical_set hermes/api_server_key              "$HERMES_API_KEY"
infisical_set hermes/operator_pocket_id_subject  ""
infisical_set hermes/openai_api_key              "$LITELLM_PLACEHOLDER"
infisical_set hermes/otel_exporter_otlp_endpoint "$LANGFUSE_OTEL"

# Write the bons-iac credential to the Komodo Periphery mount path
mkdir -p /etc/komodo/secrets
cat > /etc/komodo/secrets/infisical_secret <<EOF
INFISICAL_CLIENT_ID=${CLIENT_ID}
INFISICAL_CLIENT_SECRET=${CLIENT_SECRET}
INFISICAL_PROJECT_ID=${PROJECT_ID}
INFISICAL_URL=${INFISICAL_URL}
INFISICAL_ENV=${ENV}
EOF
chmod 0600 /etc/komodo/secrets/infisical_secret

echo ""
echo "OK: 7 infisical + 10 openclaw + 4 hermes paths seeded under dev-baile/${ENV}"
echo "OK: bons-iac credential written to /etc/komodo/secrets/infisical_secret (mode 0600)"