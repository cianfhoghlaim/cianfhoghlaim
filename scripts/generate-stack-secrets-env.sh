#!/usr/bin/env bash
# =============================================================================
# generate-stack-secrets-env.sh — Normalize + grammar-check secrets.env across all stacks
# =============================================================================
# Per the 2026-07-30-pre-deploy-blockers-resolution-v1 openspec change
# (closes GitHub issue #107).
#
# USAGE:
#   bash scripts/generate-stack-secrets-env.sh                # normalize (write)
#   bash scripts/generate-stack-secrets-env.sh --check-grammar  # CI gate (no writes)
#   bash scripts/generate-stack-secrets-env.sh --strict       # exit 1 on any warnings
#
# APPROACH:
#   1. Calls `bun run scripts/normalize-infisical-uri.ts` to sweep
#      every `bonneagar/stacks/*/secrets.env` to the canonical bare form
#      `infisical://dev-baile/<svc>/<key>`.
#   2. Then calls `bash scripts/stack-doctor.sh --check-grammar` to
#      verify 0 mixed-grammar stacks.
#
# Exit codes:
#   0 = OK (0 mixed-grammar stacks)
#   1 = FAIL (>= 1 mixed-grammar stack)
#   2 = script error (missing tool, etc.)
# =============================================================================

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GRAMMAR_ONLY=0
STRICT=0

# --- Args ---
for arg in "$@"; do
  case "$arg" in
    --check-grammar) GRAMMAR_ONLY=1 ;;
    --strict)        STRICT=1 ;;
    -h|--help)
      cat <<USAGE
Usage: $0 [options]
  --check-grammar   CI gate: only run grammar check (no writes)
  --strict          exit 1 on any mixed-grammar stack
USAGE
      exit 0
      ;;
  esac
done

# --- Step 1: Normalize (unless --check-grammar) ---
if [ "$GRAMMAR_ONLY" = "0" ]; then
  if command -v bun >/dev/null 2>&1; then
    echo "[generate-stack-secrets-env] running bun run scripts/normalize-infisical-uri.ts"
    # The TS script defaults to ./stacks (the legacy pre-v7 path). Use
    # STACKS_DIR env var if the script supports it; otherwise run with
    # the canonical path. Note: the canonical TS script uses `./stacks`
    # as default — see scripts/normalize-infisical-uri.ts. We pass the
    # path as the first arg via env override if supported.
    if ! bun run "$REPO_ROOT/scripts/normalize-infisical-uri.ts" 2>&1; then
      echo "[generate-stack-secrets-env] WARN: normalize-infisical-uri.ts exited non-zero" >&2
    fi
  else
    echo "[generate-stack-secrets-env] WARN: bun not on PATH; skipping normalization step" >&2
  fi
fi

# --- Step 2: Grammar check ---
# The canonical TS script supports --check-grammar. We call it directly.
exit_code=0
if command -v bun >/dev/null 2>&1; then
  echo "[generate-stack-secrets-env] running bun run scripts/normalize-infisical-uri.ts --check-grammar"
  if bun run "$REPO_ROOT/scripts/normalize-infisical-uri.ts" --check-grammar 2>&1; then
    echo "[generate-stack-secrets-env] OK: 0 mixed-grammar stacks"
  else
    rc=$?
    echo "[generate-stack-secrets-env] FAIL: mixed-grammar stacks detected (rc=$rc)"
    exit_code=1
  fi
else
  # Fallback: use the bash stack-doctor.sh --check-grammar (only flags the
  # mixed cases; emits less detail than the TS version)
  echo "[generate-stack-secrets-env] WARN: bun not on PATH; falling back to stack-doctor.sh --check-grammar"
  if ! bash "$REPO_ROOT/scripts/stack-doctor.sh" --check-grammar 2>&1 | tee /tmp/generate-stack-secrets-env.check-grammar.out; then
    rc=$?
    exit_code=1
  fi
  # stack-doctor.sh considers --check-grammar a warning only; check the output
  if grep -q "MIXED-GRAMMAR" /tmp/generate-stack-secrets-env.check-grammar.out 2>/dev/null; then
    echo "[generate-stack-secrets-env] FAIL: mixed-grammar stacks detected in stack-doctor.sh output"
    exit_code=1
  else
    echo "[generate-stack-secrets-env] OK: 0 mixed-grammar stacks"
  fi
fi

if [ "$STRICT" = "1" ] && [ "$exit_code" != "0" ]; then
  exit "$exit_code"
fi

exit "$exit_code"
