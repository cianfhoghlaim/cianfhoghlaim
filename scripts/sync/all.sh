#!/usr/bin/env bash
# Orchestrator: runs sync:paths + sync:ccc + sync:cognee + sync:skills + sync:mcp
# Per the 2026-08-15-knowledge-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/all-$(date +%Y-%m-%d).md"
{
  echo "# Knowledge Sync Loop — Full Report"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "Per the 2026-08-15-knowledge-sync-loop-v1 change. Pull-based."
  echo ""
  echo "---"
  echo ""
} > "$REPORT"

for layer in paths ccc cognee skills mcp; do
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
  echo "All 5 layers completed. The deployment control panel (notebooks/24_deployment_control_panel.py) reads this report."
} >> "$REPORT"

cat "$REPORT"
