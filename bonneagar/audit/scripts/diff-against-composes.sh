#!/usr/bin/env bash
# infrastructure/audit/scripts/diff-against-composes.sh
# ---------------------------------------------------------------------------
# Diff two inventory JSON snapshots (bunchloch + arm1-oci) against
# the filesystem `infrastructure/stacks/**/compose.yaml` files.
# Surfaces:
#   * orphaned containers: live but not declared in any compose
#   * missing services:    declared in a compose but not running
#   * port conflicts:       two services on the same host port
#
# Usage:
#   bash infrastructure/audit/scripts/diff-against-composes.sh \
#       infrastructure/audit/inventory/bunchloch-20260615T120000Z.json \
#       infrastructure/audit/inventory/arm1-oci-20260615T120000Z.json
#
# Or, with no args, the script picks the most recent bunchloch +
# arm1-oci JSON under infrastructure/audit/inventory/.
#
# Exit codes:
#   0  - no orphans, no missing services, no port conflicts
#   1  - at least one orphan
#   2  - at least one missing service
#   3  - at least one port conflict
#   4  - combinations of the above (bitwise OR)
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../../.." >/dev/null 2>&1 && pwd)"
INV_DIR="${REPO_ROOT}/infrastructure/audit/inventory"

if [[ -n "${1:-}" && -n "${2:-}" ]]; then
  BUNCHLOCH_JSON="$1"
  ARM_JSON="$2"
else
  BUNCHLOCH_JSON=$(ls -1t "${INV_DIR}"/bunchloch-*.json 2>/dev/null | head -1 || true)
  ARM_JSON=$(ls -1t "${INV_DIR}"/arm1-oci-*.json 2>/dev/null | head -1 || true)
fi

if [[ -z "${BUNCHLOCH_JSON}" || ! -f "${BUNCHLOCH_JSON}" ]]; then
  echo "ERROR: no bunchloch snapshot found. Run inventory-bunchloch.sh first." >&2
  exit 1
fi
if [[ -z "${ARM_JSON}" || ! -f "${ARM_JSON}" ]]; then
  echo "ERROR: no arm1-oci snapshot found. Run inventory-arm1-oci.sh first." >&2
  exit 1
fi

echo "Using snapshots:"
echo "  bunchloch: ${BUNCHLOCH_JSON}"
echo "  arm1-oci:  ${ARM_JSON}"
echo

# Extract container names from the live snapshots
LIVE_NAMES=$(jq -r '(.containers // []) | .[].name' "${BUNCHLOCH_JSON}" "${ARM_JSON}" \
  | sort -u)

# Extract declared service container_names from the filesystem
DECLARED_NAMES=$(grep -rhE '^\s*container_name:' \
    "${REPO_ROOT}/infrastructure/stacks" "${REPO_ROOT}/infrastructure/infisical" \
    --include="compose.yaml" --include="docker-compose.yaml" 2>/dev/null \
  | sed -E 's/^\s*container_name:\s*"?([^"]+)"?\s*$/\1/' \
  | sort -u)

# 1. Orphans: live but not in any compose
echo "== Orphaned containers (live, not in any compose) =="
ORPHANS=$(comm -23 <(echo "${LIVE_NAMES}") <(echo "${DECLARED_NAMES}"))
if [[ -z "${ORPHANS}" ]]; then
  echo "  (none)"
else
  echo "${ORPHANS}" | sed 's/^/  /'
fi
echo

# 2. Missing services: declared in a compose but not running
echo "== Missing services (in a compose, not running) =="
MISSING=$(comm -13 <(echo "${LIVE_NAMES}") <(echo "${DECLARED_NAMES}"))
if [[ -z "${MISSING}" ]]; then
  echo "  (none)"
else
  echo "${MISSING}" | sed 's/^/  /'
fi
echo

# 3. Port conflicts: same host port, two services
echo "== Host-port conflicts =="
# Each line: "container_name  host_port"  e.g. "komodo-core  9120:9120"
# Extract "0.0.0.0:NNNN->.../tcp" patterns and pair with the
# container's ports field.  Simpler: grep ports lines.
CONFLICTS=$(jq -r '
  (.containers // [])[]
  | .name as $n
  | (.ports // [])[]
  | select(test(":[0-9]+->"))
  | capture(":(?<p>[0-9]+)->").p
  | "\(input_line_number)\t\($n)\t\(.)"
' "${BUNCHLOCH_JSON}" "${ARM_JSON}" 2>/dev/null || true)

# The jq path is fiddly.  Use a flatter shell pipeline instead.
PORT_TABLE=$(jq -r '
  (.containers // [])[]
  | . as $c
  | (.ports // [])
  | map(select(test(":[0-9]+->")))
  | map(capture(":(?<p>[0-9]+)->").p)
  | .[]
  | "\(. )\t\($c.name)"
' "${BUNCHLOCH_JSON}" "${ARM_JSON}" 2>/dev/null \
  | sort -k1,1n | uniq)

DUPES=$(echo "${PORT_TABLE}" | awk -F'\t' '{print $1}' | sort | uniq -d)
if [[ -z "${DUPES}" ]]; then
  echo "  (none)"
else
  for port in ${DUPES}; do
    echo "  port ${port}:"
    echo "${PORT_TABLE}" | awk -F'\t' -v p="${port}" '$1 == p {print "    " $2}' | sed 's/^/    /'
  done
fi
echo

# Exit-code math
EXIT=0
if [[ -n "${ORPHANS}"   ]]; then EXIT=$((EXIT | 1)); fi
if [[ -n "${MISSING}"   ]]; then EXIT=$((EXIT | 2)); fi
if [[ -n "${DUPES}"     ]]; then EXIT=$((EXIT | 3)); fi
exit "${EXIT}"
