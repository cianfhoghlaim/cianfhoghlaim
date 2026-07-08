#!/usr/bin/env bash
# =============================================================================
# bonneagar stack-doctor — the 7-gate v5 CI check
# =============================================================================
# Gates:
#   1. GOLD_STANDARD 6-file compliance (compose, sidecar, secrets,
#      pangolin, blueprint, .env.example)
#   2. No `[[stack]]` blocks in komodo/procedures/*.toml
#   3. No ghost hosts (oci-databases, oci-devtools, macbook-media,
#      macbook-analytics, cax41)
#   4. No `op://` 1Password URIs
#   5. Locket image canonical (ghcr.io/bpbradley/locket:infisical only)
#   6. Pangolin blueprint per-stack (no root-level pangolin/*.yaml
#      blueprints pointing at multiple stacks)
#   7. Two-host topology (no cax41-hetzner outside pulumi/)
# =============================================================================
# Returns exit code 0 on success, non-zero on any gate failure.
# =============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$REPO_ROOT"

GATE_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# ANSI color codes (no-op if not a TTY)
if [ -t 1 ]; then
  RED=$'\033[0;31m'
  GREEN=$'\033[0;32m'
  YELLOW=$'\033[0;33m'
  BLUE=$'\033[0;34m'
  BOLD=$'\033[1m'
  RESET=$'\033[0m'
else
  RED="" GREEN="" YELLOW="" BLUE="" BOLD="" RESET=""
fi

run_gate() {
  local name="$1"
  local cmd="$2"
  GATE_COUNT=$((GATE_COUNT + 1))
  echo "${BOLD}${BLUE}─── Gate $GATE_COUNT: $name ───${RESET}"
  local exit_code=0
  eval "$cmd" || exit_code=$?
  if [ "$exit_code" = "0" ]; then
    echo "${GREEN}✓ pass${RESET}"
  else
    echo "${RED}✗ fail${RESET}"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
  echo
}

warn_gate() {
  local name="$1"
  local msg="$2"
  GATE_COUNT=$((GATE_COUNT + 1))
  WARN_COUNT=$((WARN_COUNT + 1))
  echo "${BOLD}${YELLOW}─── Gate $GATE_COUNT: $name (warning) ───${RESET}"
  echo "${YELLOW}⚠ $msg${RESET}"
  echo
}

# ─── Gate 1: 1 required GOLD_STANDARD file ───
# Per the v5 spec delta, the only strictly required file is:
#   compose.yaml (every stack MUST have this)
# The 5 OPTIONAL files (per v5 user decision to keep all 88 stacks
# including the 5 personal/utility stacks that don't need secrets):
#   sidecar.yaml (only stacks with Infisical secrets need this)
#   secrets.env (only production stacks with Infisical refs need this)
#   blueprint.yaml (only actively-deployed stacks need this)
#   pangolin.yaml (only stacks with a public Pangolin route need this)
#   .env.example (only actively-deployed stacks need this)
run_gate "GOLD_STANDARD minimum: compose.yaml required" '
  bad=0
  # Find all directories under stacks/ that contain a compose.yaml or
  # compose.dev.yaml. Directories without compose files are flagged, but
  # nested stacks (e.g. stacks/croilar/croilar-marimo) are OK if their
  # leaves have compose files.
  while IFS= read -r d; do
    if [ -z "$(ls "$d"/compose.yaml "$d"/compose.dev.yaml 2>/dev/null)" ]; then
      if [ -z "$(find "$d" -mindepth 2 -maxdepth 2 \( -name compose.yaml -o -name compose.dev.yaml \) 2>/dev/null)" ]; then
        echo "  ✗ no compose.yaml in $d"
        bad=$((bad + 1))
      fi
    fi
  done < <(find bonneagar/stacks -mindepth 1 -maxdepth 1 -type d)
  return $bad
'

warn_gate "GOLD_STANDARD optional files" "Some stacks are missing sidecar.yaml / secrets.env / blueprint.yaml / pangolin.yaml / .env.example; these are optional and tracked for hygiene"

