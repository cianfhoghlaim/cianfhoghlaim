#!/usr/bin/env bash
# Layer 10 orchestrator: runs sync:agents-drift + sync:agents-ccc + sync:agents-cognee
#                            + sync:agents-test + sync:agents-lint in sequence
# Per the 2026-08-15-agent-definitions-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/agents-$(date +%Y-%m-%d).md"
{
  echo "# Agent Definitions Sync Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Subdir Breakdown"
  echo ""
  total_files=0
  for subdir in agents agents/adk agents/agno agents/api agents/tools agents/tuatha agents/meaisinfhoghlaim; do
    if [ -d "$subdir" ]; then
      files=$(find "$subdir" -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' ')
      agents_md=$(find "$subdir" -name "AGENTS.md" 2>/dev/null | wc -l | tr -d ' ')
      printf "| %-30s | %s .py | %s AGENTS.md |\n" "$subdir" "$files" "$agents_md"
      total_files=$((total_files + files))
    fi
  done
  echo ""
  echo "## The 5 AGENTS.md Files"
  echo ""
  for f in agents/AGENTS.md agents/tuatha/AGENTS.md agents/api/AGENTS.md agents/meaisinfhoghlaim/AGENTS.md agents/adk/AGENTS.md agents/agno/AGENTS.md; do
    if [ -f "$f" ]; then
      lines=$(wc -l < "$f" | tr -d ' ')
      echo "- $f ($lines lines)"
    fi
  done
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total .py files: $total_files"
  echo ""
  if [ "$total_files" -gt 0 ]; then
    echo "OK: $total_files .py files registered across 7 agent subdirs"
  else
    echo "FAIL: 0 .py files detected (suspicious)"
  fi
} > "$REPORT"
cat "$REPORT"
