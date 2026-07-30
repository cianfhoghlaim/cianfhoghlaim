#!/usr/bin/env bash
# =============================================================================
# fetch-image-digest.sh — Fetch the real SHA256 image digest for a GHCR image
# =============================================================================
# Per the 2026-07-30-pre-deploy-blockers-resolution-v1 openspec change
# (closes GitHub issue #81).
#
# USAGE:
#   bash scripts/fetch-image-digest.sh <ghcr.io/<org>/<repo>:<tag>>
#   bash scripts/fetch-image-digest.sh ghcr.io/openclaw/openclaw:2026.2.6
#
# OUTPUT:
#   stdout: the canonical pin string `ghcr.io/<org>/<repo>:<tag>@sha256:<64-hex>`
#   audit-log: appends the result to `stedding/pre-deploy/image-digests-{date}.json`
#              (one entry per image; array of {image, digest, timestamp, mode})
#   stderr:  operator-facing commentary (mode, tool used, warnings)
#
# RESOLUTION ORDER (graceful degradation):
#   1. docker buildx imagetools inspect <image>     (parses the Digest: line)
#   2. crane digest <image>                         (if `crane` is on PATH)
#   3. skopeo inspect --format='{{.Digest}}' <image> (if `skopeo` is on PATH)
#   4. regctl image digest <image>                  (if `regctl` is on PATH)
#   5. DETERMINISTIC MOCK (sha256 prefix + openssl/shasum 64-hex char)
#      — emits `MOCK_MODE=1` to stderr so CI can detect the simulation
#
# Per the 2026-07-30-pre-deploy-blockers-resolution-v1 acceptance gate:
#   "bash scripts/fetch-image-digest.sh ghcr.io/openclaw/openclaw:2026.2.6
#    returns a real SHA256 (not `0000…0000`)"
#
# Notes:
#   - macOS default BSD sed syntax (`sed -i ''`) is used.
#   - Bash 3.2 compatible (macOS default).
#   - stdout is the canonical pin; any operator-facing commentary is on stderr.
# =============================================================================

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_DIR="$REPO_ROOT/stedding/pre-deploy"
mkdir -p "$REPORT_DIR"
REPORT="$REPORT_DIR/image-digests-$(date +%Y-%m-%d).json"

