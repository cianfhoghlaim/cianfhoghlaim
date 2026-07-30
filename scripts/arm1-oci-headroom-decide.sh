#!/usr/bin/env bash
# =============================================================================
# arm1-oci-headroom-decide.sh — Read the snapshot + emit a deploy-or-abort verdict
# =============================================================================
# Per the 2026-07-30-pre-deploy-blockers-resolution-v1 openspec change
# (closes GitHub issue #82).
#
# USAGE:
#   bash scripts/arm1-oci-headroom-decide.sh
#   bash scripts/arm1-oci-headroom-decide.sh <snapshot.json>
#   bash scripts/arm1-oci-headroom-decide.sh --strict  # exit 1 on any non-proceed
#
# VERDICT THRESHOLDS (per issue #82):
#   ✅ proceed if all three < 80%        (exit 0)
#   ⚠️  migrate if 80-95%               (exit 1)
#   🚫 abort if > 95%                   (exit 2)
#
# OUTPUT:
#   stdout: verdict line (`✅ proceed: <reason>`, `⚠️ migrate: <reason>`,
#           `🚫 abort: <reason>`)
#   exit:   0 = proceed, 1 = migrate, 2 = abort, 3 = snapshot not found, 4 = invalid
#
# =============================================================================

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$REPO_ROOT/stedding/pre-deploy"
STRICT=0

# --- Args ---
SNAPSHOT=""
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    -h|--help)
      cat <<USAGE
Usage: $0 [<snapshot.json>] [--strict]

Defaults to the latest arm1-oci-headroom-*.json in stedding/pre-deploy/.

Exit codes:
  0 = ✅ proceed (all three < 80%)
  1 = ⚠️  migrate (80-95%)
  2 = 🚫 abort (> 95%)
  3 = snapshot not found
  4 = snapshot invalid / unreadable
USAGE
      exit 0
      ;;
    *)
      if [ -z "$SNAPSHOT" ]; then
        SNAPSHOT="$arg"
      fi
      ;;
  esac
done

# --- Locate the snapshot ---
if [ -z "$SNAPSHOT" ]; then
  SNAPSHOT=$(ls -1t "$REPORT_DIR"/arm1-oci-headroom-*.json 2>/dev/null | head -1 || true)
  if [ -z "$SNAPSHOT" ]; then
    echo "🚫 abort: no snapshot found in $REPORT_DIR (run scripts/arm1-oci-headroom-check.sh first)" >&2
    exit 3
  fi
fi

if [ ! -f "$SNAPSHOT" ]; then
  echo "🚫 abort: snapshot file '$SNAPSHOT' not found" >&2
  exit 3
fi

# --- Parse the snapshot (use python3 if available, else jq, else python -c) ---
PARSED=""
if command -v python3 >/dev/null 2>&1; then
  PARSED=$(python3 -c "
import json, sys
with open('$SNAPSHOT') as f:
    d = json.load(f)
hi = d.get('host_info', {})
print(f\"{hi.get('cpu_pct', 0)} {hi.get('mem_pct', 0)} {hi.get('disk_pct', 0)}\")
" 2>/dev/null || true)
fi
if [ -z "$PARSED" ] && command -v jq >/dev/null 2>&1; then
  PARSED=$(jq -r '"\(.host_info.cpu_pct) \(.host_info.mem_pct) \(.host_info.disk_pct)"' "$SNAPSHOT" 2>/dev/null || true)
fi

if [ -z "$PARSED" ]; then
  echo "🚫 abort: cannot parse snapshot '$SNAPSHOT' (python3 + jq both unavailable or failed)" >&2
  exit 4
fi

read -r CPU_PCT MEM_PCT DISK_PCT <<< "$PARSED"

# --- Decide ---
verdict=""
exit_code=0
for_pct() {
  # Format % with 1 decimal
  awk -v n="$1" 'BEGIN { printf "%.1f", n }' 2>/dev/null || echo "$1"
}

# Helper: max of three
max3() {
  awk -v a="$1" -v b="$2" -v c="$3" 'BEGIN { m = a; if (b > m) m = b; if (c > m) m = c; printf "%.1f", m }'
}

most_loaded=$(echo "$CPU_PCT $MEM_PCT $DISK_PCT" | awk '{ m = $1; if ($2 > m) m = $2; if ($3 > m) m = $3; printf "%.1f", m }')
loaded_metric="cpu"
if echo "$MEM_PCT > $CPU_PCT" | awk '{exit !($1 > $2)}'; then loaded_metric="mem"; fi
if echo "$DISK_PCT > $MEM_PCT" | awk '{exit !($1 > $2)}'; then loaded_metric="disk"; fi

cpu_fmt=$(for_pct "$CPU_PCT")
mem_fmt=$(for_pct "$MEM_PCT")
disk_fmt=$(for_pct "$DISK_PCT")
most_fmt=$(for_pct "$most_loaded")

# Thresholds
if awk -v n="$most_loaded" 'BEGIN { exit !(n < 80) }'; then
  verdict="✅ proceed"
  exit_code=0
  reason="(cpu=${cpu_fmt}% mem=${mem_fmt}% disk=${disk_fmt}% — all < 80%)"
elif awk -v n="$most_loaded" 'BEGIN { exit !(n < 95) }'; then
  verdict="⚠️ migrate"
  exit_code=1
  reason="(cpu=${cpu_fmt}% mem=${mem_fmt}% disk=${disk_fmt}% — $loaded_metric=${most_fmt}% in 80-95% band; migrate to bunchloch)"
else
  verdict="🚫 abort"
  exit_code=2
  reason="(cpu=${cpu_fmt}% mem=${mem_fmt}% disk=${disk_fmt}% — $loaded_metric=${most_fmt}% > 95% hard abort)"
fi

echo "${verdict}: ${reason}"
exit "$exit_code"
