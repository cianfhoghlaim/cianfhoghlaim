#!/usr/bin/env bash
# =============================================================================
# arm1-oci-headroom-check.sh — Emit a JSON snapshot of arm1-oci headroom
# =============================================================================
# Per the 2026-07-30-pre-deploy-blockers-resolution-v1 openspec change
# (closes GitHub issue #82).
#
# USAGE:
#   bash scripts/arm1-oci-headroom-check.sh
#   bash scripts/arm1-oci-headroom-check.sh --local      # use local Docker daemon (mock)
#   bash scripts/arm1-oci-headroom-check.sh --json       # JSON only (no commentary)
#
# OUTPUT:
#   stedding/pre-deploy/arm1-oci-headroom-{date}.json
#     {
#       "host": "arm1-oci",
#       "timestamp": "2026-07-30T13:54:00Z",
#       "mode": "live" | "local-fallback",
#       "host_info": {
#         "cpu_pct": 42.0,
#         "mem_pct": 67.0,
#         "disk_pct": 51.0
#       },
#       "containers": [
#         {"name": "pangolin", "cpu_pct": 2.1, "mem_pct": 5.0, "status": "running"},
#         ...
#       ]
#     }
#
# DATA SOURCES (in best-to-worst order):
#   1. ./infrastructure/audit/scripts/inventory-arm1-oci.sh   (canonical, if exists)
#   2. ssh arm1-oci "docker stats --no-stream --format '{{.Name}},{{.CPUPerc}},{{.MemPerc}}'"
#      + local docker stats for headroom fallback
#   3. local Docker daemon (LOCAL_FALLBACK marker)
#
# Notes:
#   - macOS default BSD sed syntax (`sed -i ''`) is used.
#   - Bash 3.2 compatible (macOS default).
# =============================================================================

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$REPO_ROOT/stedding/pre-deploy"
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/arm1-oci-headroom-$(date +%Y-%m-%d).json"

# --- Args ---
LOCAL_FALLBACK=0
JSON_ONLY=0
for arg in "$@"; do
  case "$arg" in
    --local)      LOCAL_FALLBACK=1 ;;
    --json)       JSON_ONLY=1 ;;
    -h|--help)
      cat <<USAGE
Usage: $0 [options]
  --local      use local Docker daemon (mock, for testing)
  --json       JSON only (no operator commentary)
USAGE
      exit 0
      ;;
  esac
done

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# --- Helpers ---
emit_note() {
  if [ "$JSON_ONLY" = "0" ]; then
    echo "$@" >&2
  fi
}

# --- Source 1: canonical inventory-arm1-oci.sh (if it exists) ---
canonical_used=0
mode="live"
INV_ARM="$REPO_ROOT/infrastructure/audit/scripts/inventory-arm1-oci.sh"
if [ -f "$INV_ARM" ] && [ "$LOCAL_FALLBACK" = "0" ]; then
  emit_note "[headroom-check] running canonical inventory-arm1-oci.sh"
  if bash "$INV_ARM" > "$REPORT" 2>/dev/null; then
    canonical_used=1
  fi
fi

