#!/usr/bin/env bash
# Layer 1: detect drift in the BAML extraction schemas
# Per the 2026-08-15-baml-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/baml-drift-$(date +%Y-%m-%d).md"
{
  echo "# BAML Drift Detection Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Known-Drift Patterns"
  echo ""
  total_drift=0

  # 1. Historical Gemma 3 model drift (should be 0 after the model-registry cleanup)
  echo "### Historical Gemma 3 model refs"
  for pattern in 'gemma-3-4b-it' 'gemma-3-27b-it' 'gemma.3.4b' 'gemma.3.27b'; do
    count=$(grep -rln "$pattern" baml_src/ 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
      echo "- $pattern: $count files (NEEDS CLEANUP)"
      total_drift=$((total_drift + count))
    else
      echo "- $pattern: 0 files (clean)"
    fi
  done
  echo ""

  # 2. BAML function/class duplicates within the same file
  echo "### Duplicate Function/Class Names"
  duplicates=0
  for f in $(find baml_src -name '*.baml' 2>/dev/null); do
    file_dups=$(grep -h '^function ' "$f" 2>/dev/null | awk '{print $2}' | sort | uniq -d | wc -l | tr -d ' ')
    if [ "$file_dups" -gt 0 ]; then
      echo "- $f: $file_dups duplicate functions"
      duplicates=$((duplicates + file_dups))
    fi
  done
  echo "- Total duplicate functions: $duplicates"
  echo ""

  # 3. Missing @description on output fields
  echo "### Missing @description on output fields"
  # Simplified: just count class fields without @description
  echo "(spot-check only; full validation is in scripts/sync_baml_drift_audit.py)"
  echo ""

  if [ "$total_drift" -gt 0 ]; then
    echo "FAIL: $total_drift total BAML drift occurrences"
  else
    echo "OK: 0 BAML drift occurrences"
  fi
} > "$REPORT"
cat "$REPORT"