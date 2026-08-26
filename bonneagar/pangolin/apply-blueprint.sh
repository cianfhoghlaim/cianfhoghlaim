#!/usr/bin/env bash
# =============================================================================
# Apply a Pangolin blueprint (declarative private/proxy resource definitions).
# =============================================================================
# Pangolin's blueprint endpoint reconciles: for every resource in the file it
# rewrites site bindings and user/client grants to match. Re-applying an
# unchanged file is a no-op, which is what makes this safe to run repeatedly.
#
# USAGE
#   export PANGOLIN_API_KEY='<apiKeyId>.<apiKeySecret>'
#   ./apply-blueprint.sh                                  # default file
#   ./apply-blueprint.sh private-resources.blueprint.yaml
#
# ENVIRONMENT
#   PANGOLIN_API_KEY  required. Format "{apiKeyId}.{apiKeySecret}".
#   PANGOLIN_API      default https://pangolin.cianfhoghlaim.ie/v1
#   PANGOLIN_ORG_ID   default cianfhoghlaim
#
# The endpoint takes base64-encoded *JSON*, despite blueprints being authored
# and displayed as YAML in the Pangolin UI (the UI converts before sending).
# Posting base64 YAML fails with:
#   "Failed to update database from config: SyntaxError: Unexpected token '#'"
# so this script converts YAML -> JSON first.
#
# REQUIRES: python3 with PyYAML (pip install pyyaml).
# =============================================================================
set -euo pipefail

BLUEPRINT="${1:-$(dirname "$0")/private-resources.blueprint.yaml}"
API="${PANGOLIN_API:-https://pangolin.cianfhoghlaim.ie/v1}"
ORG="${PANGOLIN_ORG_ID:-cianfhoghlaim}"

if [[ -z "${PANGOLIN_API_KEY:-}" ]]; then
  echo "error: PANGOLIN_API_KEY is not set." >&2
  echo "       Expected format: {apiKeyId}.{apiKeySecret}" >&2
  exit 1
fi

if [[ ! -f "$BLUEPRINT" ]]; then
  echo "error: blueprint not found: $BLUEPRINT" >&2
  exit 1
fi

# -----------------------------------------------------------------------------
# PRE-FLIGHT
# -----------------------------------------------------------------------------
# Validate against live org state before sending anything. Set SKIP_PREFLIGHT=1
# to bypass (not recommended).
if [[ "${SKIP_PREFLIGHT:-}" != "1" ]]; then
  echo "Pre-flight ..."
  PF_DIR="$(dirname "$0")"
  SITES_JSON="$(curl -sS -H "Authorization: Bearer $PANGOLIN_API_KEY" "$API/org/$ORG/sites" || echo '{}')"
  CLIENTS_JSON="$(curl -sS -H "Authorization: Bearer $PANGOLIN_API_KEY" "$API/org/$ORG/clients" || echo '{}')"
  USERS_JSON="$(curl -sS -H "Authorization: Bearer $PANGOLIN_API_KEY" "$API/org/$ORG/users" || echo '{}')"

  if ! python3 "$PF_DIR/preflight-blueprint.py" \
        "$BLUEPRINT" "$SITES_JSON" "$CLIENTS_JSON" "$USERS_JSON"; then
    echo "Pre-flight failed; nothing was applied." >&2
    exit 1
  fi
  echo "  pre-flight OK"
fi

# YAML -> JSON -> base64. `base64 -w0` is GNU-only, so encode in Python to
# keep this portable across macOS/BSD and Linux.
ENCODED="$(python3 -c '
import base64, json, sys, yaml
with open(sys.argv[1]) as fh:
    doc = yaml.safe_load(fh)
print(base64.b64encode(json.dumps(doc).encode()).decode())
' "$BLUEPRINT")"

echo "Applying $(basename "$BLUEPRINT") to org '$ORG' at $API ..."

RESPONSE="$(curl -sS -X PUT "$API/org/$ORG/blueprint" \
  -H "Authorization: Bearer $PANGOLIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"blueprint\": \"$ENCODED\"}")"

echo "$RESPONSE"

# Pangolin returns HTTP 200 even when individual resources fail to apply; the
# real outcome is in the JSON body. Fail loudly rather than reporting success
# on a blueprint that silently did nothing.
if printf '%s' "$RESPONSE" | grep -q '"success":true'; then
  if printf '%s' "$RESPONSE" | grep -qi 'with errors'; then
    echo "FAILED: applied with errors (see message above)." >&2
    exit 1
  fi
  echo "OK: blueprint applied."
else
  echo "FAILED: blueprint was not applied." >&2
  exit 1
fi
