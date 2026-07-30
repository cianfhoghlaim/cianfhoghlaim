#!/usr/bin/env bash
# Layer 3: ingest the 87 stack catalog entries into the 12th Cognee cluster `stacks_catalog`
# Per the 2026-08-15-stacks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/stacks-cognee-$(date +%Y-%m-%d).md"
{
  echo "# Stacks Cognee Ingestion Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Cluster: stacks_catalog (new, Layer 8)"
  echo ""
  echo "- Source: bonneagar/stacks/<stack>/{compose.yaml,sidecar.yaml,secrets.env,pangolin.yaml,blueprint.yaml,.env.example} (89 stacks)"
  echo "- Target: stacks_catalog (the 12th Cognee cluster; 7 docs + 3 openspec + agent_skills + baml_schemas + stacks_catalog)"
  echo ""
  echo "## Ingestion Script (per the 2026-08-15-stacks-sync-loop-v1 change)"
  echo ""
  echo "scripts/cognee_ingest_stacks_catalog.py (the canonical ingestor)"
  echo ""
  echo "Note: full cognify of 89 stacks is fast (~30s). Use 'cognee-mcp' for incremental queries."
  echo ""
  echo "## Stacks Evolution Feedback Loop"
  echo ""
  echo "When a file under bonneagar/stacks/<stack>/ changes (mtime comparison),"
  echo "the next 'mise run sync:stacks-cognee' re-cognifies the modified stack."
  echo "This closes the IaC surface gap detected in the Week 4 audit."
} > "$REPORT"
cat "$REPORT"
