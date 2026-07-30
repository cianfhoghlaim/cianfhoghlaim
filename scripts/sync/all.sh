#!/usr/bin/env bash
# Orchestrator: runs the 10 sync surfaces in the pull-based knowledge loop
# Per the 2026-08-15-knowledge-sync-loop-v1 change (Layers 1-5) +
# the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Layer 6: dagster) +
# the 2026-08-15-baml-sync-loop-v1 change (Layer 7: baml) +
# the 2026-08-15-stacks-sync-loop-v1 change (Layer 8: stacks) +
# the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change (drift-docs + spec-agents).
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/all-$(date +%Y-%m-%d).md"
{
  echo "# Knowledge Sync Loop — Full Report"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "Per the 2026-08-15-knowledge-sync-loop-v1 change (5 layers) +"
  echo "the 2026-08-15-retroactive-pre-v7-cleanup-v1 change (Layer 6) +"
  echo "the 2026-08-15-baml-sync-loop-v1 change (Layer 7) +"
  echo "the 2026-08-15-stacks-sync-loop-v1 change (Layer 8) +"
  echo "the 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change"
  echo "(drift-docs + spec-agents). Pull-based. 10 sync surfaces total."
  echo ""
  echo "---"
  echo ""
} > "$REPORT"

for layer in paths ccc cognee skills mcp dagster drift_docs spec_agents baml stacks dlt agents; do
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
  echo "All 10 layers completed. The deployment control panel (notebooks/00_control_panel.py) reads this report."
} >> "$REPORT"

cat "$REPORT"