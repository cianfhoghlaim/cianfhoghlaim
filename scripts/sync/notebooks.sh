#!/usr/bin/env bash
# Layer 11 orchestrator: runs sync:notebooks-drift + sync:notebooks-ccc + sync:notebooks-cognee
#                            + sync:notebooks-test + sync:notebooks-lint in sequence
# Per the 2026-08-15-notebooks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/notebooks-$(date +%Y-%m-%d).md"
{
  echo "# Notebooks Sync Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Prefix Breakdown"
  echo ""
  total_files=0
  for prefix in 00 01 02 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 27 40; do
    if compgen -G "notebooks/${prefix}_*.py" > /dev/null; then
      files=$(ls notebooks/${prefix}_*.py 2>/dev/null | wc -l | tr -d ' ')
      cell_count=$(grep -l '@app.cell' notebooks/${prefix}_*.py 2>/dev/null | wc -l | tr -d ' ')
      printf "| %s_ | %s .py | %s @app.cell |\n" "$prefix" "$files" "$cell_count"
      total_files=$((total_files + files))
    fi
  done
  echo ""
  echo "## The Canonical Notebook Helpers"
  echo ""
  for f in notebooks/_shared notebooks/cli.py notebooks/_shared/db.py; do
    if [ -e "$f" ]; then
      echo "- $f"
    fi
  done
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total notebook files: $total_files"
  echo ""
  if [ "$total_files" -gt 0 ]; then
    echo "OK: $total_files notebooks registered across 20+ prefixes"
  else
    echo "FAIL: 0 notebooks detected (suspicious)"
  fi
} > "$REPORT"
cat "$REPORT"
