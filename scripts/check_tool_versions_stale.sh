#!/usr/bin/env bash
# scripts/check_tool_versions_stale.sh
#
# Per the 2026-08-23-dev-tooling-version-pinning-v1 change: compare the
# pinned tool ranges in mise.toml against the latest released version
# for each tool, exit 1 if any tool is > 1 major behind.
#
# This is a hygiene check, not a release gate — it gives the dev a
# heads-up that a tool has a new major release available, and is
# tracked in `mise run core:tool-versions:check-stale`.
set -uo pipefail

# The 6 minor-stable tools + 1 major-version-aware tool we care about.
# External infra tools (gh, cloudflared, gcloud, oci, sops, aqua,
# zoxide) are intentionally excluded per the dev-tooling-surfaces spec.
TOOLS=(
    "uv"
    "bun"
    "dagger"
    "pulumi"
    "infisical"
    "duckdb"
    "opencode"
)

STALE=0
WARNINGS=0

echo "=== Tool versions: pinned range vs latest ==="
printf "%-15s %-15s %-15s %s\n" "Tool" "Pinned" "Latest" "Status"
printf -- "-%.0s" {1..70}; echo ""

for tool in "${TOOLS[@]}"; do
    # Read the pinned range from mise.toml (naive but works for our pattern)
    pinned=$(grep -E "^${tool} = " mise.toml | head -1 | sed -E 's/^[^=]+= //; s/"//g')
    if [ -z "$pinned" ]; then
        printf "%-15s %-15s %-15s %s\n" "$tool" "(not found)" "?" "SKIP"
        continue
    fi

    # Query the latest version (skip on network failure)
    latest=$(mise ls-remote "$tool" 2>/dev/null | tail -1 || echo "")
    if [ -z "$latest" ]; then
        printf "%-15s %-15s %-15s %s\n" "$tool" "$pinned" "(no network)" "SKIP"
        continue
    fi

    # Compare major versions (very naive — assumes pinned is caret or tilde)
    # ^X.Y.Z or ~X.Y.Z or X.Y.Z — extract first integer as major
    pinned_major=$(echo "$pinned" | grep -oE "[0-9]+" | head -1)
    latest_major=$(echo "$latest" | grep -oE "[0-9]+" | head -1)
    if [ -z "$pinned_major" ] || [ -z "$latest_major" ]; then
        printf "%-15s %-15s %-15s %s\n" "$tool" "$pinned" "$latest" "PARSE-ERR"
        continue
    fi

    gap=$((latest_major - pinned_major))
    if [ "$gap" -gt 1 ]; then
        printf "%-15s %-15s %-15s %s\n" "$tool" "$pinned" "$latest" "STALE (>1 major)"
        STALE=$((STALE + 1))
    elif [ "$gap" -eq 1 ]; then
        printf "%-15s %-15s %-15s %s\n" "$tool" "$pinned" "$latest" "WARN (1 major behind)"
        WARNINGS=$((WARNINGS + 1))
    else
        printf "%-15s %-15s %-15s %s\n" "$tool" "$pinned" "$latest" "OK"
    fi
done

echo ""
if [ "$STALE" -gt 0 ]; then
    echo "FAIL: $STALE tool(s) are > 1 major behind. Open an openspec change to bump."
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo "WARN: $WARNINGS tool(s) are 1 major behind (not blocking)."
    exit 0
else
    echo "OK: all 7 pinned tools are within 1 major of latest."
    exit 0
fi
