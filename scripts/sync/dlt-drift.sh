#!/usr/bin/env bash
# Layer 1: detect source drift across the 928 DLT sources
# Per the 2026-08-15-dlt-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/dlt-drift-$(date +%Y-%m-%d).md"
{
  echo "# DLT Source Drift Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-Jurisdiction Drift Counts"
  echo ""
  total_sources=0
  total_resources=0
  total_dup_sources=0
  total_dup_resources=0
  total_stale_write_disposition=0
  total_stale_destination=0
  for subdir in american_nations api_sources apple_photos british_isles common commonwealth european_nations european_union filesystem jobs language official_media portfolio; do
    if [ -d "dlt_sources/$subdir" ]; then
      sources=$(grep -rln '"'"'@dlt\.source'"'"' "dlt_sources/$subdir" 2>/dev/null | wc -l | tr -d '"'"' '"'"')
      resources=$(grep -rln '"'"'@dlt\.resource'"'"' "dlt_sources/$subdir" 2>/dev/null | wc -l | tr -d '"'"' '"'"')
      duplicates=$(grep -rh '"'"'^@dlt\.source.*name='"'"' "dlt_sources/$subdir" 2>/dev/null | sed '"'"'s/.*name="\([^"]*\)".*/\1/'"'"' | sort | uniq -d | wc -l | tr -d '"'"' '"'"')
      printf "| %-22s | %s sources | %s resources | %s dups |\n" "$subdir" "$sources" "$resources" "$duplicates"
      total_sources=$((total_sources + sources))
      total_resources=$((total_resources + resources))
      total_dup_sources=$((total_dup_sources + duplicates))
    fi
  done
  echo ""
  echo "## Summary"
  echo ""
  echo "- Total sources: $total_sources"
  echo "- Total resources: $total_resources"
} > "$REPORT"
cat "$REPORT"
