#!/usr/bin/env bash
# scripts/verify-unsloth-serve.sh
# 7-step verification protocol per the 2026-08-21-unsloth-v5-architecture-refinement-v1 change
# Per the umbrella change 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1
set -euo pipefail

API_KEY="${UNSLOTH_API_KEY:-sk-unsloth-0441df9d8d90363e2a80cbb226f197f6}"
LITELLM_KEY="${LITELLM_MASTER_KEY:?must be set}"
# UNSLOTH_URL: try host.docker.internal first (inside Docker), fall back to localhost
if [ -z "${UNSLOTH_URL:-}" ]; then
  if curl -fs -m 1 http://host.docker.internal:8888/api/auth/status >/dev/null 2>&1; then
    UNSLOTH_URL="http://host.docker.internal:8888"
  else
    UNSLOTH_URL="http://localhost:8888"
  fi
fi
LITELLM_URL="${LITELLM_URL:-http://localhost:4000}"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

check() {
  local name="$1"
  local result="$2"  # "PASS" or "FAIL"
  local detail="${3:-}"
  if [ "$result" = "PASS" ]; then
    echo -e "${GREEN}✅${NC} $name"
    [ -n "$detail" ] && echo -e "   $detail"
    pass_count=$((pass_count+1))
  else
    echo -e "${RED}❌${NC} $name"
    [ -n "$detail" ] && echo -e "   $detail"
    fail_count=$((fail_count+1))
  fi
}

echo -e "${BLUE}=== Unsloth Studio + Litellm verification (7 steps) ===${NC}"
echo ""

# Step 1: Studio health
echo "[1/7] Studio health endpoint..."
RESP=$(curl -fs -m 5 "$UNSLOTH_URL/api/auth/status" 2>&1) && \
  check "Step 1: Studio health" "PASS" "$RESP" || \
  check "Step 1: Studio health" "FAIL" "$RESP"

# Step 2: Studio status (empty models OK)
echo "[2/7] Studio status..."
HTTP=$(curl -fs -m 5 -H "Authorization: Bearer $API_KEY" "$UNSLOTH_URL/api/inference/status" -o /dev/null -w "%{http_code}" 2>&1)
[ "$HTTP" = "200" ] && check "Step 2: Studio status" "PASS" "(empty model fields expected)" || \
  check "Step 2: Studio status" "FAIL" "HTTP $HTTP"

# Step 3: Studio flags catalog
echo "[3/7] Studio llama-flags..."
FLAG_COUNT=$(curl -fs -m 10 -H "Authorization: Bearer $API_KEY" "$UNSLOTH_URL/api/inference/llama-flags" 2>/dev/null | python3 -c "import json, sys; print(len(json.loads(sys.stdin.read()).get('flags', {})))" 2>/dev/null || echo 0)
if [ "$FLAG_COUNT" -gt 100 ]; then
  check "Step 3: Studio llama-flags catalog" "PASS" "$FLAG_COUNT flags exposed"
else
  check "Step 3: Studio llama-flags catalog" "FAIL" "Only $FLAG_COUNT flags"
fi

# Step 4: Studio error path (expected 400 "No model loaded")
echo "[4/7] Studio chat error path..."
HTTP=$(curl -s -m 5 -o /tmp/verify-studio-resp.json -w "%{http_code}" -X POST \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  "$UNSLOTH_URL/v1/chat/completions" \
  -d '{"model":"unsloth/Qwen3.8-27B-GGUF","messages":[{"role":"user","content":"hi"}]}' 2>&1) || HTTP="000"
RESP_BODY=$(cat /tmp/verify-studio-resp.json 2>/dev/null | head -c 200 || echo "")
if [ "$HTTP" = "400" ] || [ "$HTTP" = "503" ]; then
  if echo "$RESP_BODY" | grep -q "No model loaded\|model_group"; then
    check "Step 4: Studio chat returns expected error" "PASS" "HTTP $HTTP (no model loaded)"
  else
    check "Step 4: Studio chat" "FAIL" "HTTP $HTTP but unexpected body: $RESP_BODY"
  fi
else
  check "Step 4: Studio chat" "FAIL" "HTTP $HTTP"
fi

# Step 5: Litellm unsloth routes
echo "[5/7] Litellm unsloth routes..."
ROUTE_COUNT=$(curl -fs -m 10 -H "Authorization: Bearer $LITELLM_KEY" "$LITELLM_URL/v1/models" 2>/dev/null | \
  python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
print(len([m for m in d['data'] if 'unsloth' in m['id'].lower()]))
" 2>/dev/null || echo 0)
if [ "$ROUTE_COUNT" -ge 18 ]; then
  check "Step 5: Litellm unsloth routes loaded" "PASS" "$ROUTE_COUNT routes"
else
  check "Step 5: Litellm unsloth routes" "FAIL" "Only $ROUTE_COUNT routes (need ≥18)"
fi

# Step 6: Litellm → Studio passthrough
echo "[6/7] Litellm → Studio passthrough..."
HTTP=$(curl -s -m 30 -o /tmp/verify-litellm-resp.json -w "%{http_code}" -X POST \
  -H "Authorization: Bearer $LITELLM_KEY" \
  -H "Content-Type: application/json" \
  "$LITELLM_URL/v1/chat/completions" \
  -d '{"model":"local/unsloth/qwen3.8-27b","messages":[{"role":"user","content":"hi"}],"max_tokens":5}' 2>&1) || HTTP="000"
RESP_BODY=$(cat /tmp/verify-litellm-resp.json 2>/dev/null | head -c 300 || echo "")
if echo "$RESP_BODY" | grep -q "No model loaded"; then
  check "Step 6: Litellm reaches Studio" "PASS" "HTTP $HTTP (Studio returns 'No model loaded')"
else
  check "Step 6: Litellm reaches Studio" "FAIL" "HTTP $HTTP: $RESP_BODY"
fi

# Step 7: Marimo notebook (manual UI test)
echo "[7/7] Marimo notebook (manual UI test)..."
MARIMO_BODY=$(curl -fs -m 5 http://localhost:2718/health 2>/dev/null || echo "DOWN")
if echo "$MARIMO_BODY" | grep -q '"status":"ok"'; then
  check "Step 7: Marimo notebook server live" "PASS" "Open http://localhost:2718/apps/34_onboarding_04_biep_ocr_eval/ manually"
else
  check "Step 7: Marimo notebook server" "FAIL" "Body: $MARIMO_BODY"
fi

echo ""
echo -e "${BLUE}=== Summary ===${NC}"
echo -e "Passed: ${GREEN}$pass_count${NC} / 7"
echo -e "Failed: ${RED}$fail_count${NC} / 7"

if [ "$fail_count" -eq 0 ]; then
  echo -e "\n${GREEN}✅ All 7 steps verified!${NC}"
  exit 0
else
  echo -e "\n${RED}❌ Some steps failed. See above.${NC}"
  exit 1
fi
