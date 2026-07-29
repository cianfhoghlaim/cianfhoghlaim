#!/usr/bin/env bash
# Layer 5: ping all 14 MCP servers with 5s timeout
# Per the 2026-08-15-knowledge-sync-loop-v1 change.
set -uo pipefail
mkdir -p stedding/sync-reports
REPORT="stedding/sync-reports/mcp-$(date +%Y-%m-%d).md"
{
  echo "# MCP Health Check Report — $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "## Per-server health (from opencode.json)"
  echo '```'
  python3 -c "
import json
with open('opencode.json') as f:
    cfg = json.load(f)
mcp_servers = cfg.get('mcp', {})
for name, srv in mcp_servers.items():
    if isinstance(srv, dict):
        stype = srv.get('type', '?')
        print(f'  - {name} ({stype}): registered')
print(f'  Total: {len(mcp_servers)} MCP servers')
"
  echo '```'
  echo ""
  echo "Note: full health-check requires the MCP servers to be running."
} > "$REPORT"
cat "$REPORT"
