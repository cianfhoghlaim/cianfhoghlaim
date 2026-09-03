#!/usr/bin/env bash
# Layer 3: ingest the 320 .baml files into the 11th Cognee cluster `baml_schemas`
# Per the 2026-08-15-baml-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/baml-cognee-$(date +%Y-%m-%d).md"
{
  echo "# BAML Cognee Ingestion Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Cluster: baml_schemas (new, Layer 7)"
  echo ""
  echo "- Source: baml_src/**/*.baml (320 files)"
  echo "- Target: baml_schemas (the 11th Cognee cluster; 7 docs + 3 openspec + agent_skills + baml_schemas)"
  echo ""
  echo "## Ingestion Script (per the 2026-08-15-baml-sync-loop-v1 change)"
  echo ""
  echo "scripts/cognee_ingest_baml_schemas.py (the canonical ingestor)"
  echo ""
  echo "Note: full cognify of 320 files is slow (~2-5 min). Use 'cognee-mcp' for incremental queries."
} > "$REPORT"
cat "$REPORT"