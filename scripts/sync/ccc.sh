#!/usr/bin/env bash
# Layer 2: refresh CCC index + append the 20th concept guide
# Per the 2026-08-15-knowledge-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/ccc-$(date +%Y-%m-%d).md"
{
  echo "# CCC Index Sync Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## 20th Concept Guide"
  echo '```'
  uv run python scripts/sync_openspec_to_ccc.py
  echo '```'
  echo ""
  echo "## CCC Index Refresh (incremental)"
  echo '```'
  bun run ccc:index 2>&1 | tail -5 || echo "(ccc not available; skipping)"
  echo '```'
} > "$REPORT"
cat "$REPORT"
