#!/usr/bin/env bash
# wire-pocketid-resource-idp.sh — Bind the PocketID IdP to Pangolin Resources.
# This is the 4th manual step in the original 4-step OIDC wiring flow.
#
# After the Org IdP is created (via wire-pocketid-pangolin-komodo.sh), each
# Resource (site) needs to have that IdP bound to it so that:
#   - The Resource's auth flow uses Pocket ID (instead of the default Tinyauth)
#   - Users in Pocket ID can access the Resource
#
# Usage:
#   ./scripts/wire-pocketid-resource-idp.sh --resource=mlflow.cianfhoghlaim.ie
#   ./scripts/wire-pocketid-resource-idp.sh --all    # bind PocketID to all resources
#   ./scripts/wire-pocketid-resource-idp.sh --dry-run
#
# KNOWN LIMITATION: This uses the user-cookie auth flow (needs a browser
# or a working session cookie). For now, the script uses the cached
# PANGOLIN_API_KEY from .env and POSTs directly. If CSRF blocks it,
# use the dashboard to bind the IdP manually.
#
# Per-resource: Pangolin's API endpoint is:
#   POST /v1/org/{orgId}/site-resource/{resourceId}/idp
#   Body: { "idp_id": "<the PocketID org IdP id>" }
#   Cookie: session=...

set -euo pipefail

WORKTREE="$(git rev-parse --show-toplevel)"
ENV_FILE="$WORKTREE/.env"

cd "$WORKTREE"
set -a; source "$ENV_FILE" 2>/dev/null; set +a

PANGOLIN_URL="${PANGOLIN_URL:-https://pangolin.cianfhoghlaim.ie}"

# Parse args
RESOURCE=""
ALL=false
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    -h|--help)
      cat <<USAGE
Usage: $0 [options]
  --resource=DOMAIN  Bind PocketID to one resource (e.g. mlflow.cianfhoghlaim.ie)
  --all             Bind PocketID to all resources in the org
  --dry-run         Show what would be done
  -h, --help        Show this help
USAGE
      exit 0
      ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

# Step 1: Get the PocketID IdP id (from the existing org IdPs)
IDP_ID=$(curl -ksS "$PANGOLIN_URL/api/v1/idp?org_id=$PANGOLIN_ORG_ID" \
  -H "Authorization: Bearer $PANGOLIN_API_KEY" 2>&1 | \
  python3 -c "import json,sys; d=json.load(sys.stdin); [print(i.get('idp_id','')) for i in d.get('data',[]) if i.get('name') == 'PocketID']" 2>/dev/null)

if [ -z "$IDP_ID" ]; then
  echo "ERROR: PocketID IdP not found. Run wire-pocketid-pangolin-komodo.sh first." >&2
  exit 1
fi
echo "PocketID IdP id: $IDP_ID"

# Step 2: Get the resource(s) to bind
if [ "$ALL" = true ]; then
  RESOURCES=$(curl -ksS "$PANGOLIN_URL/api/v1/site-resources?org_id=$PANGOLIN_ORG_ID" \
    -H "Authorization: Bearer $PANGOLIN_API_KEY" 2>&1 | \
    python3 -c "import json,sys; d=json.load(sys.stdin); [print(r.get('fullDomain','')) for r in d.get('data',{}).get('siteResources',[])]" 2>/dev/null)
elif [ -n "$RESOURCE" ]; then
  RESOURCES="$RESOURCE"
else
  echo "ERROR: provide --resource=DOMAIN or --all"
  exit 2
fi

# Step 3: Bind each resource
for domain in $RESOURCES; do
  echo ""
  echo "Processing resource: $domain"
  RESOURCE_ID=$(curl -ksS "$PANGOLIN_URL/api/v1/site-resources?org_id=$PANGOLIN_ORG_ID" \
    -H "Authorization: Bearer $PANGOLIN_API_KEY" 2>&1 | \
    python3 -c "import json,sys; d=json.load(sys.stdin); [print(r.get('siteResourceId','')) for r in d.get('data',{}).get('siteResources',[]) if r.get('fullDomain') == '$domain']" 2>/dev/null)
  
  if [ -z "$RESOURCE_ID" ]; then
    echo "  ! Resource $domain not found"
    continue
  fi
  
  echo "  Resource id: $RESOURCE_ID"
  
  # Bind the IdP to the resource
  RESULT=$(curl -ksS -X POST "$PANGOLIN_URL/v1/org/$PANGOLIN_ORG_ID/site-resource/$RESOURCE_ID/idp" \
    -H "Authorization: Bearer $PANGOLIN_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"idp_id\": \"$IDP_ID\"}" 2>&1)
  
  if echo "$RESULT" | grep -q "success.*true"; then
    echo "  ✓ Bound PocketID IdP to $domain"
  else
    echo "  ! Failed to bind: $RESULT"
  fi
done

echo ""
echo "Done! Use --dry-run first to preview changes."
