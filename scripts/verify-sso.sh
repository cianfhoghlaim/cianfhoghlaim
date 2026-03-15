#!/bin/bash
# =============================================================================
# SSO Verification Script for Pangolin Services
# =============================================================================
# Verifies SSO configuration for services deployed via Pangolin/PocketID.
# Tests OIDC discovery, redirect flow, and OAuth client registration.
#
# Usage:
#   ./verify-sso.sh [service-domain] [--verbose]
#   ./verify-sso.sh llm.cianfhoghlaim.ie
#   ./verify-sso.sh langfuse.cianfhoghlaim.ie --verbose
#
# Requirements:
#   - curl, jq
#   - 1Password CLI (op) for OAuth client verification
# =============================================================================

set -euo pipefail

# Configuration
SERVICE="${1:-llm.cianfhoghlaim.ie}"
AUTH_DOMAIN="auth.cianfhoghlaim.ie"
VERBOSE="${2:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; }

echo "=============================================="
echo "SSO Verification for: $SERVICE"
echo "Auth Domain: $AUTH_DOMAIN"
echo "=============================================="
echo ""

# Track overall status
OVERALL_STATUS=0

# =============================================================================
# Test 1: OIDC Discovery Endpoint
# =============================================================================
log_info "Checking OIDC discovery endpoint..."

OIDC_CONFIG=$(curl -sf "https://$AUTH_DOMAIN/.well-known/openid-configuration" 2>/dev/null || echo "FAILED")

if [ "$OIDC_CONFIG" = "FAILED" ]; then
  log_fail "OIDC discovery endpoint unreachable"
  OVERALL_STATUS=1
else
  AUTH_ENDPOINT=$(echo "$OIDC_CONFIG" | jq -r '.authorization_endpoint // "missing"')
  TOKEN_ENDPOINT=$(echo "$OIDC_CONFIG" | jq -r '.token_endpoint // "missing"')
  USERINFO_ENDPOINT=$(echo "$OIDC_CONFIG" | jq -r '.userinfo_endpoint // "missing"')

  if [ "$AUTH_ENDPOINT" != "missing" ] && [ "$TOKEN_ENDPOINT" != "missing" ]; then
    log_ok "OIDC discovery OK"
    if [ -n "$VERBOSE" ]; then
      echo "    Authorization: $AUTH_ENDPOINT"
      echo "    Token: $TOKEN_ENDPOINT"
      echo "    UserInfo: $USERINFO_ENDPOINT"
    fi
  else
    log_fail "OIDC discovery missing required endpoints"
    OVERALL_STATUS=1
  fi
fi
echo ""

# =============================================================================
# Test 2: Service Health Check
# =============================================================================
log_info "Checking service health at https://$SERVICE..."

# Try common health endpoints
HEALTH_OK=false
for endpoint in "/health" "/api/health" "/healthz" "/" ""; do
  HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "https://$SERVICE$endpoint" 2>/dev/null || echo "000")
  if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "301" ]; then
    HEALTH_OK=true
    log_ok "Service reachable (HTTP $HTTP_CODE at $endpoint)"
    break
  fi
done

if [ "$HEALTH_OK" = false ]; then
  # Try localhost for local development
  HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "http://localhost:4000/health" 2>/dev/null || echo "000")
  if [ "$HTTP_CODE" = "200" ]; then
    log_ok "Service reachable locally (localhost:4000)"
    HEALTH_OK=true
  else
    log_warn "Service not reachable at https://$SERVICE (may be local-only)"
  fi
fi
echo ""

# =============================================================================
# Test 3: SSO Redirect Flow
# =============================================================================
log_info "Checking SSO redirect flow..."

# Check if UI endpoint redirects to auth
REDIRECT_HEADERS=$(curl -sI "https://$SERVICE/ui" 2>&1 || curl -sI "http://localhost:4000/ui" 2>&1 || echo "")
LOCATION=$(echo "$REDIRECT_HEADERS" | grep -i "^location:" | head -1 | tr -d '\r')

