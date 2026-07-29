#!/usr/bin/env bash
# Orchestrator: runs sync:paths + sync:ccc + sync:cognee + sync:skills + sync:mcp + sync:dagster
# Per the 2026-08-15-knowledge-sync-loop-v1 change (5 layers) +
# the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Layer 6).
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/all-$(date +%Y-%m-%d).md"
{
  echo "# Knowledge Sync Loop — Full Report"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "Per the 2026-08-15-knowledge-sync-loop-v1 change (5 layers) +"
  echo "the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Layer 6)."
  echo "Pull-based. 6 layers total."
  echo ""
  echo "---"
  echo ""
} > "$REPORT"

for layer in paths ccc cognee skills mcp dagster; do
  echo "## Layer: sync:$layer" >> "$REPORT"
  echo '```' >> "$REPORT"
  bash "scripts/sync/$layer.sh" >> "$REPORT" 2>&1
  echo '```' >> "$REPORT"
  echo "" >> "$REPORT"
done

{
  echo "---"
  echo ""
  echo "## Summary"
  echo ""
  echo "All 6 layers completed. The deployment control panel (notebooks/24_deployment_control_panel.py) reads this report."
} >> "$REPORT"

cat "$REPORT"