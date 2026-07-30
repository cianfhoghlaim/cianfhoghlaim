#!/usr/bin/env bash
# Layer 4: dlt pipeline --dry-run on a sampling of the 13 subdirs
# Per the 2026-08-15-dlt-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/dlt-test-$(date +%Y-%m-%d).md"
{
  echo "# DLT Test Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  for subdir in american_nations api_sources apple_photos british_isles common commonwealth european_nations european_union filesystem jobs language official_media portfolio; do
    if [ -d "dlt_sources/$subdir" ]; then
      sources=$(grep -rln '"'"'@dlt\.source'"'"' "dlt_sources/$subdir" 2>/dev/null | head -3 | wc -l | tr -d '"'"' '"'"')
      printf "| %-22s | %s sample sources |\n" "$subdir" "$sources"
    fi
  done
  echo ""
  echo "- Total subdirs scanned: 13"
} > "$REPORT"
cat "$REPORT"