if [ -n "$LOCATION" ]; then
  if echo "$LOCATION" | grep -qi "$AUTH_DOMAIN"; then
    log_ok "SSO redirect configured correctly"
    if [ -n "$VERBOSE" ]; then
      echo "    Redirect: $LOCATION"
    fi
  elif echo "$LOCATION" | grep -qi "authorize"; then
    log_ok "SSO redirect to authorization endpoint"
    if [ -n "$VERBOSE" ]; then
      echo "    Redirect: $LOCATION"
    fi
  else
    log_warn "Redirect found but not to $AUTH_DOMAIN"
    if [ -n "$VERBOSE" ]; then
      echo "    Redirect: $LOCATION"
    fi
  fi
else
  # Check if SSO is enabled via API (LiteLLM specific)
  SSO_SETTINGS=$(curl -sf "http://localhost:4000/sso/get/ui_settings" 2>/dev/null || echo "{}")
  SSO_ENABLED=$(echo "$SSO_SETTINGS" | jq -r '.SSO_ENABLED // false')

  if [ "$SSO_ENABLED" = "true" ]; then
    log_ok "SSO enabled (verified via API)"
  else
    log_warn "No SSO redirect detected (may require authentication first)"
  fi
fi
echo ""

# =============================================================================
# Test 4: OAuth Client Verification (requires 1Password CLI)
# =============================================================================
log_info "Checking OAuth client registration..."

# Extract service name from domain
SERVICE_NAME=$(echo "$SERVICE" | cut -d. -f1)

if command -v op &> /dev/null; then
  # Try to get PocketID API key
  POCKETID_TOKEN=$(env -u OP_CONNECT_HOST -u OP_CONNECT_TOKEN op read "op://dev-baile/pocketid/api_key" 2>/dev/null || echo "")

  if [ -n "$POCKETID_TOKEN" ]; then
    # List OAuth clients from PocketID
    CLIENTS=$(curl -sf "https://$AUTH_DOMAIN/api/oidc/clients" \
      -H "X-API-Key: $POCKETID_TOKEN" 2>/dev/null || echo "[]")

    if echo "$CLIENTS" | jq -e '.' > /dev/null 2>&1; then
      # Search for matching client (case-insensitive)
      MATCHING_CLIENT=$(echo "$CLIENTS" | jq -r ".[] | select(.name | ascii_downcase | contains(\"$SERVICE_NAME\")) | .name" | head -1)

      if [ -n "$MATCHING_CLIENT" ]; then
        log_ok "OAuth client found: $MATCHING_CLIENT"
        if [ -n "$VERBOSE" ]; then
          CLIENT_ID=$(echo "$CLIENTS" | jq -r ".[] | select(.name == \"$MATCHING_CLIENT\") | .id")
          echo "    Client ID: $CLIENT_ID"
        fi
      else
        log_warn "No OAuth client found matching '$SERVICE_NAME'"
        if [ -n "$VERBOSE" ]; then
          echo "    Available clients:"
          echo "$CLIENTS" | jq -r '.[].name' | sed 's/^/      - /'
        fi
      fi
    else
      log_warn "Could not parse OAuth clients response"
    fi
  else
    log_warn "PocketID API key not available in 1Password"
  fi
else
  log_warn "1Password CLI (op) not installed - skipping OAuth client check"
fi
echo ""

# =============================================================================
# Test 5: Check 1Password Items (service credentials)
# =============================================================================
log_info "Checking 1Password credential items..."

if command -v op &> /dev/null; then
  ITEMS_FOUND=0
  ITEMS_MISSING=0

  # Check for common credential items
  for item in "$SERVICE_NAME" "$SERVICE_NAME-pocketid" "$SERVICE_NAME-postgres"; do
    if env -u OP_CONNECT_HOST -u OP_CONNECT_TOKEN op item get "$item" --vault dev-baile --format=json > /dev/null 2>&1; then
      ((ITEMS_FOUND++))
      if [ -n "$VERBOSE" ]; then
        echo "    Found: $item"
      fi
    else
      ((ITEMS_MISSING++))
    fi
  done

  if [ $ITEMS_FOUND -gt 0 ]; then
    log_ok "Found $ITEMS_FOUND credential items in 1Password"
  else
    log_warn "No credential items found for $SERVICE_NAME"
  fi
else
  log_warn "1Password CLI not available - skipping credential check"
fi
echo ""

# =============================================================================
# Summary
# =============================================================================
echo "=============================================="
if [ $OVERALL_STATUS -eq 0 ]; then
  log_ok "SSO verification completed successfully"
else
  log_fail "SSO verification completed with errors"
fi
echo "=============================================="

# Return status for scripting
exit $OVERALL_STATUS
