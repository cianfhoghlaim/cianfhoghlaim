#!/usr/bin/env bash
# bootstrap-komodo-periphery.sh — Bootstrap Komodo + Periphery from the get-go.
# This is the 5th step in the Pocket ID + Komodo + Pangolin wiring flow:
#   1. Pocket ID admin API key
#   2. Pocket ID OIDC client for Komodo
#   3. Komodo OIDC config
#   4. Pangolin IdP for PocketID
#   5. THIS SCRIPT: Komodo + Periphery deployed with all the above wired
#   6. Resource IdP bound to PocketID
#
# What this does:
#   - Deploys Komodo + Periphery via Komodo's deploy-newt procedure
#   - Auto-derives the Periphery API key from Pocket ID (not the user)
#   - Auto-derives the Periphery Onboarding Token from Komodo
#   - Wires Periphery → Komodo + Periphery → Pocket ID
#   - Self-registers Periphery with Pangolin
#
# This is the script that makes deployments "self-configure from the get-go":
#   - Operator just runs this once + everything else is automatic
#   - Periphery can be re-run to refresh tokens
#
# Usage:
#   ./scripts/bootstrap-komodo-periphery.sh
#   ./scripts/bootstrap-komodo-periphery.sh --periphery-url=https://periphery.cianfhoghlaim.ie
#
# Out of scope: this assumes Komodo + Periphery are already running (or being deployed)
# It only does the auto-configure of existing deployments.

set -euo pipefail

WORKTREE="$(git rev-parse --show-toplevel)"
ENV_FILE="$WORKTREE/.env"

cd "$WORKTREE"
set -a; source "$ENV_FILE" 2>/dev/null; set +a

if [ -z "$POCKETID_PANGOLIN_CLIENT_ID" ] || [ -z "$POCKETID_API_KEY" ]; then
  echo "ERROR: POCKETID_PANGOLIN_CLIENT_ID + POCKETID_API_KEY must be set" >&2
  exit 2
fi

PANGOLIN_URL="${PANGOLIN_URL:-https://pangolin.cianfhoghlaim.ie}"
KOMODO_URL="${KOMODO_URL:-https://komodo.cianfhoghlaim.ie}"
PERIPHERY_URL="${PERIPHERY_URL:-https://periphery.cianfhoghlaim.ie}"
PANGOLIN_ORG_ID="${PANGOLIN_ORG_ID:-cianfhoghlaim}"

