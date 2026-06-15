#!/usr/bin/env bash
# infrastructure/audit/scripts/inventory-bunchloch.sh
# ---------------------------------------------------------------------------
# Snapshot the live state of the local Docker host (bunchloch, the
# MacBook M4 primary-workloads host) to a JSON file under
# `infrastructure/audit/inventory/bunchloch-<UTC>.json`.
#
# This is documentation/audit content. It does NOT modify any
# container, network, or volume. It is safe to run any time.
#
# Usage:
#   bash infrastructure/audit/scripts/inventory-bunchloch.sh
#   bash infrastructure/audit/scripts/inventory-bunchloch.sh --output /tmp/snap.json
#
# Exit codes:
#   0  - snapshot written
#   1  - docker not installed
#   2  - docker daemon not reachable
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/../../.." >/dev/null 2>&1 && pwd)"
INV_DIR="${REPO_ROOT}/infrastructure/audit/inventory"
mkdir -p "${INV_DIR}"

OUTPUT="${INV_DIR}/bunchloch-$(date -u +%Y%m%dT%H%M%SZ).json"
if [[ "${1:-}" == "--output" && -n "${2:-}" ]]; then
  OUTPUT="${2}"
fi

# Pre-flight
command -v docker >/dev/null 2>&1 || { echo "ERROR: docker not installed" >&2; exit 1; }
docker info >/dev/null 2>&1 || { echo "ERROR: docker daemon not reachable" >&2; exit 2; }

# Host info
HOST_INFO=$(cat <<EOF
{
  "hostname": "$(hostname)",
  "uname":   "$(uname -srm)",
  "docker":  "$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo unknown)",
  "captured_utc": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
)

# Containers
CONTAINERS=$(docker ps -a --no-trunc --format '{{json .}}' \
  | jq -s 'map({
      name: .Names,
      image: .Image,
      state: .State,
      status: .Status,
      ports: (.Ports // "" | split(",")),
      mounts: (.Mounts // "" | split(",")),
      labels: (.Labels // ""),
      networks: ""
    })' 2>/dev/null || echo "[]")

# Networks
NETWORKS=$(docker network ls --no-trunc --format '{{json .}}' \
  | jq -s 'map({name: .Name, driver: .Driver, scope: .Scope})' 2>/dev/null || echo "[]")

# Volumes
VOLUMES=$(docker volume ls --format '{{json .}}' \
  | jq -s 'map({name: .Name, driver: .Driver})' 2>/dev/null || echo "[]")

# Compose-file coverage (best-effort)
COMPOSE_COVERAGE=$(find "${REPO_ROOT}/infrastructure/stacks" -name "compose.yaml" \
  -type f 2>/dev/null | wc -l | tr -d ' ')

# Assemble final JSON
{
  printf '{\n'
  printf '  "host": %s,\n' "${HOST_INFO}"
  printf '  "containers": %s,\n' "${CONTAINERS}"
  printf '  "networks": %s,\n'    "${NETWORKS}"
  printf '  "volumes": %s,\n'     "${VOLUMES}"
  printf '  "compose_files_in_repo": %s\n' "${COMPOSE_COVERAGE}"
  printf '}\n'
} | jq . > "${OUTPUT}"

echo "Wrote ${OUTPUT}"
echo "  containers: $(echo "${CONTAINERS}" | jq 'length')"
echo "  networks:   $(echo "${NETWORKS}" | jq 'length')"
echo "  volumes:    $(echo "${VOLUMES}" | jq 'length')"
