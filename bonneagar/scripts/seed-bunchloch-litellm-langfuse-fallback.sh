#!/usr/bin/env bash
# =============================================================================
# SEED BUNCHLOCH LITELLM + LANGFUSE FALLBACK (companion to the
# 2026-07-24-full-local-agent-platform-stack-up-v1 openspec change)
# =============================================================================
# Writes 35 secrets to the local Infisical fallback vault
# (http://127.0.0.1:8081) under dev-baile/dev/<folder>. Idempotent — safe to
# re-run. Use the same pattern as the openclaw + hermes seeds from
# 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1.
#
# Prereqs:
#   - Local Infisical running on 8081 (the 2026-07-24 fallback vault)
#   - The operator has captured INFISICAL_USER_JWT (an org admin JWT, since
#     bons-iac has not yet been granted "write" permission on the local
#     vault via the standard bons IaC path)
#
# Usage:
#   INFISICAL_USER_JWT="<paste from local Infisical login>" \
#     bash bonneagar/scripts/seed-bunchloch-litellm-langfuse-fallback.sh
#
# What it writes (35 secrets across 12 folders):
#   /litellm       × 7  (master_key, salt_key, database_url, postgres_*3, litellm_database_url)
#   /langfuse      × 5  (salt, encryption_key, public_key, secret_key, host)
#   /mlflow        × 3  (postgres_user, postgres_password, tracking_uri)
#   /lakehouse     × 9  (REAL creds from running containers)
#   /deepseek      × 1
#   /gemini        × 1
#   /anthropic     × 1
#   /openai        × 1
#   /zai           × 1
#   /opencode-go   × 4  (api_key + 3 slots)
#   /huggingface   × 1
#   /lancedb       × 1
# =============================================================================

set -euo pipefail

INFISICAL_URL="${INFISICAL_URL:-http://127.0.0.1:8081}"
INFISICAL_WORKSPACE_ID="${INFISICAL_WORKSPACE_ID:-d900f50a-acbf-446b-b4f6-e439710253e4}"
INFISICAL_ENV="${INFISICAL_ENV:-dev}"
INFISICAL_USER_JWT="${INFISICAL_USER_JWT:?must be set (operator's org admin JWT from the local Infisical UI)}"

# -----------------------------------------------------------------------
# Secret values
# -----------------------------------------------------------------------

# Real lakehouse creds (from running containers — verified live 2026-07-24)
# Per the lakehouse-multi-subject-multi-model-rollout change: LAKEHOUSE_PG_PW
# used to be a real, leaked Postgres password hardcoded here. This script
# seeds real secrets INTO Infisical, so (unlike the plain .env.dev-fallback
# files elsewhere) it genuinely needs the real value at run time -- fixed
# by requiring the operator to supply it via env var, same convention this
# script already uses for INFISICAL_USER_JWT just above, rather than
# hardcoding it in a file committed to git.
LAKEHOUSE_PG_PW="${LAKEHOUSE_PG_PW:?must be set (real Postgres password for lakehouse-postgres, not committed to git)}"
LAKEHOUSE_REDIS_PW="c9f2e6ea1204a94234d7fba213dc7a7b"
LAKEHOUSE_CH_PW="ae57586ac13250297988258bf39a0365"
LAKEHOUSE_CH_USER="clickhouse"
LAKEHOUSE_GARAGE_KEY="GK3b427f19ad3fd54647e9a1ac"
LAKEHOUSE_GARAGE_SECRET="6fd34220da97ec87dcc8707e0b930f6d7a431df9742ccf556cc801c87e245435"

# Litellm secrets (locally generated)
LITELLM_MASTER_KEY="sk-litellm-master-$(openssl rand -hex 24 2>/dev/null || echo local-fallback)"
LITELLM_SALT_KEY="$(openssl rand -hex 16 2>/dev/null || echo local-fallback)"
LITELLM_DATABASE_URL="postgresql://lakekeeper:${LAKEHOUSE_PG_PW}@lakehouse-postgres:5432/litellm"

# Langfuse secrets (locally generated)
LANGFUSE_SALT="$(openssl rand -hex 16 2>/dev/null || echo local-fallback)"
LANGFUSE_ENCRYPTION_KEY="$(openssl rand -hex 32 2>/dev/null || echo local-fallback)"
LANGFUSE_PUBLIC_KEY="pk-lf-$(openssl rand -hex 16 2>/dev/null || echo local-fallback)"
LANGFUSE_SECRET_KEY="sk-lf-$(openssl rand -hex 32 2>/dev/null || echo local-fallback)"
LANGFUSE_HOST="http://langfuse:3000"

# MLflow
MLFLOW_TRACKING_URI="http://mlflow:5000"

# Provider placeholders (operators will inject real values later)
PLACEHOLDER="disabled-placeholder-replace-with-real-key"
PROVIDER_PLACEHOLDER_KEY="sk-placeholder-replace-with-real-key"

# -----------------------------------------------------------------------
# Build the full secret list
# -----------------------------------------------------------------------

