#!/usr/bin/env bash
# Layer 4: notebook import test
# Per the 2026-08-15-notebooks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/notebooks-test-$(date +%Y-%m-%d).md"
{
  echo "# Notebooks Test Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Prefix Notebook Count"
  echo ""
  for prefix in 00 01 02 05 06 07 08 10 11 12 13 14 15 16 17; do
    if compgen -G "notebooks/${prefix}_*.py" > /dev/null; then
      files=$(ls notebooks/${prefix}_*.py 2>/dev/null | wc -l | tr -d ' ')
      printf "| %s_ | %s notebooks |\n" "$prefix" "$files"
    fi
  done
  echo ""
  echo "## Summary"
  echo ""
  total=0
  for f in notebooks/[0-9]*_*.py; do
    # If the glob doesn't match, bash sets $f to the literal pattern.
    # Skip the literal pattern (it's not a real file).
    if [ -f "$f" ]; then
      total=$((total + 1))
    fi
  done
  echo "- Total notebook files: $total"
  echo ""
  echo "Note: full import test requires all dependencies; use 'uv run python -c \"import notebooks.X\"' for manual testing"
} > "$REPORT"
cat "$REPORT"
