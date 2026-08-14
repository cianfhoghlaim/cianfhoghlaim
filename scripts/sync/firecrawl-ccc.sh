#!/usr/bin/env bash
# scripts/sync/firecrawl-ccc.sh
# Layer 2 (firecrawl): append the 27-31st CCC concept guides + reindex
# Per the 2026-08-14-firecrawl-mcp-ccc-dual-search-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/firecrawl-ccc-$(date +%Y-%m-%d).md"
{
  echo "# Firecrawl CCC Sync Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## 27th-31st Concept Guides"
  echo ""
  echo "The 5 new guides appended by this change are:"
  echo ""
  echo "- 27th \`firecrawl-search\`"
  echo "- 28th \`firecrawl-mcp-tools\`"
  echo "- 29th \`firecrawl-research-index\`"
  echo "- 30th \`firecrawl-developer-index\`"
  echo "- 31st \`firecrawl-corpus\`"
  echo ""
  echo "(the canonical guides live at .cocoindex_code/guides.yml)"
  echo ""
  echo "## CCC Index Refresh (incremental)"
  echo '```'
  bun run ccc:index 2>&1 | tail -5 || echo "(ccc not available; skipping incremental refresh)"
  echo '```'
} > "$REPORT"
cat "$REPORT"