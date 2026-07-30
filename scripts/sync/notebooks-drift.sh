#!/usr/bin/env bash
# Layer 1: notebook registration drift
# Per the 2026-08-15-notebooks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/notebooks-drift-$(date +%Y-%m-%d).md"
{
  echo "# Notebooks Drift Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Unregistered Notebooks (not in cli.py GROUPS)"
  echo ""
  total_drift=0
  if [ -f notebooks/cli.py ]; then
    for f in $(ls notebooks/[0-9]*_*.py 2>/dev/null | head -20); do
      name=$(basename "$f" .py)
      if ! grep -q "\"$name\"\|'$name'\|$name" notebooks/cli.py 2>/dev/null; then
        echo "- $f (not in GROUPS)"
        total_drift=$((total_drift + 1))
      fi
    done
  fi
  echo ""
  echo "## Broken @app.cell Decorators"
  echo ""
  for f in $(ls notebooks/[0-9]*_*.py 2>/dev/null | head -20); do
    if grep -q "@app.cell" "$f" 2>/dev/null; then
      # Check if the @app.cell line is well-formed
      if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "- $f (broken AST)"
        total_drift=$((total_drift + 1))
      fi
    fi
  done
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
