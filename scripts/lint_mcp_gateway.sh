#!/usr/bin/env bash
# lint_mcp_gateway.sh — verify the phantom MCP gateway at
# web/apps/croilar-portal/src/routes/api/mcp.gateway.ts carries the
# KNOWN-ISSUE header + TODO(mcp-bridge) marker.
#
# Per openspec/changes/2026-08-21-document-phantom-mcp-gateway-gap-v1/
# Exits 0 if both markers are present, 1 otherwise.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATEWAY="${REPO_ROOT}/web/apps/croilar-portal/src/routes/api/mcp.gateway.ts"

if [ ! -f "${GATEWAY}" ]; then
    echo "FAIL: ${GATEWAY} not found"
    exit 1
fi

errors=0

# Check 1: KNOWN-ISSUE comment block
if ! grep -q "KNOWN-ISSUE (2026-08-21)" "${GATEWAY}"; then
    echo "FAIL: missing KNOWN-ISSUE (2026-08-21) comment block in mcp.gateway.ts"
    echo "      See: openspec/changes/2026-08-21-document-phantom-mcp-gateway-gap-v1/"
    errors=$((errors + 1))
fi

# Check 2: TODO(mcp-bridge) marker on the fetch() line
if ! grep -q "TODO(mcp-bridge)" "${GATEWAY}"; then
    echo "FAIL: missing TODO(mcp-bridge) marker in mcp.gateway.ts"
    echo "      The \${LITELLM_BASE_URL}/mcp/\${server} fetch() call must be marked"
    errors=$((errors + 1))
fi

# Check 3: LITELLM_BASE_URL must be present (the phantom reference)
if ! grep -q "LITELLM_BASE_URL" "${GATEWAY}"; then
    echo "INFO: LITELLM_BASE_URL not found in mcp.gateway.ts — phantom may have been replaced"
fi

if [ ${errors} -eq 0 ]; then
    echo "OK: mcp.gateway.ts has KNOWN-ISSUE + TODO(mcp-bridge) markers"
    exit 0
else
    echo "FAIL: ${errors} marker(s) missing"
    exit 1
fi