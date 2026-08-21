# Change: 2026-08-21-archive-legacy-sruth-mcp-servers-v1

## Why

The 3 in-repo MCP server directories under `sruth/` —
`sruth/códeolas/mcp_server/`, `sruth/crypteolas/mcp_server/`,
`sruth/oideachais/mcp_server/` — are leftover code from the
pre-v7-flatten topology. Per user directive (2026-08-21):

> "our sruth are for historic references and should all be
> considered archived already"

These directories:
1. Were never wired into either `opencode.json` or `.mcp.json`
2. Use the pre-v7 `sruth_*` Python namespace that was renamed to
   `cianfhoghlaim.*` by the
   `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1`
   change
3. Contain dead Python modules (`server.py` + `tools.py`) that
   would block `mise run lint:skills` and `mise run stack-doctor`
   if ever revived
4. Provide no production value — the canonical research surface is
   now `crawl4ai` MCP (per
   `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`)

This change **marks** the 3 directories as historic reference by
adding a `_DEPRECATED.md` header to each. Per the user directive,
no files are deleted — the directories remain for context.

## What Changes

### 1. Add `_DEPRECATED.md` to each of the 3 sruth mcp_server directories

- `sruth/códeolas/mcp_server/_DEPRECATED.md` (NEW)
- `sruth/crypteolas/mcp_server/_DEPRECATED.md` (NEW)
- `sruth/oideachais/mcp_server/_DEPRECATED.md` (NEW)

Each file SHALL:
- Carry a top-line `# DEPRECATED — 2026-08-21` marker
- Reference this openspec change by id
- Reference the v7-flatten change that renamed the namespace
- State the canonical replacement (none — the functionality was
  absorbed into `cognee` MCP for knowledge-graph queries + `crawl4ai`
  MCP for document ingestion)

### 2. NO file deletions

Per the user directive ("sruth are for historic references"), no
files inside the 3 directories SHALL be deleted. The Python modules
remain on disk as historic reference but are NOT discoverable by the
agent runtime.

## Dependencies

- `Blocked by: none`
- `Blocked by (soft): 2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`
  (parallel — both are part of the broader "MCP revival" work)
- `Affected repos: cianfhoghlaim`

## Cross-links

- Companion to: `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`
  (the canonical research-surface change)
- Companion to: `2026-08-21-bring-up-knowledge-and-design-mcps-v1`
  (the replacement knowledge surface)
- Historic context: `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1`
  (the change that removed the `sruth_*` namespace from the active code)

## Requirements

See `tasks.md` for the 2-task plan (A: write the 3 _DEPRECATED.md files,
B: validate the change + verify no regressions).

## Validation gate

- [ ] `openspec validate 2026-08-21-archive-legacy-sruth-mcp-servers-v1 --strict` exits 0
- [ ] `git grep -lE "^from sruth_(códeolas|crypteolas|oideachais)\.mcp_server" agents/ orchestration/ meaisinfhoghlaim/ web/ dlt_sources/ baml_src/ notebooks/` returns 0 results
- [ ] `git grep -nE '"sruth/(códeolas|crypteolas|oideachais)/mcp_server"' opencode.json .mcp.json` returns 0 results (no wiring existed)