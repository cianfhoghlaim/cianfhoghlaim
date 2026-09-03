#!/bin/bash
# bons IaC setup helper for arm1-oci production env
# Source this to load all env vars the bons IaC needs to talk to arm1-oci.
# Usage: source ./setup-iac-env.sh

# The .env at /Users/cianmacandeisigh/dev/kings_college_galway/.env has the bulk
# of the credentials already. We just need to override the URLs to point to arm1-oci.

# The cianfhoghlaim root .env (shared with all bons worktrees)
if [ -f /Users/cianmacandeisigh/dev/kings_college_galway/.env ]; then
  set -a
  source /Users/cianmacandeisigh/dev/kings_college_galway/.env
  set +a
else
  echo "ERROR: /Users/cianmacandeisigh/dev/kings_college_galway/.env not found" >&2
  return 1 2>/dev/null || exit 1
fi

# Override URLs to point to arm1-oci (production)
# (the bons IaC's defaults are mixed — Infisical defaults to localhost dev,
#  Komodo defaults to localhost:9120, Pocket ID + Pangolin default to arm1-oci)
export POCKETID_URL=https://auth.cianfhoghlaim.ie
export KOMODO_URL=https://komodo.cianfhoghlaim.ie
export PANGOLIN_URL=https://pangolin.cianfhoghlaim.ie
export PANGOLIN_API_BASE=https://pangolin.cianfhoghlaim.ie/v1
export INFISICAL_URL=https://infisical.cianfhoghlaim.ie

# Defaults for the bons IaC
export IAC_DRY_RUN=false
export IAC_VERBOSE=false

echo "bons IaC env loaded for arm1-oci production:"
echo "  POCKETID_URL=$POCKETID_URL"
echo "  KOMODO_URL=$KOMODO_URL"
echo "  PANGOLIN_URL=$PANGOLIN_URL"
echo "  INFISICAL_URL=$INFISICAL_URL"
echo ""
echo "  Required env vars:"
echo "    POCKETID_API_KEY               = ${POCKETID_API_KEY:0:8}..."
echo "    POCKETID_PANGOLIN_CLIENT_ID    = ${POCKETID_PANGOLIN_CLIENT_ID}"
echo "    POCKETID_PANGOLIN_CLIENT_SECRET = ${POCKETID_PANGOLIN_CLIENT_SECRET:0:8}..."
echo "    POCKETID_BONS_IAC_CLIENT_ID    = ${POCKETID_BONS_IAC_CLIENT_ID}"
echo "    POCKETID_BONS_IAC_CLIENT_SECRET = ${POCKETID_BONS_IAC_CLIENT_SECRET:0:8}..."
echo "    POCKETID_TINYAUTH_CLIENT_ID    = ${POCKETID_TINYAUTH_CLIENT_ID}"
echo "    POCKETID_TINYAUTH_CLIENT_SECRET = ${POCKETID_TINYAUTH_CLIENT_SECRET:0:8}..."
echo "    PANGOLIN_API_KEY               = ${PANGOLIN_API_KEY:0:16}..."
echo "    INFISICAL_UNIVERSAL_AUTH_CLIENT_ID  = ${INFISICAL_UNIVERSAL_AUTH_CLIENT_ID}"
echo "    INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET = ${INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET:0:12}..."
echo "    INFISICAL_PROJECT_ID           = $INFISICAL_PROJECT_ID"
