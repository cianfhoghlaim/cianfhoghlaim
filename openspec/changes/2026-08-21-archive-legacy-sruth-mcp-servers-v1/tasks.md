# Tasks: 2026-08-21-archive-legacy-sruth-mcp-servers-v1

## Phase A: Add `_DEPRECATED.md` to each of the 3 directories (1st priority)

- [ ] A.1 — Write `sruth/códeolas/mcp_server/_DEPRECATED.md` with the 6 canonical sections (header + reference + v7-flatten + replacement + DO NOT + Cross-references)
- [ ] A.2 — Write `sruth/crypteolas/mcp_server/_DEPRECATED.md` (same template)
- [ ] A.3 — Write `sruth/oideachais/mcp_server/_DEPRECATED.md` (same template)
- [ ] A.4 — Verify all 3 files exist and are valid markdown (run `git diff --stat`)

## Phase B: Validate the change (2nd priority)

- [ ] B.1 — Run `openspec validate 2026-08-21-archive-legacy-sruth-mcp-servers-v1 --strict` and confirm exit 0
- [ ] B.2 — Run `git grep -lE "^from sruth_(códeolas|crypteolas|oideachais)\.mcp_server" agents/ orchestration/ meaisinfhoghlaim/ web/ dlt_sources/ baml_src/ notebooks/` and confirm 0 results (no live imports)
- [ ] B.3 — Run `git grep -nE '"sruth/(códeolas|crypteolas|oideachais)/mcp_server"' opencode.json .mcp.json` and confirm 0 results (no live wiring)

## Validation gate

- [ ] V.1 `openspec validate 2026-08-21-archive-legacy-sruth-mcp-servers-v1 --strict` exits 0
- [ ] V.2 3 `_DEPRECATED.md` files exist
- [ ] V.3 No live imports or wiring references the 3 deprecated directories