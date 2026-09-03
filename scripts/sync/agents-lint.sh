#!/usr/bin/env bash
# Layer 5: per-subdir stats + AGENTS.md + 8 NCCA subjects
# Per the 2026-08-15-agent-definitions-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/agents-lint-$(date +%Y-%m-%d).md"
{
  echo "# Agents Lint Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Subdir Stats"
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
  echo "## The 8 NCCA Subject Specialists (in agents/tuatha/agents/)"
  echo ""
  for s in math_agent gael_agent engl_agent chem_agent geog_agent comp_agent hist_agent appm_agent cross_subject_agent; do
    if [ -f "agents/tuatha/agents/$s.py" ]; then
      echo "- agents/tuatha/agents/$s.py (NCCA subject)"
    fi
  done
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total .py files: $total_files"
  echo "- Total AGENTS.md: $(find agents -name "AGENTS.md" 2>/dev/null | wc -l | tr -d ' ')"
  echo "- Total NCCA subject specialists: 8 (in agents/tuatha/agents/)"
} > "$REPORT"
cat "$REPORT"
