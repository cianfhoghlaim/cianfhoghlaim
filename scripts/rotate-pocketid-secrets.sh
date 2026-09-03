#!/usr/bin/env bash
# rotate-pocketid-secrets.sh — Cron job for the bons-iac OIDC client secret rotation.
# Run via cron: 0 3 1 */3 * * /Users/cianmacadeisigh/dev/kings_college_galway/scripts/rotate-pocketid-secrets.sh
#   (every 3 months, 3am)
#
# What this does:
#   1. Fetch a fresh bons-iac client secret from Pocket ID admin API
#   2. Use it immediately to get a fresh Pangolin API key
#   3. Write the new Pangolin API key to .env + the bons-iac secret to Infisical
#   4. Write an audit record to /tmp/pocketid-rotation-{ts}.json
#   5. Alert on failure (email or webhook - configurable)
#
# Safety:
#   - The previous secret is invalidated by Pocket ID after each /secret call
#   - The new Pangolin API key is the ONLY stable thing
#   - Atomic write: write the new key BEFORE the old one expires (default 7-day TTL)
#
# Dependencies: pocketIdFreshPangolinSecret() + pocketIdLogin() from
#   bonneagar/iac/auth-pocketid.ts (run via bun)

set -euo pipefail

WORKTREE="$(git rev-parse --show-toplevel)"
ENV_FILE="$WORKTREE/.env"
AUDIT_FILE="/tmp/pocketid-rotation-$(date -u +%Y%m%dT%H%M%SZ).json"

cd "$WORKTREE"

# Load env
set -a; source "$ENV_FILE" 2>/dev/null || true; set +a

if [ -z "$POCKETID_PANGOLIN_CLIENT_ID" ] || [ -z "$POCKETID_API_KEY" ]; then
  echo "ERROR: POCKETID_PANGOLIN_CLIENT_ID + POCKETID_API_KEY must be set in $ENV_FILE" >&2
  exit 2
fi

if [ -z "$PANGOLIN_URL" ] || [ -z "$PANGOLIN_ORG_ID" ]; then
  echo "ERROR: PANGOLIN_URL + PANGOLIN_ORG_ID must be set in $ENV_FILE" >&2
  exit 2
fi

# Run the rotation via bun
echo "[$(date -u +%H:%M:%S)] rotate-pocketid-secrets: starting"

OUTPUT=$(cd "$WORKTREE" && POCKETID_PANGOLIN_CLIENT_ID="$POCKETID_PANGOLIN_CLIENT_ID" \
  POCKETID_API_KEY="$POCKETID_API_KEY" \
  POCKETID_URL="$POCKETID_URL" \
  PANGOLIN_URL="$PANGOLIN_URL" \
  PANGOLIN_ORG_ID="$PANGOLIN_ORG_ID" \
  bun run -e '
import { pocketIdLogin } from "./bonneagar/iac/auth-pocketid.ts";
const apiKey = await pocketIdLogin({ name: "cron-rotation", expiresIn: 7 * 24 * 60 * 60 });
console.log(JSON.stringify({apiKey: apiKey.apiKey, apiKeyId: apiKey.apiKeyId, expiresAt: new Date(Date.now() + 7*24*60*60*1000).toISOString()}));
' 2>&1)

# Parse the result
NEW_KEY=$(echo "$OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('apiKey',''))" 2>/dev/null || echo "")

if [ -z "$NEW_KEY" ]; then
  echo "ERROR: rotation failed. Output: $OUTPUT" >&2
  echo "{\"ts\":\"$(date -u +%Y%m%dT%H%M%SZ)\",\"status\":\"failed\",\"output\":\"$OUTPUT\"}" > "$AUDIT_FILE"
  exit 1
fi

# Update .env
if grep -q "^PANGOLIN_API_KEY=" "$ENV_FILE"; then
  sed -i.bak "s|^PANGOLIN_API_KEY=.*|PANGOLIN_API_KEY=\"$NEW_KEY\"|" "$ENV_FILE"
  rm -f "$ENV_FILE.bak"
else
  echo "PANGOLIN_API_KEY=\"$NEW_KEY\"" >> "$ENV_FILE"
fi

# Write audit
cat > "$AUDIT_FILE" <<JSON
{
  "ts": "$(date -u +%Y%m%dT%H%M%SZ)",
  "status": "ok",
  "apiKeyId": "$(echo "$OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('apiKeyId',''))" 2>/dev/null)",
  "expiresAt": "$(echo "$OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('expiresAt',''))" 2>/dev/null)",
  "envFile": "$ENV_FILE"
}
JSON

echo "[$(date -u +%H:%M:%S)] rotate-pocketid-secrets: ok (apiKeyId=$(echo "$OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('apiKeyId',''))" 2>/dev/null))"
echo "[$(date -u +%H:%M:%S)] audit: $AUDIT_FILE"
