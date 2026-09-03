#!/usr/bin/env bash
# Layer 3: ingest the 188 agent files into the 14th Cognee cluster
# Per the 2026-08-15-agent-definitions-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/agents-cognee-$(date +%Y-%m-%d).md"
{
  echo "# Agents Cognee Ingestion Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Cluster: agent_definitions (new, Layer 10)"
  echo ""
  echo "- Source: agents/**/*.py (188 files)"
  echo "- Target: agent_definitions (the 14th Cognee cluster; 13 existing + agent_definitions)"
  echo ""
  echo "## Ingestion Script"
  echo "scripts/cognee_ingest_agent_definitions.py"
} > "$REPORT"
cat "$REPORT"
