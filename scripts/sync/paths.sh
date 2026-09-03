#!/usr/bin/env bash
# Layer 1: detect pre-v7 path drift in source files
# Per the 2026-08-15-knowledge-sync-loop-v1 change (the foundation)
# + the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (the --fix mode)
#
# Usage:
#   bash scripts/sync/paths.sh              # detect only (exit 1 if drift found)
#   bash scripts/sync/paths.sh --fix       # detect + auto-fix the 3 safe patterns
#
# The 3 safe auto-fix patterns (per sync_paths_fix.py):
#   sruth/cianfhoghlaim/        -> . (the pre-v7 repo rename)
#   infrastructure/stacks/      -> bonneagar/stacks/  (the IaC move)
#   infrastructure/komodo/      -> bonneagar/komodo/  (the IaC move)
#
# The 2 manual patterns (require human review):
#   cianfhoghlaim/dlt/          -> documented in the per-directory diagnostic report
#   cianfhoghlaim/baml/         -> documented in the per-directory diagnostic report

set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/paths-$(date +%Y-%m-%d).md"
{
  echo "# Pre-v7 Path Drift Sync Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  total_drift=0
  for pattern in 'cianfhoghlaim/dlt/' 'cianfhoghlaim/baml/' 'infrastructure/stacks/' 'infrastructure/komodo/' 'sruth/cianfhoghlaim/' 'infrastructure/iac/dagster/'; do
    count=$(grep -rE "$pattern" \
      --include='*.py' --include='*.ts' --include='*.toml' \
      --include='*.yaml' --include='*.baml' --include='*.tsx' \
      --include='*.json' \
      bonneagar/ dlt_sources/ orchestration/ baml_src/ cocoindex/ \
      motherduck/ meaisinfhoghlaim/ agents/ observability/ \
      pyproject.toml mise.toml turbo.json package.json tsconfig.json \
      2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
      echo "- $pattern: $count occurrences (NEEDS CLEANUP)"
      total_drift=$((total_drift + count))
    else
      echo "- $pattern: 0 occurrences (clean)"
    fi
  done
  echo ""
  if [ "$total_drift" -gt 0 ]; then
    echo "FAIL: $total_drift total pre-v7 path drift occurrences"
  else
    echo "OK: 0 pre-v7 path drift in active source"
  fi
} > "$REPORT"
cat "$REPORT"
auto_fixable_drift=$(python3 -c 'from scripts.sync_paths_fix import SAFE_PATTERNS, find_files_with_pattern, is_safe_to_rename; print(sum(p.read_text().count(old) for old, new, _ in SAFE_PATTERNS for p in find_files_with_pattern(old) if is_safe_to_rename(p, old, new)[0]))')
if [ "$auto_fixable_drift" -eq 0 ]; then
    echo "OK: 0 auto-fixable pre-v7 path drift occurrences"
else
    echo "FAIL: $auto_fixable_drift auto-fixable pre-v7 path drift occurrences"
fi

# Handle --fix mode
if [ "${1:-}" = "--fix" ]; then
    echo ""
    echo "=== Running auto-fix mode (per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change) ==="
    python3 scripts/sync_paths_fix.py
    fix_exit=$?
    echo ""
    echo "=== Re-running sync:paths to verify the count dropped ==="
    bash "$0" 2>&1 | tail -15 || true
    exit "$fix_exit"
fi

[ "$auto_fixable_drift" -eq 0 ]