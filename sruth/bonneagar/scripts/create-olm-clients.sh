#!/bin/bash
# =============================================================================
# Create OLM Clients via Dagger
# =============================================================================
# Automates OLM client creation using:
# - Pangolin Integration API for client creation
# - 1Password Connect for credential storage
# - Komodo for stack deployment
#
# PREREQUISITES:
#   1. Newt sites must exist (e.g., arm1-oci-newt, cax41-hetzner-newt)
#   2. 1Password credentials configured
#   3. Komodo API access
#
# USAGE:
#   ./create-olm-clients.sh [--dry-run]
# =============================================================================

set -euo pipefail

# Configuration
DOMAIN="${DOMAIN:-cianfhoghlaim.ie}"
DAGGER_DIR="${DAGGER_DIR:-$(dirname "$0")/../dagger}"

# OLM Client configurations
# Edit this JSON to match your infrastructure
CLIENTS='[
  {
    "name": "arm1-oci-olm",
    "server": "arm1-oci",
    "siteNames": ["arm1-oci-newt"]
  },
  {
    "name": "cax41-hetzner-olm",
    "server": "cax41-hetzner",
    "siteNames": ["cax41-hetzner-newt"]
  }
]'

# Parse arguments
DRY_RUN="false"
while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN="true"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--dry-run]"
      exit 1
      ;;
  esac
done

echo "=== OLM Client Creation ==="
echo "Domain: $DOMAIN"
echo "Dry run: $DRY_RUN"
echo ""

# Check for required tools
if ! command -v op &> /dev/null; then
  echo "Error: 1Password CLI (op) not found"
  exit 1
fi

if ! command -v dagger &> /dev/null; then
  echo "Error: Dagger CLI not found"
  exit 1
fi

# Get secrets from 1Password
echo "Fetching secrets from 1Password..."
export PANGOLIN_TOKEN=$(op read "op://dev-baile/pangolin/api_token")
export KOMODO_API_KEY=$(op read "op://dev-baile/komodo/api_key")
export KOMODO_API_SECRET=$(op read "op://dev-baile/komodo/api_secret")
export OP_CONNECT_TOKEN=$(op read "op://dev-baile/op_connect_cianfhoghlaim/credential")

# SSH key is needed for constructor but not used by createOLMClients
# Use a dummy value since we're not doing SSH operations
export SSH_KEY="unused"

# Verify secrets were retrieved
if [[ -z "$PANGOLIN_TOKEN" ]] || [[ -z "$KOMODO_API_KEY" ]] || [[ -z "$KOMODO_API_SECRET" ]] || [[ -z "$OP_CONNECT_TOKEN" ]]; then
  echo "Error: Failed to retrieve secrets from 1Password"
  echo "Ensure the following items exist in vault 'dev-baile':"
  echo "  - pangolin (with api_token field)"
  echo "  - komodo (with api_key and api_secret fields)"
  echo "  - op_connect_cianfhoghlaim (with credential field)"
  exit 1
fi

echo "Secrets retrieved successfully"
echo ""

# Run Dagger function
echo "Creating OLM clients..."
cd "$DAGGER_DIR"

# Note: PangolinDeployment constructor requires ssh-key and op-connect-token
# even though createOLMClients doesn't use SSH. The op-connect-token is used
# for storing credentials in 1Password.
dagger call pangolin-deployment \
  --target-host "unused@localhost" \
  --domain "$DOMAIN" \
  --ssh-key env:SSH_KEY \
  --op-connect-token env:OP_CONNECT_TOKEN \
  create-olm-clients \
    --pangolin-token env:PANGOLIN_TOKEN \
    --komodo-api-key env:KOMODO_API_KEY \
    --komodo-api-secret env:KOMODO_API_SECRET \
    --clients "$CLIENTS" \
    --dry-run="$DRY_RUN"

echo ""
echo "=== Complete ==="
echo ""
echo "Next steps:"
echo "  1. Verify OLM agents are deployed: komodo stack status olm-oracle olm-hetzner"
echo "  2. Check Pangolin UI for connected OLM clients"
echo "  3. Apply TCP resources blueprint if needed:"
echo "     dagger call apply-blueprint --blueprint-file bonneagar/pangolin/olm-resources.blueprint.yaml"
echo ""
echo "Test connections:"
echo "  SSH Oracle:  ssh -p 22001 user@pangolin.$DOMAIN"
echo "  SSH Hetzner: ssh -p 22002 user@pangolin.$DOMAIN"
