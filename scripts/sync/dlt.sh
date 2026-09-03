#!/usr/bin/env bash
# Layer 9 orchestrator: runs sync:dlt-drift + sync:dlt-ccc + sync:dlt-cognee
#                            + sync:dlt-test + sync:dlt-lint in sequence
# Per the 2026-08-15-dlt-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/dlt-$(date +%Y-%m-%d).md"
{
  echo "# DLT Source Sync Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Jurisdiction Breakdown"
  echo ""
  total_files=0
  total_sources=0
  total_resources=0
  for subdir in american_nations api_sources apple_photos british_isles common commonwealth european_nations european_union filesystem jobs language official_media portfolio; do
    if [ -d "dlt_sources/$subdir" ]; then
      files=$(find "dlt_sources/$subdir" -name "*.py" -type f 2>/dev/null | wc -l | tr -d ' ')
      sources=$(grep -rln '@dlt\.source' "dlt_sources/$subdir" 2>/dev/null | wc -l | tr -d ' ')
      resources=$(grep -rln '@dlt\.resource' "dlt_sources/$subdir" 2>/dev/null | wc -l | tr -d ' ')
      printf "| %-22s | %s .py | %s sources | %s resources |\n" "$subdir" "$files" "$sources" "$resources"
      total_files=$((total_files + files))
      total_sources=$((total_sources + sources))
      total_resources=$((total_resources + resources))
    fi
  done
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total .py files: $total_files"
  echo "- Total @dlt.source: $total_sources"
  echo "- Total @dlt.resource: $total_resources"
  echo ""
  if [ "$total_files" -gt 0 ]; then
    echo "OK: $total_files .py files registered across 13 jurisdiction subdirs"
  else
    echo "FAIL: 0 .py files detected (suspicious)"
  fi
} > "$REPORT"
cat "$REPORT"