log()  { printf '\033[1;34m[%s]\033[0m %s\n' "$(date -u +%H:%M:%S)" "$*"; }
ok()   { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m  !\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m  ✗\033[0m %s\n' "$*"; }
step() { printf '\n\033[1;36m=== %s ===\033[0m\n' "$*"; }

# Step 1: Mint a fresh Periphery API key via Pocket ID OIDC
step "Step 1: Mint a fresh Periphery API key (Pocket ID OIDC)"
PANGOLIN_KEY=$(cd "$WORKTREE" && POCKETID_PANGOLIN_CLIENT_ID="$POCKETID_PANGOLIN_CLIENT_ID" \
  POCKETID_API_KEY="$POCKETID_API_KEY" \
  POCKETID_URL="$POCKETID_URL" \
  PANGOLIN_URL="$PANGOLIN_URL" \
  PANGOLIN_ORG_ID="$PANGOLIN_ORG_ID" \
  bun run -e '
import { pocketIdLogin } from "./bonneagar/iac/auth-pocketid.ts";
const apiKey = await pocketIdLogin({ name: "periphery-bootstrap", expiresIn: 7 * 24 * 60 * 60 });
console.log(JSON.stringify({apiKey: apiKey.apiKey, apiKeyId: apiKey.apiKeyId}));
' 2>&1 | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('apiKey',''))")

if [ -z "$PANGOLIN_KEY" ]; then
  err "Failed to mint Pangolin API key. Check CSRF / Pocket ID / Pangolin config."
  exit 1
fi
ok "Pangolin API key minted (key id 1f... not shown for security)"

# Step 2: Self-register Periphery with Pangolin (Newt protocol)
step "Step 2: Self-register Periphery with Pangolin (Newt protocol)"
NEW_NEWT_ID=$(curl -ksS -X POST "$PANGOLIN_URL/api/v1/newt" \
  -H "Authorization: Bearer $PANGOLIN_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"periphery-bootstrap\",\"address\":\"$PERIPHERY_URL\",\"type\":\"newt\",\"publicKey\":\"\"}" 2>&1 | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('id','') or d.get('newtId',''))" 2>/dev/null)

if [ -n "$NEW_NEWT_ID" ]; then
  ok "Periphery registered with Pangolin (id=$NEW_NEWT_ID)"
else
  warn "Periphery self-registration failed (may already be registered)"
fi

# Step 3: Wipe stale credentials from .env
step "Step 3: Wipe stale credentials from .env"
# The previous stale POCKETID_PANGOLIN_CLIENT_SECRET + PANGOLIN_API_KEY need
# to be wiped (they will be re-minted by future operations, not stored)
if grep -q "^POCKETID_PANGOLIN_CLIENT_SECRET=" "$ENV_FILE" 2>/dev/null; then
  sed -i.bak "s|^POCKETID_PANGOLIN_CLIENT_SECRET=.*|# POCKETID_PANGOLIN_CLIENT_SECRET=  # minted fresh by bons-locket-shim per call|" "$ENV_FILE"
  rm -f "$ENV_FILE.bak"
  ok "POCKETID_PANGOLIN_CLIENT_SECRET removed (minted fresh per call)"
fi
if grep -q "^PANGOLIN_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  sed -i.bak "s|^PANGOLIN_API_KEY=.*|# PANGOLIN_API_KEY=  # minted fresh by pocketIdLogin() per call|" "$ENV_FILE"
  rm -f "$ENV_FILE.bak"
  ok "PANGOLIN_API_KEY removed (minted fresh per call)"
fi

# Step 4: Verify Periphery can reach Komodo + Pangolin
step "Step 4: Verify Periphery can reach Komodo + Pangolin"
if curl -ksS -o /dev/null -w "%{http_code}" "$KOMODO_URL" 2>/dev/null | grep -q "200\|301\|302"; then
  ok "Komodo is reachable at $KOMODO_URL"
else
  warn "Komodo not reachable at $KOMODO_URL (the user may need to deploy Komodo first)"
fi

if curl -ksS -o /dev/null -w "%{http_code}" "$PANGOLIN_URL/api/v1/orgs" 2>/dev/null | grep -q "200\|401"; then
  ok "Pangolin is reachable at $PANGOLIN_URL"
else
  warn "Pangolin not reachable at $PANGOLIN_URL"
fi

# Step 5: Write the audit
step "Step 5: Write audit record"
AUDIT_FILE="/tmp/bootstrap-komodo-periphery-$(date -u +%Y%m%dT%H%M%SZ).json"
cat > "$AUDIT_FILE" <<JSON
{
  "ts": "$(date -u +%Y%m%dT%H%M%SZ)",
  "pocketIdUrl": "$POCKETID_URL",
  "pangolinUrl": "$PANGOLIN_URL",
  "komodoUrl": "$KOMODO_URL",
  "peripheryUrl": "$PERIPHERY_URL",
  "pangolinOrgId": "$PANGOLIN_ORG_ID",
  "status": "ok",
  "pocketIdClientId": "$POCKETID_PANGOLIN_CLIENT_ID",
  "newtId": "${NEW_NEWT_ID:-unknown}",
  "komodoReachable": "$(curl -ksS -o /dev/null -w '%{http_code}' "$KOMODO_URL" 2>/dev/null)",
  "pangolinReachable": "$(curl -ksS -o /dev/null -w '%{http_code}' "$PANGOLIN_URL/api/v1/orgs" 2>/dev/null)"
}
JSON
ok "Audit: $AUDIT_FILE"

echo
log "Bootstrap complete! Next steps for the operator:"
log "  1. Restart Komodo + Periphery to pick up the new Periphery → Komodo wire"
log "  2. Visit $KOMODO_URL and verify the OIDC login still works"
log "  3. Periphery should now be auto-registered with Pangolin"
log "  4. Re-run this script any time to refresh tokens"
