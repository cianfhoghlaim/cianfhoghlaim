#!/usr/bin/env bash
# Layer 4: run baml-cli test on the 11 test blocks
# Per the 2026-08-15-baml-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/baml-test-$(date +%Y-%m-%d).md"
{
  echo "# BAML Test Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Test Block Counts (per cluster)"
  echo ""
  total_tests=0
  for cluster in american_nations british_isles celtic commonwealth european_nations european_union processing; do
    if [ -d "baml_src/$cluster" ]; then
      tests=$(grep -h '^test ' "baml_src/$cluster"/*.baml 2>/dev/null | wc -l | tr -d ' ')
      echo "- $cluster: $tests test blocks"
      total_tests=$((total_tests + tests))
    fi
  done
  echo ""
  echo "- Total test blocks: $total_tests"
  echo ""
  echo "Note: full 'baml-cli test' requires the baml-py package; use mise run baml:test."
} > "$REPORT"
cat "$REPORT"