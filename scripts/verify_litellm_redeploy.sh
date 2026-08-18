#!/usr/bin/env bash
# verify_litellm_redeploy.sh
#
# Per the 2026-08-17-biep-v3-bring-up-v1 change (P2.5): after
# `km deploy stack litellm --force`, wait for the container to be
# healthy and assert that the new config is in effect (i.e. the
# `router_settings.fallbacks` is the dict form, not a bare list).
#
# Usage:
#   bash scripts/verify_litellm_redeploy.sh
#
# Exit codes:
#   0 = litellm container is healthy + dict-form fallbacks are in effect
#   1 = container not healthy within timeout
#   2 = bare-list form is still present in the deployed config
#   3 = runtime fallback validation errors found in container logs

set -euo pipefail

LITELLM_CONTAINER="${LITELLM_CONTAINER:-litellm}"
LITELLM_HOST="${LITELLM_HOST:-http://localhost:4000}"
HEALTH_PATH="${HEALTH_PATH:-/health/readiness}"
TIMEOUT="${TIMEOUT:-60}"  # seconds
DICT_FORM_PATTERN='^\s*-\s*[a-zA-Z0-9_./-]+\s*:\s*\['
BARE_LIST_PATTERN='^\s*-\s*[a-zA-Z0-9_./-]+\s*$'

echo "Step 1: wait for litellm container to be healthy (timeout: ${TIMEOUT}s)..."
SECONDS=0
while [ $SECONDS -lt $TIMEOUT ]; do
  if docker exec "$LITELLM_CONTAINER" curl -fsS "$LITELLM_HOST/$HEALTH_PATH" >/dev/null 2>&1; then
    echo "  OK: litellm container is healthy at $LITELLM_HOST/$HEALTH_PATH"
    break
  fi
  sleep 2
done

if [ $SECONDS -ge $TIMEOUT ]; then
  echo "FAIL: litellm container did not become healthy within ${TIMEOUT}s"
  docker logs --tail 50 "$LITELLM_CONTAINER" >&2 || true
  exit 1
fi

echo ""
echo "Step 2: assert the deployed config uses the dict-form fallbacks..."
# Inspect the config that's actually loaded by litellm
DEPLOYED_CONFIG=$(docker exec "$LITELLM_CONTAINER" cat /app/config.yaml 2>/dev/null || echo "")

if [ -z "$DEPLOYED_CONFIG" ]; then
  echo "  WARN: cannot read /app/config.yaml from the container; falling back to the source-of-truth"
  DEPLOYED_CONFIG=$(cat "bonneagar/stacks/litellm/config/config.yaml")
fi

# Find the `fallbacks:` block under `router_settings:` and inspect each
# entry. A correct entry looks like:
#   - qwen3-vl-8b: [gemma-4-26B-A4B, ...]
# A wrong entry looks like (bare list):
#   - qwen3-vl-8b
#   - gemma-4-26B-A4B
FOUND_DICT=0
FOUND_BARE=0
IN_ROUTER=0
while IFS= read -r line; do
  if [[ "$line" =~ ^router_settings: ]]; then
    IN_ROUTER=1
    continue
  fi
  if [ "$IN_ROUTER" -eq 1 ] && [[ "$line" =~ ^[a-zA-Z] ]] && [[ ! "$line" =~ ^[[:space:]] ]]; then
    # end of router_settings section
    break
  fi
  if [ "$IN_ROUTER" -eq 1 ] && [[ "$line" =~ $DICT_FORM_PATTERN ]]; then
    FOUND_DICT=$((FOUND_DICT + 1))
  fi
  if [ "$IN_ROUTER" -eq 1 ] && [[ "$line" =~ $BARE_LIST_PATTERN ]]; then
    FOUND_BARE=$((FOUND_BARE + 1))
  fi
done <<< "$DEPLOYED_CONFIG"

if [ "$FOUND_DICT" -eq 0 ]; then
  echo "  FAIL: no dict-form fallbacks found in router_settings"
  exit 2
fi

if [ "$FOUND_BARE" -gt 0 ]; then
  echo "  FAIL: $FOUND_BARE bare-list fallbacks detected (crash-loops the container)"
  echo "  FIX: use the dict form {primary_model: [fallback_model, ...]}"
  exit 2
fi

echo "  OK: $FOUND_DICT dict-form fallbacks, $FOUND_BARE bare-list"

echo ""
echo "Step 3: scan container logs for Router.validate_fallbacks errors..."
VALIDATION_ERRORS=$(docker logs --since 5m "$LITELLM_CONTAINER" 2>&1 | grep -cE "Router.validate_fallbacks|Item '.*' is not a dictionary" || true)

if [ "$VALIDATION_ERRORS" -gt 0 ]; then
  echo "  FAIL: $VALIDATION_ERRORS Router.validate_fallbacks errors in the last 5m"
  docker logs --since 5m "$LITELLM_CONTAINER" | grep -E "Router.validate_fallbacks|is not a dictionary" | head -5 >&2
  exit 3
fi

echo "  OK: no Router.validate_fallbacks errors in the last 5m"

echo ""
echo "OK: litellm redeploy is healthy + dict-form fallbacks are in effect"
exit 0