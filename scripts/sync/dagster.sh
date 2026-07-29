#!/usr/bin/env bash
# Layer 6: validate Dagster assets via AST parsing + per-group breakdown.
# Per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change + the
# 2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1 change
# (the `knowledge-sync-loop` spec's Layer 6 requirement).
#
# Walks the 5-layer `orchestration/defs/` tree, parses each `.py` file
# with `ast`, counts @asset / @sensor / @schedule / @job / @asset_check
# decorators + the group_name= kwarg on each @asset.
#
# Usage:
#   bash scripts/sync/dagster.sh              # detect + report (exit 1 if broken)
#   bash scripts/sync/dagster.sh --dry-run    # detect + report, exit 0

set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/dagster-$(date +%Y-%m-%d).md"
DRY_RUN="${1:-}"

# Run the AST walker (the Python script) and capture the Markdown report
MARKDOWN_OUTPUT=$(.venv/bin/python3 scripts/sync/ast_walk.py 2>&1)
EXIT_CODE=$?

# Write the report (prepend the UTC timestamp + per the paths.sh convention)
{
  echo "# Dagster Defs Sync Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  # Strip the header line from the Python output (we add our own)
  echo "$MARKDOWN_OUTPUT" | tail -n +2
} > "$REPORT"

cat "$REPORT"

if [ "$DRY_RUN" = "--dry-run" ]; then
    exit 0
fi
exit $EXIT_CODE
