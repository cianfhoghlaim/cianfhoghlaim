#!/usr/bin/env bash
# infrastructure/audit/scripts/inventory-arm1-oci.sh
# ---------------------------------------------------------------------------
# Snapshot the live state of the arm1-oci host (Oracle Cloud ARM,
# control plane) to a JSON file under
# `infrastructure/audit/inventory/arm1-oci-<UTC>.json`.
#
# Runs the same inventory commands as inventory-bunchloch.sh but
# over `ssh arm1-oci '...'`. Requires:
#   - ssh in $PATH
#   - `arm1-oci` host entry in ~/.ssh/config
#   - passwordless key auth (public key installed on arm1-oci)
#
# This is documentation/audit content. It does NOT modify any
# container, network, or volume. It is safe to run any time.
#
# Usage:
#   bash infrastructure/audit/scripts/inventory-arm1-oci.sh
#   bash infrastructure/audit/scripts/inventory-arm1-oci.sh --output /tmp/snap.json
#
# Exit codes:
#   0  - snapshot written
#   1  - ssh / docker not installed
#   2  - cannot reach arm1-oci
#   3  - arm1-oci has no docker daemon
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../../.." >/dev/null 2>&1 && pwd)"
INV_DIR="${REPO_ROOT}/infrastructure/audit/inventory"
mkdir -p "${INV_DIR}"

OUTPUT="${INV_DIR}/arm1-oci-$(date -u +%Y%m%dT%H%M%SZ).json"
if [[ "${1:-}" == "--output" && -n "${2:-}" ]]; then
  OUTPUT="${2}"
fi

# Pre-flight
command -v ssh >/dev/null 2>&1   || { echo "ERROR: ssh not installed"     >&2; exit 1; }
command -v jq  >/dev/null 2>&1   || { echo "ERROR: jq not installed"      >&2; exit 1; }
ssh -o ConnectTimeout=5 -o BatchMode=yes arm1-oci 'true' \
  || { echo "ERROR: cannot reach arm1-oci" >&2; exit 2; }

# Remote commands — identical shape to inventory-bunchloch.sh so
# the diff-against-composes script can consume either output.
REMOTE_BLOCK='
set -e
docker info >/dev/null 2>&1 || { echo "REMOTE_DOCKER_DOWN" 1>&2; exit 3; }

HOST_INFO=$(cat <<EOF2
{
  "hostname": "$(hostname)",
  "uname":   "$(uname -srm)",
  "docker":  "$(docker version --format '"'"'{{.Server.Version}}'"'"' 2>/dev/null || echo unknown)",
  "captured_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF2
)

CONTAINERS=$(docker ps -a --no-trunc --format '"'"'{{json .}}'"'"' \
  | jq -s '"'"'map({
      name: .Names,
      image: .Image,
      state: .State,
      status: .Status,
      ports: (.Ports // "" | split(",")),
      mounts: (.Mounts // "" | split(",")),
      labels: (.Labels // ""),
      networks: (.Names | tostring)
    })'"'"' 2>/dev/null || echo "[]")

NETWORKS=$(docker network ls --no-trunc --format '"'"'{{json .}}'"'"' \
  | jq -s '"'"'map({name: .Name, driver: .Driver, scope: .Scope})'"'"' 2>/dev/null || echo "[]")

VOLUMES=$(docker volume ls --format '"'"'{{json .}}'"'"' \
  | jq -s '"'"'map({name: .Name, driver: .Driver})'"'"' 2>/dev/null || echo "[]")

printf "{\n"
printf "  \"host\": %s,\n" "$HOST_INFO"
printf "  \"containers\": %s,\n" "$CONTAINERS"
printf "  \"networks\": %s,\n"   "$NETWORKS"
printf "  \"volumes\": %s\n"     "$VOLUMES"
printf "}\n"
'

OUT=$(ssh -o BatchMode=yes arm1-oci "$REMOTE_BLOCK")
echo "$OUT" | jq . > "${OUTPUT}"

CONTAINER_COUNT=$(echo "$OUT" | jq '.containers | length')
NETWORK_COUNT=$(echo "$OUT"  | jq '.networks | length')
VOLUME_COUNT=$(echo "$OUT"   | jq '.volumes | length')

echo "Wrote ${OUTPUT}"
echo "  containers: ${CONTAINER_COUNT}"
echo "  networks:   ${NETWORK_COUNT}"
echo "  volumes:    ${VOLUME_COUNT}"
