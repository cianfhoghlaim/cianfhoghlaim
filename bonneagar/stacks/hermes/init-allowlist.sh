#!/bin/bash
# =============================================================================
# Hermes — 1-shot allowlist init script
# =============================================================================
# Populates the Hermes `users.allowlist` with the operator's Pocket ID
# subject on day one. Called as a one-shot init container at deploy time
# by the deploy-agent-platform-cluster-bunchloch Komodo procedure.
#
# Usage:
#   HERMES_OPERATOR_POCKET_ID_SUBJECT=oidc-subject-abc-123 \
#   HERMES_API_SERVER_KEY=<admin-token> \
#   HERMES_DASHBOARD_URL=https://hermes.cianfhoghlaim.ie \
#   ./init-allowlist.sh
#
# Exit codes:
#   0 — allowlist populated successfully
#   1 — required env var missing
#   2 — allowlist POST failed
#   3 — smoke test (allowlist test) failed
# =============================================================================

set -euo pipefail

# Required env vars
: "${HERMES_OPERATOR_POCKET_ID_SUBJECT:?HERMES_OPERATOR_POCKET_ID_SUBJECT is required}"
: "${HERMES_API_SERVER_KEY:?HERMES_API_SERVER_KEY is required}"
: "${HERMES_DASHBOARD_URL:?HERMES_DASHBOARD_URL is required (e.g. https://hermes.cianfhoghlaim.ie)}"

echo "[hermes-init-allowlist] operator subject: $HERMES_OPERATOR_POCKET_ID_SUBJECT"
echo "[hermes-init-allowlist] dashboard URL:  $HERMES_DASHBOARD_URL"

# Add the operator to the allowlist
ALLOWLIST_RESPONSE=$(curl -fsS -X POST \
  -H "Authorization: Bearer $HERMES_API_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"subject\": \"$HERMES_OPERATOR_POCKET_ID_SUBJECT\"}" \
  "$HERMES_DASHBOARD_URL/api/users/allowlist")

if [ $? -ne 0 ]; then
  echo "[hermes-init-allowlist] ERROR: allowlist POST failed" >&2
  exit 2
fi

echo "[hermes-init-allowlist] allowlist POST succeeded: $ALLOWLIST_RESPONSE"

# Smoke test: verify the subject is in the allowlist
TEST_RESPONSE=$(curl -fsS -X POST \
  -H "Authorization: Bearer $HERMES_API_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"subject\": \"$HERMES_OPERATOR_POCKET_ID_SUBJECT\"}" \
  "$HERMES_DASHBOARD_URL/api/users/allowlist/test")

if [ $? -ne 0 ]; then
  echo "[hermes-init-allowlist] ERROR: allowlist test POST failed" >&2
  exit 3
fi

if ! echo "$TEST_RESPONSE" | grep -q '"allowed":\s*true'; then
  echo "[hermes-init-allowlist] ERROR: smoke test failed (response: $TEST_RESPONSE)" >&2
  exit 3
fi

echo "[hermes-init-allowlist] OK: subject $HERMES_OPERATOR_POCKET_ID_SUBJECT is in the allowlist"
exit 0