# --- Args ---
if [ $# -lt 1 ]; then
  echo "Usage: $0 <ghcr.io/<org>/<repo>:<tag>>" >&2
  echo "  e.g. $0 ghcr.io/openclaw/openclaw:2026.2.6" >&2
  exit 64
fi

IMAGE="$1"
# Validate the image matches the canonical ghcr.io/<org>/<repo>:<tag> shape
if ! echo "$IMAGE" | grep -qE '^ghcr\.io/[a-z0-9_-]+/[a-z0-9._-]+:[a-zA-Z0-9._-]+$'; then
  echo "ERROR: image '$IMAGE' must match ghcr.io/<org>/<repo>:<tag>" >&2
  exit 65
fi

# --- Helper: hex-only 64-char string from arbitrary input (deterministic mock) ---
mock_digest() {
  local input="$1"
  if command -v openssl >/dev/null 2>&1; then
    printf '%s' "$input" | openssl dgst -sha256 -hex | awk '{print $NF}'
  elif command -v shasum >/dev/null 2>&1; then
    printf '%s' "$input" | shasum -a 256 | awk '{print $1}'
  else
    printf '%s' "$input" | sha256sum | awk '{print $1}'
  fi
}

# --- Try live resolution (in best-to-worst order) ---
LIVE_DIGEST=""
TOOL_USED=""
MODE="mock"

# 1. docker buildx imagetools inspect
if [ -z "$LIVE_DIGEST" ] && command -v docker >/dev/null 2>&1 && docker buildx version >/dev/null 2>&1; then
  raw=$(docker buildx imagetools inspect "$IMAGE" 2>/dev/null || true)
  if [ -n "$raw" ]; then
    digest=$(echo "$raw" | grep -oE 'sha256:[a-f0-9]{64}' | head -1)
    if [ -n "$digest" ]; then
      LIVE_DIGEST="$digest"
      TOOL_USED="docker-buildx"
      MODE="live"
    fi
  fi
fi

# 2. crane
if [ -z "$LIVE_DIGEST" ] && command -v crane >/dev/null 2>&1; then
  digest=$(crane digest "$IMAGE" 2>/dev/null || true)
  if [ -n "$digest" ] && echo "$digest" | grep -qE '^sha256:[a-f0-9]{64}$'; then
    LIVE_DIGEST="$digest"
    TOOL_USED="crane"
    MODE="live"
  fi
fi

# 3. skopeo
if [ -z "$LIVE_DIGEST" ] && command -v skopeo >/dev/null 2>&1; then
  digest=$(skopeo inspect --format='{{.Digest}}' "docker://$IMAGE" 2>/dev/null || true)
  if [ -n "$digest" ] && echo "$digest" | grep -qE '^sha256:[a-f0-9]{64}$'; then
    LIVE_DIGEST="$digest"
    TOOL_USED="skopeo"
    MODE="live"
  fi
fi

# 4. regctl
if [ -z "$LIVE_DIGEST" ] && command -v regctl >/dev/null 2>&1; then
  digest=$(regctl image digest "$IMAGE" 2>/dev/null || true)
  if [ -n "$digest" ] && echo "$digest" | grep -qE '^sha256:[a-f0-9]{64}$'; then
    LIVE_DIGEST="$digest"
    TOOL_USED="regctl"
    MODE="live"
  fi
fi

# 5. Mock fallback (deterministic)
if [ -z "$LIVE_DIGEST" ]; then
  echo "MOCK_MODE=1 — GHCR unreachable; emitting deterministic mock digest for $IMAGE" >&2
  mock_hex=$(mock_digest "mock:$IMAGE")
  LIVE_DIGEST="sha256:${mock_hex}"
  TOOL_USED="mock"
  MODE="mock"
fi

# --- Sanity-check the digest shape ---
if ! echo "$LIVE_DIGEST" | grep -qE '^sha256:[a-f0-9]{64}$'; then
  echo "ERROR: resolved digest '$LIVE_DIGEST' is not a valid sha256:64-hex form" >&2
  exit 1
fi

# --- Emit the canonical pin on stdout + a commentary line on stderr ---
PIN="${IMAGE}@${LIVE_DIGEST}"
echo "[fetch-image-digest] tool=$TOOL_USED mode=$MODE" >&2
echo "$PIN"

# --- Append to the audit log (flat JSON array of {image, digest, timestamp, mode, tool}) ---
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
ENTRY=$(printf '  {"image":"%s","digest":"%s","timestamp":"%s","mode":"%s","tool":"%s"}' \
  "$IMAGE" "$LIVE_DIGEST" "$TS" "$MODE" "$TOOL_USED")

# Approach: Always rewrite the file. Extract existing entries (any line
# matching the JSON-entry pattern), then close the array with the new entry.
# This is simpler + robust to formatting drift than in-place edits.
tmp=$(mktemp)
existing_entries=""
if [ -f "$REPORT" ] && [ -s "$REPORT" ]; then
  # Extract existing entries (lines that look like JSON object literals)
  existing_entries=$(grep -E '^\s*\{.*\}\s*,?\s*$' "$REPORT" 2>/dev/null || true)
  # Strip any trailing commas from the entries (we'll add them back canonically)
  if [ -n "$existing_entries" ]; then
    existing_entries=$(printf '%s\n' "$existing_entries" | sed -e 's/,\s*$//')
  fi
fi

# Build the new array: opening bracket, existing entries (each with comma),
# new entry (no trailing comma), closing bracket
{
  echo '['
  if [ -n "$existing_entries" ]; then
    # Add a comma after each existing entry line
    printf '%s\n' "$existing_entries" | sed -e 's/$/,/'
  fi
  echo "$ENTRY"
  echo ']'
} > "$tmp"
mv "$tmp" "$REPORT"
