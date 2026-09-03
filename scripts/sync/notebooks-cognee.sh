#!/usr/bin/env bash
# Layer 3: ingest the 119 notebook files into the 15th Cognee cluster
# Per the 2026-08-15-notebooks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/notebooks-cognee-$(date +%Y-%m-%d).md"
{
  echo "# Notebooks Cognee Ingestion Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Cluster: notebooks (new, Layer 11)"
  echo ""
  echo "- Source: notebooks/**/*.py (119 files)"
  echo "- Target: notebooks (the 15th Cognee cluster; 14 existing + notebooks)"
  echo ""
  echo "## Ingestion Script"
  echo "scripts/cognee_ingest_notebooks.py"
} > "$REPORT"
cat "$REPORT"
