#!/usr/bin/env bash
# Layer 3: ingest the 928 DLT sources into the 13th Cognee cluster
# Per the 2026-08-15-dlt-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/dlt-cognee-$(date +%Y-%m-%d).md"
{
  echo "# DLT Cognee Ingestion Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Cluster: dlt_sources (new, Layer 9)"
  echo ""
  echo "- Source: dlt_sources/**/*.py (928 source files)"
  echo "- Target: dlt_sources (the 13th Cognee cluster)"
  echo ""
  echo "## Ingestion Script"
  echo "scripts/cognee_ingest_dlt_sources.py"
} > "$REPORT"
cat "$REPORT"
