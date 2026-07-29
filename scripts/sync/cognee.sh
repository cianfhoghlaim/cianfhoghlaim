#!/usr/bin/env bash
# Layer 3: ingest openspec + skills docs into Cognee
# Per the 2026-08-15-knowledge-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/cognee-$(date +%Y-%m-%d).md"
{
  echo "# Cognee Ingestion Sync Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Cluster Counts (target: 10)"
  echo ""
  for cluster in docs-cognee docs-platform docs-data-platform docs-agents docs-models docs-web docs-ci openspec_changes openspec_specs agent_skills; do
    echo "- $cluster: pending cognify"
  done
  echo ""
  echo "## Ingestion Scripts (target: 5 runs)"
  echo "1. scripts/cognee_ingest.py docs/01-cognee docs-cognee"
  echo "2. scripts/cognee_ingest.py docs/01-platform-architecture docs-platform"
  echo "3. scripts/cognee_ingest.py docs/02-data-platform docs-data-platform"
  echo "4. scripts/cognee_ingest_openspec.py (openspec_changes + openspec_specs)"
  echo "5. scripts/cognee_ingest_skills.py (agent_skills)"
  echo ""
  echo "Note: full cognify is slow (~5-10min for 7 docs/ dirs). Use 'cognee-mcp' for incremental queries."
} > "$REPORT"
cat "$REPORT"
