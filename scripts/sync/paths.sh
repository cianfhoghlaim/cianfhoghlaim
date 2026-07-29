#!/usr/bin/env bash
# Layer 1: detect pre-v7 path drift in source files
# Per the 2026-08-15-knowledge-sync-loop-v1 change.
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
[ "$total_drift" -eq 0 ]
