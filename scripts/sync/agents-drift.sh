#!/usr/bin/env bash
# Layer 1: agent registration drift
# Per the 2026-08-15-agent-definitions-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/agents-drift-$(date +%Y-%m-%d).md"
{
  echo "# Agent Drift Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Unregistered Agents (not in agent_registry.py)"
  echo ""
  total_drift=0
  for f in $(find agents -name "*.py" 2>/dev/null | head -20); do
    if grep -q "class.*Agent" "$f" 2>/dev/null; then
      if ! grep -q "$(basename "$f" .py)" agents/agent_registry.py 2>/dev/null; then
        echo "- $f (unregistered agent class detected)"
        total_drift=$((total_drift + 1))
      fi
    fi
  done
  echo ""
  echo "## Stale Model References (e.g. gemma-3-4b-it after model-registry cleanup)"
  echo ""
  stale_count=$(grep -rln "gemma-3-4b-it\|gemma-3-27b-it" agents/ 2>/dev/null | wc -l | tr -d ' ')
  echo "- Stale model refs: $stale_count"
  total_drift=$((total_drift + stale_count))
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total drift occurrences: $total_drift"
  if [ "$total_drift" -gt 0 ]; then
    echo "FAIL: $total_drift total drift occurrences"
  else
    echo "OK: 0 drift occurrences"
  fi
} > "$REPORT"
cat "$REPORT"
