#!/usr/bin/env bash
# =============================================================================
# bootstrap-pocket-id.sh
# =============================================================================
# Idempotent: re-runnable. Recreates the OIDC client + API key if missing.
#
# What it does:
#   1. SSHes to arm1-oci
#   2. Inspects pocket-id db for user + OIDC client + API key state
#   3. Creates user `ciandeacy` (admin) if missing
#   4. Creates API key `agent-bootstrap` if missing
#   5. Creates OIDC client `pocketid-team-workflow` with wildcards for all
#      team-workflow callback URLs
#   6. Prints the client_id and client_secret (caller saves to Infisical)
#
# Usage:
#   ./scripts/bootstrap-pocket-id.sh           # idempotent
#   ./scripts/bootstrap-pocket-id.sh --reset   # nukes db and starts fresh
# =============================================================================

set -euo pipefail

POCKET_ID_URL="https://auth.cianfhoghlaim.ie"
POCKET_ID_API_KEY="pidk_agent_bootstrap_a9f4d0e3f8c2g5h7i9k1m3n6q9r2t4v7w0x3y6z9c2d5e8f1g4h7i0j3k6l2m5n8"
OIDC_CLIENT_ID="pocketid-team-workflow"
OIDC_CLIENT_NAME="Team Workflow SSO"
SSH_TARGET="oci.arm1"
RESET=false

for arg in "$@"; do
    case $arg in
        --reset) RESET=true ;;
    esac
done

if [[ "$RESET" == "true" ]]; then
    echo "⚠️  Resetting pocket-id database (--reset)"
    ssh -i /Users/cianmacandeisigh/.oci/sessions/DEFAULT/oci_api_key.pem "$SSH_TARGET" \
        "sudo sqlite3 /var/lib/docker/volumes/pocket-id-data/_data/pocket-id.db \
            'DELETE FROM webauthn_sessions; DELETE FROM oidc_authorization_codes; \
             DELETE FROM oidc_refresh_tokens; DELETE FROM one_time_access_tokens; \
             DELETE FROM api_keys; DELETE FROM oidc_clients; \
             DELETE FROM users; DELETE FROM user_groups_users; \
             DELETE FROM user_groups;' 2>&1"
fi

echo "🔍 Checking pocket-id state on $SSH_TARGET..."

# Bootstrap: ensure user ciandeacy (admin) exists
echo "→ Checking user ciandeacy..."
ssh -i /Users/cianmacandeisigh/.oci/sessions/DEFAULT/oci_api_key.pem "$SSH_TARGET" \
    "sudo sqlite3 /var/lib/docker/volumes/pocket-id-data/_data/pocket-id.db <<'SQL'
INSERT OR IGNORE INTO users
  (id, created_at, updated_at, username, email, first_name, last_name, display_name, is_admin)
VALUES ('9bdfebf5-3ce7-4a44-89cd-22125e6accd3', datetime('now'), datetime('now'),
        'cianfhoghlaim', 'cian.deacy@icloud.com', 'Cian', 'Deacy', 'Cian Deacy', 1);
UPDATE users SET is_admin=1 WHERE username='cianfhoghlaim';
SQL"

# Bootstrap: ensure API key exists with SHA256 hash
echo "→ Checking API key..."
HASH=$(echo -n "$POCKET_ID_API_KEY" | sha256sum | cut -d' ' -f1)
ssh -i /Users/cianmacandeisigh/.oci/sessions/DEFAULT/oci_api_key.pem "$SSH_TARGET" \
    "sudo sqlite3 /var/lib/docker/volumes/pocket-id-data/_data/pocket-id.db <<SQL
INSERT OR REPLACE INTO api_keys
  (id, name, key, description, expires_at, last_used_at, created_at, user_id, expiration_email_sent)
VALUES ('11111111-1111-1111-1111-111111111111', 'agent-bootstrap',
        '$HASH', 'Agent API key for programmatic access to pocket-id',
        '2030-12-31 23:59:59', NULL, datetime('now'),
        '9bdfebf5-3ce7-4a44-89cd-22125e6accd3', 0);
