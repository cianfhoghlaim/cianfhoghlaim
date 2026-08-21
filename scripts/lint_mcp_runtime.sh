#!/usr/bin/env bash
# lint_mcp_runtime.sh — verify every `enabled: true` MCP entry in
# opencode.json has a corresponding mcp:smoke:<name> task in mise.toml.
#
# Per openspec/changes/2026-08-21-fix-wired-but-unloaded-mcps-v1/
# Exits 0 if every enabled MCP has a smoke task, 1 otherwise.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OPENCODE_JSON="${REPO_ROOT}/opencode.json"
MISE_TOML="${REPO_ROOT}/mise.toml"

if [ ! -f "${OPENCODE_JSON}" ]; then
    echo "FAIL: ${OPENCODE_JSON} not found"
    exit 1
fi

if [ ! -f "${MISE_TOML}" ]; then
    echo "FAIL: ${MISE_TOML} not found"
    exit 1
fi

# Parse enabled MCP server names from opencode.json using bun (already on PATH).
# Falls back to jq if bun is unavailable.
get_enabled_mcps() {
    if command -v jq >/dev/null 2>&1; then
        jq -r '.mcp // {} | to_entries[] | select(.value.enabled == true) | .key' "${OPENCODE_JSON}"
    elif command -v bun >/dev/null 2>&1; then
        bun -e "const j = await Bun.file('${OPENCODE_JSON}').json(); for (const [k, v] of Object.entries(j.mcp ?? {})) if (v.enabled === true) console.log(k);"
    else
        echo "ERROR: neither jq nor bun on PATH" >&2
        return 1
    fi
}

errors=0
mcp_count=0

while IFS= read -r mcp_name; do
    [ -z "${mcp_name}" ] && continue
    mcp_count=$((mcp_count + 1))

    # Check for a corresponding mcp:smoke:<name> task in mise.toml
    if grep -qE "^\[tasks\.?\"mcp:smoke:${mcp_name}\"\]|^\[tasks\.?\"mcp:smoke:${mcp_name}:" "${MISE_TOML}"; then
        echo "OK: mcp:smoke:${mcp_name} task found"
    else
        echo "FAIL: no smoke task for enabled MCP '${mcp_name}'"
        echo "      Add [tasks.\"mcp:smoke:${mcp_name}\"] to mise.toml"
        errors=$((errors + 1))
    fi
done < <(get_enabled_mcps)

if [ ${mcp_count} -eq 0 ]; then
    echo "WARN: no enabled MCPs found in opencode.json (skipping)"
    exit 0
fi

if [ ${errors} -eq 0 ]; then
    echo "OK: all ${mcp_count} enabled MCPs have smoke tasks"
    exit 0
else
    echo "FAIL: ${errors} missing smoke task(s) across ${mcp_count} enabled MCPs"
    exit 1
fi