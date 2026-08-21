# DEPRECATED — 2026-08-21

> **This directory is deprecated.** It is retained for historic
> reference only.

## Why deprecated

This directory contains a Python MCP server (`server.py` +
`tools.py`) using the pre-v7 `sruth_crypteolas` namespace that was
renamed by the
[`2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1`](../2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/)
change.

The directory was never wired into either `opencode.json` or
`.mcp.json`, so the deprecation has no functional impact on the
agent fleet.

Per user directive (2026-08-21):

> "our sruth are for historic references and should all be
> considered archived already"

## Replacement

There is no production replacement for this module's intended
functionality (cryptography MCP). The canonical encryption / secret
surface is now:

- **Infisical MCP** (post `2026-08-21-flip-observability-mcps-v1`):
  for runtime secret mutation
- **Infisical + Locket + mise** (already wired): for
  `cd`-time secret hydration

See: [`2026-08-21-flip-observability-mcps-v1`](../2026-08-21-flip-observability-mcps-v1/proposal.md)
for the canonical secret-management contract.

## DO NOT

- DO NOT import from this directory in any active code
- DO NOT wire this directory into `opencode.json` or `.mcp.json`
- DO NOT delete the files (per user directive: historic reference only)

## Cross-references

- Deprecating change: [`2026-08-21-archive-legacy-sruth-mcp-servers-v1`](../2026-08-21-archive-legacy-sruth-mcp-servers-v1/proposal.md)
- v7-flatten change: [`2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1`](../2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/)
- Replacement: Infisical MCP (post `2026-08-21-flip-observability-mcps-v1`)