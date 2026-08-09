#!/usr/bin/env bash
# =============================================================================
# deploy-full.sh — One-command full-stack deploy orchestrator (shell entry)
# =============================================================================
# Per the 2026-08-01-lakehouse-and-reproducible-deploy-v1 openspec change:
#
#   "The system MUST provide a `mise run deploy:full` command that brings
#    up the entire 91-stack platform in 8 phases with healthchecks + a
#    resumable checkpoint state file at `~/.cianfhoghlaim/deploy-state.json`."
#
# This shell script is the user-facing entry point. The TypeScript
# orchestrator (`scripts/deploy-full.ts`) is the state machine that owns
# the resumable checkpoint file. The shell entry delegates to the TS
# orchestrator after validating the preflight.
#
# USAGE:
#   mise run deploy:full                  # full deploy from phase 1
#   mise run deploy:full --skip-preflight # skip the preflight-arm-oci gate
#   mise run deploy:full --dry-run        # dry-run (no mutations)
#   bash scripts/deploy-full.sh --phase=4  # run only phase 4
#
# The 10 phases (per the 2026-08-15-bonneagar-infra-remediation-v2 openspec
# change — extends the v1 8-phase orchestrator):
#   1. preflight-arm-oci        — 4-check safety gate
#   2. iac-auth-rotate          — iac:rotate-auth (3-way credential rotation)
#   3. pocketid-oidc-wire       — iac:wire-pocketid-as-oidc (Pocket ID → Komodo + Pangolin)
#   4. pangolin-client-install  — iac:bootstrap-pangolin-client (mint Pangolin client + render newt compose)
#   5. control-plane-up         — infisical + pangolin + komodo + pocket-id + tinyauth
#   6. lakehouse-up             — postgres + garage + clickhouse + redis + lakekeeper + lance-namespace
#   7. data-stacks-up           — litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb
#   8. ocr-backends-up          — paddleocr + dots-ocr + olmocr + docling-serve + mlx-omni + llama-swap + meaisinfoghlaim (NEW 2026-08-02)
#   9. agent-surfaces-up        — openclaw + openchamber + hermes + ocr-router
#  10. dagster-materialize-and-sensor-health-gate — BIEP v3 materialise + sensor health gate (combined)
# =============================================================================

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TS_ORCHESTRATOR="${REPO_ROOT}/scripts/deploy-full.ts"
STATE_FILE="${HOME}/.cianfhoghlaim/deploy-state.json"
LOG_FILE="${HOME}/.cianfhoghlaim/deploy-$(date -u +%Y%m%dT%H%M%SZ).log"
PHASE_NAMES=(preflight-arm-oci iac-auth-rotate pocketid-oidc-wire pangolin-client-install control-plane-up lakehouse-up data-stacks-up ocr-backends-up agent-surfaces-up dagster-materialize-and-sensor-health-gate)

# --- Parse args ---
SKIP_PREFLIGHT=false
DRY_RUN=false
ONLY_PHASE=""
for arg in "$@"; do
  case "$arg" in
    --skip-preflight) SKIP_PREFLIGHT=true ;;
    --dry-run) DRY_RUN=true ;;
    --phase=*)
      ONLY_PHASE="${arg#--phase=}"
      if ! [[ "$ONLY_PHASE" =~ ^(10|[1-9])$ ]]; then
        echo "ERROR: --phase must be 1-10; got '$ONLY_PHASE'" >&2
        exit 2
      fi
      ;;
    -h|--help)
      cat <<USAGE
Usage: $0 [options]

Options:
  --skip-preflight       Skip the preflight-arm-oci safety gate (not recommended)
  --dry-run              Dry-run mode (no mutations; logs what would happen)
  --phase=N              Run only phase N (1-10); other phases SKIPPED

Examples:
  $0                            # full deploy from phase 1
  $0 --skip-preflight           # skip the safety gate (NOT recommended)
  $0 --dry-run                  # see what would happen
  $0 --phase=4                  # run only phase 4 (pangolin-client-install)
USAGE
      exit 0
      ;;
    *) echo "unknown arg: $arg; use --help" >&2; exit 2 ;;
  esac
done

# --- Helpers ---
log()  { printf '\033[1;34m[%s]\033[0m %s\n' "$(date -u +%H:%M:%S)" "$*"; }
ok()   { printf '\033[1;32m  ✓\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m  !\033[0m %s\n' "$*"; }
err()  { printf '\033[1;31m  ✗\033[0m %s\n' "$*" >&2; }

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"
exec > >(tee -a "$LOG_FILE") 2>&1

log "deploy-full.sh starting"
log "  REPO_ROOT=$REPO_ROOT"
log "  TS_ORCHESTRATOR=$TS_ORCHESTRATOR"
log "  STATE_FILE=$STATE_FILE"
log "  LOG_FILE=$LOG_FILE"
log "  SKIP_PREFLIGHT=$SKIP_PREFLIGHT"
log "  DRY_RUN=$DRY_RUN"
log "  ONLY_PHASE=$ONLY_PHASE"

# --- Preflight gate ---
if [ "$SKIP_PREFLIGHT" != true ]; then
  log "Phase 0: preflight-arm-oci (4-check safety gate)"
  if ! bash "${REPO_ROOT}/scripts/preflight-arm-oci.sh" --dry-run 2>&1 | tail -20; then
    err "preflight-arm-oci FAILED"
    err "Re-run with --skip-preflight ONLY if you understand why it failed."
    exit 1
  fi
  ok "preflight-arm-oci passed"
fi

# --- Delegate to the TS orchestrator ---
log "Delegating to TS orchestrator: $TS_ORCHESTRATOR"
if [ ! -f "$TS_ORCHESTRATOR" ]; then
  err "TS orchestrator not found at $TS_ORCHESTRATOR"
  exit 1
fi

ARGS=()
[ "$SKIP_PREFLIGHT" = true ] && ARGS+=("--skip-preflight")
[ "$DRY_RUN" = true ] && ARGS+=("--dry-run")
[ -n "$ONLY_PHASE" ] && ARGS+=("--phase=$ONLY_PHASE")

bun run "$TS_ORCHESTRATOR" "${ARGS[@]}"
RC=$?

log "deploy-full.sh exiting with code $RC"
exit $RC