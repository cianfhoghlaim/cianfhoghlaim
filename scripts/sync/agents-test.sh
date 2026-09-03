#!/usr/bin/env bash
# Layer 4: agent registration test
# Per the 2026-08-15-agent-definitions-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/agents-test-$(date +%Y-%m-%d).md"
{
  echo "# Agents Test Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Subdir Agent Count"
  echo ""
  for subdir in agents agents/adk agents/agno agents/api agents/tools agents/tuatha agents/meaisinfhoghlaim; do
    if [ -d "$subdir" ]; then
      agent_classes=$(grep -rln "^class.*Agent" "$subdir" 2>/dev/null | wc -l | tr -d ' ')
      printf "| %-30s | %s Agent classes |\n" "$subdir" "$agent_classes"
    fi
  done
  echo ""
  echo "## Summary"
  echo ""
  total=0
  for f in $(find agents -name "*.py" 2>/dev/null); do
    if grep -q "^class.*Agent" "$f" 2>/dev/null; then
      total=$((total + 1))
    fi
  done
  echo "- Total Agent classes detected: $total"
  echo ""
  echo "Note: full 'agents:smoke' test requires mise to run; use 'uv run python -c \"from agents.agent_registry import verify_agents; verify_agents()\"' for manual testing"
} > "$REPORT"
cat "$REPORT"