# ─── Gate 2: No `[[stack]]` blocks in komodo/procedures/*.toml ───
run_gate "No [[stack]] blocks in procedures/" '
  matches=$(grep -lE "^\[\[stack\]\]" bonneagar/komodo/procedures/*.toml 2>/dev/null || true)
  if [ -n "$matches" ]; then
    echo "$matches"
    echo "  → [[stack]] blocks belong in stacks/, not procedures/"
    return 1
  else
    return 0
  fi
'

# ─── Gate 3: No ghost hosts ───
run_gate "No ghost hosts (oci-databases, oci-devtools, macbook-*, cax41)" '
  matches=$(grep -rE "\"host:(oci-databases|oci-devtools|macbook-media|macbook-analytics|cax41)\"" bonneagar/komodo/ 2>/dev/null || true)
  if [ -n "$matches" ]; then
    echo "$matches"
    echo "  → only arm1-oci + bunchloch are valid hosts"
    return 1
  else
    return 0
  fi
'

# ─── Gate 4: No `op://` 1Password URIs ───
# op:// is forbidden in stacks/, pangolin/, iac/, and komodo/.
# It is allowed in dagger/ts_submodules/bonneagar/src/ (the
# preserved TypeScript reference implementation; not
# executed in production).
run_gate "No op:// 1Password URIs in stacks/ + iac/ + komodo/" '
  bad=0
  for d in bonneagar/stacks/ bonneagar/pangolin/ bonneagar/iac/ bonneagar/komodo/; do
    if grep -rnE "op://" "$d" 2>/dev/null; then
      echo "  → op:// found in $d (forbidden; use infisical://dev-baile/<svc>/<key>)"
      bad=$((bad + 1))
    fi
  done
  return $bad
'

# ─── Gate 5: Locket image canonical ───
run_gate "Locket image canonical (ghcr.io/bpbradley/locket:infisical only)" '
  # Allow only the canonical image; reject fictional cianfhoghlaim/locket
  # and any tag other than :infisical
  bad=0
  while IFS= read -r match; do
    if [[ "$match" != *"ghcr.io/bpbradley/locket:infisical"* ]]; then
      echo "  ✗ non-canonical locket image: $match"
      bad=$((bad + 1))
    fi
  done < <(grep -rE "ghcr\.io/[^ ]*locket:[a-zA-Z0-9._-]+" bonneagar/stacks/ 2>/dev/null)
  return $bad
'

# ─── Gate 6: No root-level pangolin/ blueprints pointing at multiple stacks ───
# (the pangolin/a2a-resources.blueprint.yaml + olm-resources.blueprint.yaml
# + private-resources.blueprint.yaml were moved to per-stack locations in v5)
run_gate "No root pangolin/ blueprints" '
  bad=0
  for f in a2a-resources.blueprint.yaml olm-resources.blueprint.yaml private-resources-fixed.blueprint.yaml; do
    if [ -f "bonneagar/pangolin/$f" ]; then
      echo "  ✗ deprecated root blueprint: bonneagar/pangolin/$f"
      bad=$((bad + 1))
    fi
  done
  return $bad
'

# ─── Gate 7: Two-host topology (no cax41-hetzner in runtime config) ───
# Hetzner (cax41-hetzner) is allowed in:
#   - bonneagar/pulumi/ (the canonical Hetzner provisioning)
#   - stack READMEs (documentation; the stack is/was deployed there)
#   - drift annotations (comments mentioning "v5: cax41-hetzner-removed")
# It is FORBIDDEN in active config (non-comment lines) in:
#   - iac/ (the IaC is 2-host only: arm1-oci + bunchloch)
#   - scripts/ (legacy bash scripts should be migrated)
#   - komodo/ (the Komodo fleet is 2-host only)
run_gate "No cax41-hetzner in runtime config (iac/, scripts/, komodo/)" '
  bad=0
  matches_file=$(mktemp)
  for d in bonneagar/iac/ bonneagar/scripts/ bonneagar/komodo/; do
    # Use a temp file to avoid the "|| true" exit code
    # hiding the actual count. Skip comment lines (starting with
    # # for bash/Python or // for TypeScript) — these are drift
    # annotations, not active config.
    grep -rn "cax41-hetzner" "$d" 2>/dev/null \
      | grep -vE "^[^:]+:[0-9]+:[[:space:]]*(#|//|/\*)" \
      >> "$matches_file" || true
  done
  if [ -s "$matches_file" ]; then
    cat "$matches_file"
    echo "  → cax41-hetzner found (forbidden; pulumi/ only)"
    bad=$((bad + 1))
  fi
  rm -f "$matches_file"
  return $bad
'

# ─── Gate 8 (warning): Stack count matches AGENTS.md ───
# Count stacks as the number of subdirs of bonneagar/stacks/ that
# have a compose.yaml (or compose.dev.yaml) directly.
stack_count=$(find bonneagar/stacks -mindepth 2 -maxdepth 2 -name "compose.yaml" 2>/dev/null | wc -l | tr -d ' ')
if [ "$stack_count" = "88" ]; then
  echo "${GREEN}✓ Stack count is 88 (matches AGENTS.md)${RESET}"
else
  warn_gate "Stack count" "expected 88, found $stack_count"
fi

# ─── Summary ───
echo "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
if [ "$FAIL_COUNT" = "0" ]; then
  echo "${GREEN}${BOLD}✓ stack-doctor: $GATE_COUNT gates, 0 failures${RESET}"
  echo "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
  exit 0
else
  echo "${RED}${BOLD}✗ stack-doctor: $GATE_COUNT gates, $FAIL_COUNT failures, $WARN_COUNT warnings${RESET}"
  echo "${BOLD}══════════════════════════════════════════════════════════════${RESET}"
  exit 1
fi
