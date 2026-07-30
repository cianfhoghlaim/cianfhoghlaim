#!/usr/bin/env bash
# Layer 4: run stack-doctor.sh + parse the output
# Per the 2026-08-15-stacks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/stacks-validate-$(date +%Y-%m-%d).md"
{
  echo "# Stacks Validation Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## stack-doctor.sh Audit"
  echo ""
  echo '"```"'
  bash scripts/stack-doctor.sh 2>&1 | head -20 || echo "(stack-doctor.sh missing)"
  echo '"```"'
  echo ""
  total_stacks=$(find bonneagar/stacks -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total stacks: $total_stacks"
} > "$REPORT"
cat "$REPORT"
