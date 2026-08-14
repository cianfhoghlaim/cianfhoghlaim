#!/usr/bin/env bash
# =============================================================================
# stack-doctor.sh - Audit every bonneagar/stacks/* for GOLD_STANDARD
# =============================================================================
# Bash 3.2 compatible (macOS default).
#
# The stacks/ directory uses a FLAT layout (one directory per stack, no
# category subdirectory). This script iterates every immediate subdirectory
# of bonneagar/stacks/ and validates the 6-file GOLD_STANDARD pattern.
# It also checks that every stack has a corresponding
# cianfhoghlaim/docs/stacks/<name>.md doc (the per-stack
# "purpose + why-GitOps" doc).
#
# USAGE:
#   mise turbo doctor                       # via turbo task
#   ./scripts/stack-doctor.sh               # direct
#   ./scripts/stack-doctor.sh --json        # CI output
#   ./scripts/stack-doctor.sh --strict      # warnings fatal (exit 1)
#   ./scripts/stack-doctor.sh --emit-md <path>  # write INDEX.md
# =============================================================================

set -uo pipefail

STACKS_DIR="${STACKS_DIR:-bonneagar/stacks}"
DOCS_DIR="${DOCS_DIR:-cianfhoghlaim/docs/stacks}"
KOMODO_STACKS_DIR="${KOMODO_STACKS_DIR:-bonneagar/komodo/stacks}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Parse args: support --strict (warnings fatal) + --emit-md <path>
STRICT=0
EMIT_MD=""
JSON_MODE=0
CHECK_GRAMMAR=0
shift_next=0
for arg in "$@"; do
  case "$arg" in
    --strict) STRICT=1 ;;
    --json)   JSON_MODE=1 ;;
    --check-grammar) CHECK_GRAMMAR=1 ;;
    --emit-md)
      shift_next=1
      ;;
    --emit-md=*)
      EMIT_MD="${arg#--emit-md=}"
      ;;
    *)
      if [ "$shift_next" = "1" ]; then
        EMIT_MD="$arg"
        shift_next=0
      fi
      ;;
  esac
done

if [ ! -d "$REPO_ROOT/$STACKS_DIR" ]; then
  echo "ERROR: $REPO_ROOT/$STACKS_DIR not found" >&2
  exit 1
fi

CRITICALS_FILE="$(mktemp)"
WARNINGS_FILE="$(mktemp)"
INFOS_FILE="$(mktemp)"
DOCS_MISSING_FILE="$(mktemp)"
trap 'rm -f "$CRITICALS_FILE" "$WARNINGS_FILE" "$INFOS_FILE" "$DOCS_MISSING_FILE"' EXIT

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
    refs=$(grep -cE "(infisical://dev-baile/|\{\{ infisical://)" "$stack_path/secrets.env" 2>/dev/null)
    refs=${refs:-0}
    if [ "$refs" = "0" ]; then
      echo "$name: secrets.env has no infisical:// refs" >> "$WARNINGS_FILE"
      return
    fi
  fi

  if [ "$has_compose" -eq 1 ] && [ "$has_env" -eq 1 ]; then
    if command -v docker >/dev/null 2>&1; then
      # --no-env-resolution: runtime env_file paths like
      # /run/secrets/locket/secrets.env are written by the Locket sidecar
      # at runtime and don't exist on the host at config-validation time.
      # We only validate compose-file syntax, not runtime secret injection.
      if ! docker compose -f "$stack_path/compose.yaml" --env-file "$stack_path/.env.example" config --quiet --no-env-resolution 2>/dev/null; then
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

# ----------------------------------------------------------------------------
# Grammar check (--check-grammar): flag any secrets.env that mixes bare + Jinja
# ----------------------------------------------------------------------------
GRAMMAR_FILE="$(mktemp)"
trap 'rm -f "$CRITICALS_FILE" "$WARNINGS_FILE" "$INFOS_FILE" "$DOCS_MISSING_FILE" "$GRAMMAR_FILE"' EXIT

