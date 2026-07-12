#!/usr/bin/env bash
# infrastructure/audit/scripts/probe-public-urls.sh
# ---------------------------------------------------------------------------
# Probe the public Pangolin-routable `*.cianfhoghlaim.ie` URLs.
# Reads `infrastructure/pangolin/a2a-resources.blueprint.yaml`
# and for each `full-domain`, issues a HEAD + GET, then prints a
# table of (url, status, time).
#
# This is documentation/audit content. It does NOT call any
# deploy API. It is safe to run any time.
#
# Usage:
#   bash infrastructure/audit/scripts/probe-public-urls.sh
#   bash infrastructure/audit/scripts/probe-public-urls.sh --blueprint <path>
#
# Exit codes:
#   0  - all probed URLs returned 2xx / 3xx / 4xx
#   1  - at least one URL returned 5xx
#   2  - at least one URL was unreachable (timeout / DNS fail)
#   4  - the blueprint file could not be parsed
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../../.." >/dev/null 2>&1 && pwd)"

BLUEPRINT="${REPO_ROOT}/infrastructure/pangolin/a2a-resources.blueprint.yaml"
if [[ "${1:-}" == "--blueprint" && -n "${2:-}" ]]; then
  BLUEPRINT="${2}"
fi

if [[ ! -f "${BLUEPRINT}" ]]; then
  echo "ERROR: blueprint not found at ${BLUEPRINT}" >&2
  exit 4
fi

# Extract `full-domain:` entries from the blueprint. The
# `a2a-resources.blueprint.yaml` has them either at root
# level (private-resources) or nested under `targets[*]`
# (a2a resources). The grep picks up both. Use [[:space:]]
# (POSIX) instead of \s (GNU) for macOS BSD-sed compatibility.
DOMAINS=$(grep -E '^[[:space:]]*(-[[:space:]]+)?full-domain:' "${BLUEPRINT}" \
  | sed -E 's/^[[:space:]]*-?[[:space:]]*full-domain:[[:space:]]*"?([^"]+)"?[[:space:]]*$/\1/' \
  | sort -u)

if [[ -z "${DOMAINS}" ]]; then
  echo "No full-domain entries in ${BLUEPRINT}"
  exit 0
fi

# Filter out obvious non-public entries (e.g. tailscale-only).
DOMAINS=$(echo "${DOMAINS}" | grep -E '\.cianfhoghlaim\.ie$' || true)
if [[ -z "${DOMAINS}" ]]; then
  echo "No public *.cianfhoghlaim.ie entries in ${BLUEPRINT}"
  exit 0
fi

command -v curl >/dev/null 2>&1 || { echo "ERROR: curl not installed" >&2; exit 1; }

# Print header
printf "%-50s  %-6s  %-9s  %s\n" "URL" "STATUS" "TIME(s)" "NOTE"
printf "%-50s  %-6s  %-9s  %s\n" "$(printf '%.0s-' {1..50})" "------" "---------" "----"

EXIT=0
while IFS= read -r domain; do
  url="https://${domain}"
  # -L follow redirects, -I -X GET because some stacks reject HEAD,
  # -o /dev/null to skip the body, -w to print status + time
  # The `|| true` prevents the `||` fallback from duplicating output
  # (a `set -e` shell would otherwise write the curl error AND the fallback).
  out=$(curl -L --max-time 10 -o /dev/null \
      -s -w '%{http_code} %{time_total}' \
      "${url}" 2>/dev/null || true)
  # Normalize: if curl printed nothing (network error), use 000 + 10.000
  if [[ -z "${out}" ]]; then
    status="000"
    ttime="10.000"
  else
    status=$(echo "${out}" | awk '{print $1}')
    ttime=$(echo "${out}"  | awk '{print $2}')
  fi

  note=""
  if [[ "${status}" == "000" ]]; then
    note="unreachable"
    EXIT=$((EXIT | 2))
  elif [[ "${status}" =~ ^5 ]]; then
    note="server error"
    EXIT=$((EXIT | 1))
  fi
  printf "%-50s  %-6s  %-9s  %s\n" "${url}" "${status}" "${ttime}" "${note}"
done <<< "${DOMAINS}"

exit "${EXIT}"
