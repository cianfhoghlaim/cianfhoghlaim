#!/usr/bin/env bash
# Layer 5: per-prefix stats
# Per the 2026-08-15-notebooks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/notebooks-lint-$(date +%Y-%m-%d).md"
{
  echo "# Notebooks Lint Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Prefix Stats"
  echo ""
  total_files=0
  total_cells=0
  for prefix in 00 01 02 05 06 07 08 10 11 12 13 14 15 16 17 18 19 20 21 22 23 27 40; do
    if compgen -G "notebooks/${prefix}_*.py" > /dev/null; then
      files=$(ls notebooks/${prefix}_*.py 2>/dev/null | wc -l | tr -d ' ')
      cell_count=$(grep -l '@app.cell' notebooks/${prefix}_*.py 2>/dev/null | wc -l | tr -d ' ')
      printf "| %s_ | %s .py | %s @app.cell |\n" "$prefix" "$files" "$cell_count"
      total_files=$((total_files + files))
      total_cells=$((total_cells + cell_count))
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
  echo "- Total @app.cell decorators: $total_cells"
} > "$REPORT"
cat "$REPORT"
