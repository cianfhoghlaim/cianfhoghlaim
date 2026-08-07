#!/usr/bin/env bash
# =============================================================================
# check-edge-tls.sh — TLS certificate verification gate for edge domains
# =============================================================================
# Shipped by openspec change
#   2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1
#
# Detects the "unable to verify the first certificate" failure mode:
# a Pangolin/Traefik edge serving the self-signed TRAEFIK DEFAULT CERT
# (OpenSSL verify return code 21) instead of a full-chain Let's Encrypt
# certificate.
#
# Usage:
#   bash scripts/check-edge-tls.sh            # check the 4 priority domains
#   bash scripts/check-edge-tls.sh --strict   # exit non-zero on any failure
#   bash scripts/check-edge-tls.sh --all      # also check secondary domains
#
# Exit codes:
#   0 — all checked domains serve verifiable full-chain certificates
#   1 — at least one domain failed verification (with --strict, or always
#       for the priority set when --strict is passed)
# =============================================================================
set -euo pipefail

STRICT=0
ALL=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    --all) ALL=1 ;;
    *) echo "unknown flag: $arg" >&2; exit 2 ;;
  esac
done

# The 4 priority stacks (AGENTS.md priority compose stacks table)
PRIORITY_DOMAINS=(
  "cianfhoghlaim.ie"
  "litellm.cianfhoghlaim.ie"
  "langfuse.cianfhoghlaim.ie"
)
# Secondary domains (checked with --all)
SECONDARY_DOMAINS=(
  "tinyauth.cianfhoghlaim.ie"
  "auth.cianfhoghlaim.ie"
  "openchamber.cianfhoghlaim.ie"
  "openclaw.cianfhoghlaim.ie"
  "hermes.cianfhoghlaim.ie"
  "vikunja.cianfhoghlaim.ie"
  "calcom.cianfhoghlaim.ie"
  "n8n.cianfhoghlaim.ie"
  "komodo.cianfhoghlaim.ie"
  "forgejo.cianfhoghlaim.ie"
)

DOMAINS=("${PRIORITY_DOMAINS[@]}")
if [[ "$ALL" -eq 1 ]]; then
  DOMAINS+=("${SECONDARY_DOMAINS[@]}")
fi

FAILURES=0
PRIORITY_FAILURES=0

check_domain() {
  local domain="$1"
  local is_priority="$2"
  local out subject verify_code

  # Resolve first (a domain that does not resolve is a different failure mode)
  if ! dig +short "$domain" >/dev/null 2>&1; then
    printf "  %-38s DNS-ERROR (no answer)\n" "$domain"
    FAILURES=$((FAILURES + 1))
    [[ "$is_priority" -eq 1 ]] && PRIORITY_FAILURES=$((PRIORITY_FAILURES + 1))
    return
  fi

  out="$(echo | openssl s_client -connect "$domain:443" -servername "$domain" 2>/dev/null || true)"
  if [[ -z "$out" ]]; then
    printf "  %-38s CONNECT-ERROR (no TLS handshake)\n" "$domain"
    FAILURES=$((FAILURES + 1))
    [[ "$is_priority" -eq 1 ]] && PRIORITY_FAILURES=$((PRIORITY_FAILURES + 1))
    return
  fi

  subject="$(printf '%s\n' "$out" | grep -m1 '^ 0 s:' | sed 's/^ 0 s://' || true)"
  verify_code="$(printf '%s\n' "$out" | grep -m1 'Verify return code:' | sed 's/.*Verify return code: //' || true)"

  if [[ "$verify_code" == 0* ]]; then
    printf "  %-38s OK        (%s)\n" "$domain" "${subject:-unknown}"
  else
    printf "  %-38s FAIL      code=%s subject=%s\n" "$domain" "${verify_code:-?}" "${subject:-unknown}"
    FAILURES=$((FAILURES + 1))
    [[ "$is_priority" -eq 1 ]] && PRIORITY_FAILURES=$((PRIORITY_FAILURES + 1))
  fi
}

echo "Edge TLS verification — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo
echo "Priority domains:"
for d in "${PRIORITY_DOMAINS[@]}"; do
  check_domain "$d" 1
done

if [[ "$ALL" -eq 1 ]]; then
  echo
  echo "Secondary domains:"
  for d in "${SECONDARY_DOMAINS[@]}"; do
    check_domain "$d" 0
  done
fi

echo
if [[ "$FAILURES" -eq 0 ]]; then
  echo "RESULT: PASS — all ${#DOMAINS[@]} checked domains serve verifiable certificates."
  exit 0
fi

echo "RESULT: FAIL — $FAILURES domain(s) failed TLS verification ($PRIORITY_FAILURES priority)."
echo
echo "Likely cause (verify code 21, 'unable to verify the first certificate'):"
echo "  Traefik is serving the self-signed TRAEFIK DEFAULT CERT because the ACME"
echo "  resolver did not issue a Let's Encrypt certificate. Remediation:"
echo "  1. On arm1-oci, check /opt/pangolin/config/traefik/traefik_config.yml:"
echo "     the certificatesResolvers name MUST match the certResolver referenced"
echo "     by each stack's pangolin.yaml (currently 'letsencrypt')."
echo "  2. Ensure CLOUDFLARE_DNS_API_TOKEN is set in /opt/pangolin/.env (DNS-01)."
echo "  3. docker restart traefik (in the pangolin stack), then re-run this script."
echo "  Full runbook: openspec/changes/2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1/tasks.md"

if [[ "$STRICT" -eq 1 ]]; then
  exit 1
fi
exit 0
