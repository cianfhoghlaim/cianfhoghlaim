#!/usr/bin/env bash
# Layer 2: append the 23rd CCC concept guide + reindex
# Per the 2026-08-15-stacks-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/stacks-ccc-$(date +%Y-%m-%d).md"
{
  echo "# Stacks CCC Sync Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## 23rd Concept Guide"
  echo '```'
  python3 scripts/sync_openspec_to_ccc.py 2>&1 | head -3 || echo "(no concept guide script)"
  echo '```'
  echo ""
  echo "(the canonical 'stack-catalog-search' guide lives at .cocoindex_code/guides.yml)"
  echo ""
  echo "## CCC Index Refresh (incremental)"
  echo '```'
  bun run ccc:index 2>&1 | tail -3 || echo "(ccc not available; skipping incremental refresh)"
  echo '```'
} > "$REPORT"
cat "$REPORT"