SQL"

# Check OIDC client via API
echo "→ Checking OIDC client '$OIDC_CLIENT_ID'..."
EXISTING=$(curl -s -H "X-API-KEY: $POCKET_ID_API_KEY" \
    "$POCKET_ID_URL/api/oidc/clients" | \
    python3 -c "import sys, json; data = json.load(sys.stdin)['data']; print(any(c['id'] == '$OIDC_CLIENT_ID' for c in data))" 2>/dev/null)

if [[ "$EXISTING" == "True" ]]; then
    echo "  ✓ OIDC client exists. Rotating secret for safety..."
    SECRET=$(curl -s -X POST -H "X-API-KEY: $POCKET_ID_API_KEY" \
        "$POCKET_ID_URL/api/oidc/clients/$OIDC_CLIENT_ID/secret" | \
        python3 -c "import sys, json; print(json.load(sys.stdin)['secret'])")
else
    echo "  → Creating OIDC client '$OIDC_CLIENT_ID'..."
    CREATE_RESP=$(curl -s -X POST -H "X-API-KEY: $POCKET_ID_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"id\": \"$OIDC_CLIENT_ID\",
            \"name\": \"$OIDC_CLIENT_NAME\",
            \"callbackURLs\": [
                \"https://vikunja.cianfhoghlaim.ie/auth/openid/pocketid\",
                \"https://n8n.cianfhoghlaim.ie/*\",
                \"https://calcom.cianfhoghlaim.ie/*\",
                \"https://paperless.cianfhoghlaim.ie/*\",
                \"https://glance.cianfhoghlaim.ie/*\",
                \"https://changedetection.cianfhoghlaim.ie/*\"
            ],
            \"logoutCallbackURLs\": [
                \"https://vikunja.cianfhoghlaim.ie/auth/openid/pocketid\",
                \"https://n8n.cianfhoghlaim.ie/*\",
                \"https://calcom.cianfhoghlaim.ie/*\",
                \"https://paperless.cianfhoghlaim.ie/*\",
                \"https://glance.cianfhoghlaim.ie/*\",
                \"https://changedetection.cianfhoghlaim.ie/*\"
            ],
            \"isPublic\": false,
            \"pkceEnabled\": true,
            \"credentials\": { \"federatedIdentities\": [] }
        }" \
        "$POCKET_ID_URL/api/oidc/clients")
    echo "  → Generating secret..."
    SECRET=$(curl -s -X POST -H "X-API-KEY: $POCKET_ID_API_KEY" \
        "$POCKET_ID_URL/api/oidc/clients/$OIDC_CLIENT_ID/secret" | \
        python3 -c "import sys, json; print(json.load(sys.stdin)['secret'])")
fi

cat <<EOF

╔══════════════════════════════════════════════════════════════════════════════╗
║                    POCKET-ID OIDC CLIENT BOOTSTRAPPED                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

  OIDC Client ID:     $OIDC_CLIENT_ID
  OIDC Client Secret: $SECRET

  Issuer URL:         $POCKET_ID_URL
  Discovery:          $POCKET_ID_URL/.well-known/openid-configuration
  JWKS:               $POCKET_ID_URL/.well-known/jwks.json
  Authorization:      $POCKET_ID_URL/authorize
  Token:              $POCKET_ID_URL/api/oidc/token
  Userinfo:           $POCKET_ID_URL/api/oidc/userinfo

  Admin API Key:      $POCKET_ID_API_KEY
                      (use as X-API-KEY header)

  Next steps:
  ─────────
  1. Update Infisical: paste client_secret into dev-baile/pocketid-team-workflow/client_secret
  2. Update vikunja/n8n/cal-diy compose to use OIDC_SCOPE=openid profile email
  3. Add passkey for user ciandeacy via https://auth.cianfhoghlaim.ie/settings/account
     (requires browser session + WebAuthn authenticator)

EOF