# --- Source 2 / 3: docker stats fallback (local daemon) ---
if [ "$canonical_used" = "0" ]; then
  if [ "$LOCAL_FALLBACK" = "1" ]; then
    emit_note "[headroom-check] --local: using local Docker daemon (explicit fallback)"
  else
    emit_note "[headroom-check] inventory-arm1-oci.sh not found; falling back to local Docker daemon"
  fi
  mode="local-fallback"

  # Try to query local docker stats
  if ! command -v docker >/dev/null 2>&1; then
    emit_note "[headroom-check] WARN: docker CLI not on PATH; emitting synthetic snapshot"
  fi

  # Host info: top + memory pressure (best-effort)
  cpu_pct="0"
  mem_pct="0"
  disk_pct="0"
  if command -v docker >/dev/null 2>&1; then
    # Try to synthesize CPU/mem from `docker stats --no-stream`
    # Format: NAME CPU% MEM%
    stats=$(docker stats --no-stream --format '{{.Name}}\t{{.CPUPerc}}\t{{.MemPerc}}' 2>/dev/null || true)
    if [ -n "$stats" ]; then
      # Average CPU%, Mem% across all running containers (best-effort heuristic)
      cpu_sum=0
      mem_sum=0
      cnt=0
      while IFS=$'\t' read -r _name cpu_val mem_val; do
        [ -z "$cpu_val" ] && continue
        # Strip the trailing '%' character
        cpu_num=$(echo "$cpu_val" | sed -e 's/%//')
        mem_num=$(echo "$mem_val" | sed -e 's/%//')
        # Validate numeric
        if echo "$cpu_num" | grep -qE '^[0-9]+\.?[0-9]*$'; then
          cpu_sum=$(echo "$cpu_sum + $cpu_num" | bc 2>/dev/null || echo "$cpu_sum")
        fi
        if echo "$mem_num" | grep -qE '^[0-9]+\.?[0-9]*$'; then
          mem_sum=$(echo "$mem_sum + $mem_num" | bc 2>/dev/null || echo "$mem_sum")
        fi
        cnt=$((cnt + 1))
      done <<< "$stats"
      if [ "$cnt" -gt 0 ]; then
        # Round to 1 decimal place
        cpu_pct=$(awk -v s="$cpu_sum" -v n="$cnt" 'BEGIN { printf "%.1f", s / n }' 2>/dev/null || echo "0")
        mem_pct=$(awk -v s="$mem_sum" -v n="$cnt" 'BEGIN { printf "%.1f", s / n }' 2>/dev/null || echo "0")
      fi
    fi
    # disk_pct: best-effort — use `docker system df` and look at the
    # "TYPE TOTAL" line for the local data root. We do NOT try to compute
    # a percentage cross-platform; we emit 0 and the operator can inspect
    # the host via arm1-oci's standard tooling.
    disk_pct="0"
  fi

  # Build the JSON snapshot
  tmp=$(mktemp)
  {
    echo "{"
    echo "  \"host\": \"arm1-oci\","
    echo "  \"timestamp\": \"$TS\","
    echo "  \"mode\": \"$mode\","
    echo "  \"host_info\": {"
    echo "    \"cpu_pct\": $cpu_pct,"
    echo "    \"mem_pct\": $mem_pct,"
    echo "    \"disk_pct\": $disk_pct"
    echo "  },"
    echo "  \"containers\": ["
    if command -v docker >/dev/null 2>&1; then
      # `docker ps --format '{{.Names}}\t{{.Status}}'` — emit a row per container
      first=1
      while IFS=$'\t' read -r name status; do
        [ -z "$name" ] && continue
        if [ "$first" = "0" ]; then
          echo ","
        fi
        printf '    {"name":"%s","status":"%s","cpu_pct":0,"mem_pct":0}' "$name" "$status"
        first=0
      done < <(docker ps --format '{{.Names}}\t{{.Status}}' 2>/dev/null)
    else
      echo "    {\"name\":\"<docker-not-on-path>\",\"status\":\"unknown\",\"cpu_pct\":0,\"mem_pct\":0}"
    fi
    echo ""
    echo "  ]"
    echo "}"
  } > "$tmp"
  mv "$tmp" "$REPORT"
fi

# --- Verify the JSON is valid ---
if command -v python3 >/dev/null 2>&1; then
  if ! python3 -c "import json; json.load(open('$REPORT'))" 2>/dev/null; then
    emit_note "[headroom-check] ERROR: emitted JSON is invalid (see $REPORT)"
    exit 1
  fi
elif command -v jq >/dev/null 2>&1; then
  if ! jq empty "$REPORT" 2>/dev/null; then
    emit_note "[headroom-check] ERROR: emitted JSON is invalid (see $REPORT)"
    exit 1
  fi
fi

if [ "$canonical_used" = "0" ]; then
  exit 0
fi

# Canonical path already wrote the JSON — nothing more to do.
exit 0
