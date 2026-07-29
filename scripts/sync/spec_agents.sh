#!/usr/bin/env bash
# Per-spec AGENTS.md generator wrapper used by the unified sync orchestrator.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/all-$(date +%Y-%m-%d).md"
echo "## Layer: sync:spec-agents" >> "$REPORT"
echo '```' >> "$REPORT"
uv run python scripts/sync/spec_agents.py --dry-run >> "$REPORT" 2>&1 || true
echo '```' >> "$REPORT"
echo "" >> "$REPORT"
echo "OK: spec-agents layer scanned"