if [ "$CHECK_GRAMMAR" = "1" ]; then
  for stack in "$REPO_ROOT/$STACKS_DIR"/*/; do
    [ -d "$stack" ] || continue
    [ -f "$stack/secrets.env" ] || continue
    stack_name=$(basename "$stack")
    # Count bare-form lines (infisical://dev-baile/<svc>/<key>) — outside of
    # comments or Jinja braces. Pattern requires the bare infisical:// prefix.
    bare_count=$(grep -cE '^[[:space:]]*[^#[:space:]][^=]*=infisical://dev-baile/' "$stack/secrets.env" 2>/dev/null | tr -d ' ')
    bare_count=${bare_count:-0}
    # Count Jinja-wrapped lines: KEY={{ infisical:///... }}
    jinja_count=$(grep -cE '^[[:space:]]*[^#[:space:]][^=]*=\{\{[[:space:]]*infisical:' "$stack/secrets.env" 2>/dev/null | tr -d ' ')
    jinja_count=${jinja_count:-0}
    # Mixed if both > 0
    if [ "$bare_count" -gt 0 ] && [ "$jinja_count" -gt 0 ]; then
      echo "$stack_name: MIXED-GRAMMAR (bare=$bare_count jinja=$jinja_count)" >> "$GRAMMAR_FILE"
    fi
  done
  grammar_count=$(wc -l < "$GRAMMAR_FILE" | tr -d ' ')
  if [ "$grammar_count" -gt 0 ]; then
    cat "$GRAMMAR_FILE" >> "$WARNINGS_FILE"
    echo ""
    echo "## GRAMMAR (CI gate --check-grammar)"
    echo ""
    cat "$GRAMMAR_FILE"
    echo ""
  fi
fi

# ----------------------------------------------------------------------------
# Per-stack doc check
# ----------------------------------------------------------------------------
for stack in "$REPO_ROOT/$STACKS_DIR"/*/; do
  [ -d "$stack" ] || continue
  stack_name=$(basename "$stack")
  if [ ! -f "$REPO_ROOT/$DOCS_DIR/$stack_name.md" ]; then
    echo "$stack_name: missing-doc" >> "$DOCS_MISSING_FILE"
  fi
done

cat "$DOCS_MISSING_FILE" >> "$CRITICALS_FILE"

critical_count=$(wc -l < "$CRITICALS_FILE" | tr -d ' ')
warning_count=$(wc -l < "$WARNINGS_FILE"  | tr -d ' ')
info_count=$(wc -l < "$INFOS_FILE"      | tr -d ' ')

# ----------------------------------------------------------------------------
# Emit markdown INDEX.md (--emit-md <path>)
# ----------------------------------------------------------------------------
if [ -n "$EMIT_MD" ]; then
  {
    echo "# Bonneagar Infrastructure Stacks — INDEX (single source of truth)"
    echo ""
    echo "> Generated by \`bun run stack-doctor --emit-md\` on $(date -u +%Y-%m-%dT%H:%M:%SZ)."
    echo "> This file replaces \`HEALTH_REPORT.md\` (archived 2026-07-09). The directory"
    echo "> count is canonical — the 88 stacks at \`bonneagar/stacks/\`."
    echo ""
    echo "## Summary"
    echo ""
    echo "| Severity | Count |"
    echo "|----------|-------|"
    echo "| CRITICAL | $critical_count |"
    echo "| WARNING  | $warning_count |"
    echo "| INFO     | $info_count |"
    echo ""
    echo "## Stack Inventory"
    echo ""
    echo "| Stack | compose | sidecar | secrets | pangolin | blueprint | env.example | komodo.toml |"
    echo "|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|"
    for stack in "$REPO_ROOT/$STACKS_DIR"/*/; do
      [ -d "$stack" ] || continue
      stack_name=$(basename "$stack")
      compose="❌"; [ -f "$stack/compose.yaml" ] && compose="✓"
      sidecar="❌"; [ -f "$stack/sidecar.yaml" ] && sidecar="✓"
      secrets="❌"; [ -f "$stack/secrets.env" ] && secrets="✓"
      pangolin="❌"; [ -f "$stack/pangolin.yaml" ] && pangolin="✓"
      blueprint="❌"; [ -f "$stack/blueprint.yaml" ] && blueprint="✓"
      env_example="❌"; [ -f "$stack/.env.example" ] && env_example="✓"
      komodo_toml="❌"
      if [ -d "$REPO_ROOT/$KOMODO_STACKS_DIR" ]; then
        for kt in "$REPO_ROOT/$KOMODO_STACKS_DIR"/"${stack_name}"*.toml; do
          if [ -f "$kt" ]; then
            komodo_toml="✓"
            break
          fi
        done
      fi
      echo "| ${stack_name} | $compose | $sidecar | $secrets | $pangolin | $blueprint | $env_example | $komodo_toml |"
    done
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
  } > "$EMIT_MD"
fi

# ----------------------------------------------------------------------------
# JSON output (--json)
# ----------------------------------------------------------------------------
if [ "$JSON_MODE" = "1" ]; then
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
  [ "$STRICT" = "1" ] && [ "$warning_count" -gt 0 ] && [ "$exit_code" -eq 0 ] && exit_code=2
  exit $exit_code
fi

# ----------------------------------------------------------------------------
# Default human-readable output
# ----------------------------------------------------------------------------
if [ -z "$EMIT_MD" ]; then
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
fi

exit_code=0
[ "$critical_count" -gt 0 ] && exit_code=1
[ "$warning_count" -gt 0 ] && [ "$exit_code" -eq 0 ] && exit_code=2
[ "$STRICT" = "1" ] && [ "$warning_count" -gt 0 ] && [ "$exit_code" -eq 0 ] && exit_code=2
exit $exit_code