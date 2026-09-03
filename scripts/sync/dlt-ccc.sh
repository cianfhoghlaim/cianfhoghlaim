#!/usr/bin/env bash
# Layer 2: append the 24th CCC concept guide + reindex
# Per the 2026-08-15-dlt-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/dlt-ccc-$(date +%Y-%m-%d).md"
{
  echo "# DLT CCC Sync Report -- $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## 24th Concept Guide"
  echo '"'"'```'"'"'
  python3 scripts/sync_openspec_to_ccc.py 2>&1 | head -3 || echo "(no concept guide script)"
  echo '"'"'```'"'"'
  echo ""
  echo "## CCC Index Refresh (incremental)"
  echo '"'"'```'"'"'
  bun run ccc:index 2>&1 | tail -3 || echo "(ccc not available; skipping incremental refresh)"
  echo '"'"'```'"'"'
} > "$REPORT"
cat "$REPORT"
