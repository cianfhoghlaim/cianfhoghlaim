#!/usr/bin/env bash
# =============================================================================
# stack-doctor.sh - Audit every infrastructure/stacks/* for GOLD_STANDARD
# =============================================================================
# Bash 3.2 compatible (macOS default).
#
# The stacks/ directory uses a FLAT layout (one directory per stack, no
# category subdirectory). This script iterates every immediate subdirectory
# of infrastructure/stacks/ and validates the 6-file GOLD_STANDARD pattern.
#
# USAGE:
#   mise turbo doctor             # via turbo task
#   ./scripts/stack-doctor.sh     # direct
#   ./scripts/stack-doctor.sh --json  # CI output
# =============================================================================

set -uo pipefail

STACKS_DIR="${STACKS_DIR:-infrastructure/stacks}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ ! -d "$REPO_ROOT/$STACKS_DIR" ]; then
  echo "ERROR: $REPO_ROOT/$STACKS_DIR not found" >&2
  exit 1
fi

CRITICALS_FILE="$(mktemp)"
WARNINGS_FILE="$(mktemp)"
INFOS_FILE="$(mktemp)"
trap 'rm -f "$CRITICALS_FILE" "$WARNINGS_FILE" "$INFOS_FILE"' EXIT

audit_stack() {
  local stack_path="$1"
  local name
  name=$(basename "$stack_path")
  local issues=""

  local has_compose=0 has_sidecar=0 has_pangolin=0 has_blueprint=0 has_secrets=0 has_env=0
  [ -f "$stack_path/compose.yaml" ]   && has_compose=1
  [ -f "$stack_path/sidecar.yaml" ]   && has_sidecar=1
  [ -f "$stack_path/pangolin.yaml" ]  && has_pangolin=1
  [ -f "$stack_path/blueprint.yaml" ] && has_blueprint=1
  [ -f "$stack_path/secrets.env" ]    && has_secrets=1
  [ -f "$stack_path/.env.example" ]   && has_env=1

  if [ "$has_compose" -eq 0 ] && [ "$has_blueprint" -eq 0 ]; then
    echo "$name: no-compose-or-blueprint" >> "$CRITICALS_FILE"
    return
  fi

  if [ "$has_compose" -eq 1 ] && [ "$has_blueprint" -eq 0 ]; then
    issues+="no-blueprint.yaml "
  fi

  if [ "$has_compose" -eq 1 ] && [ "$has_sidecar" -eq 0 ]; then
    issues+="no-sidecar "
    echo "$name: $issues" >> "$WARNINGS_FILE"
    return
  fi

  if [ "$has_secrets" -eq 1 ]; then
    local refs
    refs=$(grep -c "{{ infisical://" "$stack_path/secrets.env" 2>/dev/null)
    refs=${refs:-0}
    if [ "$refs" = "0" ]; then
      echo "$name: secrets.env has no infisical:// refs" >> "$WARNINGS_FILE"
      return
    fi
  fi

  if [ "$has_compose" -eq 1 ] && [ "$has_env" -eq 1 ]; then
    if command -v docker >/dev/null 2>&1; then
      if ! docker compose -f "$stack_path/compose.yaml" --env-file "$stack_path/.env.example" config --quiet 2>/dev/null; then
        echo "$name: docker compose config --quiet failed" >> "$CRITICALS_FILE"
        return
      fi
    fi
  fi

  if [ "$has_compose" -eq 1 ]; then
    local latest_count
    latest_count=$(grep -c "image: .*:latest$" "$stack_path/compose.yaml" 2>/dev/null)
    latest_count=${latest_count:-0}
    if [ "$latest_count" -gt 0 ]; then
      issues+="${latest_count}-latest-tags "
    fi
  fi

  if [ "$has_compose" -eq 1 ]; then
    local svc_count hc_count
    svc_count=$(grep -c "^  [a-z][a-z0-9_-]*:$" "$stack_path/compose.yaml" 2>/dev/null)
    svc_count=${svc_count:-0}
    hc_count=$(grep -c "healthcheck:" "$stack_path/compose.yaml" 2>/dev/null)
    hc_count=${hc_count:-0}
    if [ "$svc_count" -gt 1 ] && [ "$hc_count" = "0" ]; then
      issues+="no-healthchecks "
    fi
  fi

  if [ -n "$issues" ]; then
    echo "$name: $issues" >> "$INFOS_FILE"
  fi
}

for stack in "$REPO_ROOT/$STACKS_DIR"/*/; do
  [ -d "$stack" ] || continue
  audit_stack "$stack"
done

critical_count=$(wc -l < "$CRITICALS_FILE" | tr -d ' ')
warning_count=$(wc -l < "$WARNINGS_FILE"  | tr -d ' ')
info_count=$(wc -l < "$INFOS_FILE"      | tr -d ' ')

if [ "${1:-}" = "--json" ]; then
  printf '{"critical":%s,"warning":%s,"info":%s,"criticals":[' "$critical_count" "$warning_count" "$info_count"
  first=1
  while IFS= read -r c; do
    [ -z "$c" ] && continue
    [ $first -eq 0 ] && printf ','
    printf '"%s"' "$c"
    first=0
  done < "$CRITICALS_FILE"
  printf '],"warnings":['
  first=1
  while IFS= read -r w; do
    [ -z "$w" ] && continue
    [ $first -eq 0 ] && printf ','
    printf '"%s"' "$w"
    first=0
  done < "$WARNINGS_FILE"
  printf '],"infos":['
  first=1
  while IFS= read -r i; do
    [ -z "$i" ] && continue
    [ $first -eq 0 ] && printf ','
    printf '"%s"' "$i"
    first=0
  done < "$INFOS_FILE"
  printf ']}\n'
  exit_code=0
  [ "$critical_count" -gt 0 ] && exit_code=1
  [ "$warning_count" -gt 0 ] && [ "$exit_code" -eq 0 ] && exit_code=2
  exit $exit_code
fi

echo "# Stack Doctor Report"
echo ""
echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "| Severity | Count |"
echo "|----------|-------|"
echo "| CRITICAL | $critical_count |"
echo "| WARNING  | $warning_count |"
echo "| INFO     | $info_count |"
echo ""

if [ "$critical_count" -gt 0 ]; then
  echo "## CRITICALS"
  echo ""
  cat "$CRITICALS_FILE"
  echo ""
fi

if [ "$warning_count" -gt 0 ]; then
  echo "## WARNINGS"
  echo ""
  cat "$WARNINGS_FILE"
  echo ""
fi

if [ "$info_count" -gt 0 ]; then
  echo "## INFOS (worth fixing but not blocking)"
  echo ""
  cat "$INFOS_FILE"
  echo ""
fi

echo "## Next steps"
echo ""
echo "1. Fix CRITICALS first — these stacks can't deploy."
echo "2. Then WARNINGS — these stacks deploy but won't survive production."
echo "3. Then INFOS — hardening and best-practices polish."
echo ""
echo "Run with --json for CI integration."

exit_code=0
[ "$critical_count" -gt 0 ] && exit_code=1
[ "$warning_count" -gt 0 ] && [ "$exit_code" -eq 0 ] && exit_code=2
exit $exit_code