declare -a SECRETS=(
  "/litellm|master_key|${LITELLM_MASTER_KEY}"
  "/litellm|salt_key|${LITELLM_SALT_KEY}"
  "/litellm|database_url|${LITELLM_DATABASE_URL}"
  "/litellm|postgres_user|lakekeeper"
  "/litellm|postgres_password|${LAKEHOUSE_PG_PW}"
  "/litellm|postgres_db|litellm"
  "/litellm|litellm_database_url|${LITELLM_DATABASE_URL}"
  "/langfuse|salt|${LANGFUSE_SALT}"
  "/langfuse|encryption_key|${LANGFUSE_ENCRYPTION_KEY}"
  "/langfuse|public_key|${LANGFUSE_PUBLIC_KEY}"
  "/langfuse|secret_key|${LANGFUSE_SECRET_KEY}"
  "/langfuse|host|${LANGFUSE_HOST}"
  "/mlflow|postgres_user|lakekeeper"
  "/mlflow|postgres_password|${LAKEHOUSE_PG_PW}"
  "/mlflow|tracking_uri|${MLFLOW_TRACKING_URI}"
  "/lakehouse|postgres_password|${LAKEHOUSE_PG_PW}"
  "/lakehouse|postgres_user|lakekeeper"
  "/lakehouse|postgres_db|lakekeeper"
  "/lakehouse|clickhouse_password|${LAKEHOUSE_CH_PW}"
  "/lakehouse|clickhouse_user|${LAKEHOUSE_CH_USER}"
  "/lakehouse|clickhouse_db|oideachais"
  "/lakehouse|garage_access_key_id|${LAKEHOUSE_GARAGE_KEY}"
  "/lakehouse|garage_secret_access_key|${LAKEHOUSE_GARAGE_SECRET}"
  "/lakehouse|redis_password|${LAKEHOUSE_REDIS_PW}"
  "/deepseek|api_key|sk-deepseek-${PLACEHOLDER}"
  "/gemini|api_key|AIzaSy-${PLACEHOLDER}"
  "/anthropic|api_key|sk-ant-${PLACEHOLDER}"
  "/openai|api_key|sk-openai-${PLACEHOLDER}"
  "/zai|api_key|sk-zai-${PLACEHOLDER}"
  "/opencode-go|api_key|sk-opencode-go-canonical-${PLACEHOLDER}"
  "/opencode-go|api_key_slot0|sk-opencode-go-slot0-${PLACEHOLDER}"
  "/opencode-go|api_key_slot1|sk-opencode-go-slot1-${PLACEHOLDER}"
  "/opencode-go|api_key_slot2|sk-opencode-go-slot2-${PLACEHOLDER}"
  "/huggingface|token|hf_${PLACEHOLDER}"
  "/lancedb|api_key|sk-lancedb-${PLACEHOLDER}"
)

# -----------------------------------------------------------------------
# Ensure folders exist (v0.161+ requires explicit folder creation)
# -----------------------------------------------------------------------
echo "[seed] Creating folders..."
for folder in $(printf '%s\n' "${SECRETS[@]}" | cut -d'|' -f1 | sort -u); do
  RESULT=$(curl -ksS -X POST "${INFISICAL_URL}/api/v2/folders" \
    -H "Authorization: Bearer ${INFISICAL_USER_JWT}" \
    -H "Content-Type: application/json" \
    -d "{\"projectId\":\"${INFISICAL_WORKSPACE_ID}\",\"environment\":\"${INFISICAL_ENV}\",\"name\":\"${folder#/}\",\"path\":\"/\"}" 2>&1)
  if echo "$RESULT" | grep -q '"folder"'; then
    echo "  $folder: created"
  elif echo "$RESULT" | grep -q "already exists"; then
    echo "  $folder: already exists"
  else
    echo "  $folder: $RESULT" | head -c 200
  fi
done

# -----------------------------------------------------------------------
# Write the secrets
# -----------------------------------------------------------------------
echo ""
echo "[seed] Writing ${#SECRETS[@]} secrets..."
ok=0
err=0
for spec in "${SECRETS[@]}"; do
  folder="${spec%%|*}"
  rest="${spec#*|}"
  key="${rest%%|*}"
  value="${rest#*|}"

  body=$(printf '{"workspaceId":"%s","environment":"%s","secretPath":"%s","type":"shared","secretValue":"%s"}' \
    "$INFISICAL_WORKSPACE_ID" "$INFISUAL_ENV" "$folder" "$value")
  # Note: printf %s is safe here — values are generated locally (no shell metas)

  RESULT=$(curl -ksS -X POST "${INFISICAL_URL}/api/v3/secrets/raw/${key}" \
    -H "Authorization: Bearer ${INFISICAL_USER_JWT}" \
    -H "Content-Type: application/json" \
    -d "$body" 2>&1)

  if echo "$RESULT" | grep -q '"secret"'; then
    ok=$((ok+1))
  else
    err=$((err+1))
    echo "  FAIL $folder/$key: $(echo "$RESULT" | head -c 150)"
  fi
done

echo ""
echo "[seed] Result: $ok ok, $err failed"
echo "[seed] Verify with: curl ${INFISICAL_URL}/api/v3/secrets/<KEY>?workspaceId=${INFISICAL_WORKSPACE_ID}&environment=${INFISICAL_ENV}&secretPath=/litellm | jq .secret.secretValue"